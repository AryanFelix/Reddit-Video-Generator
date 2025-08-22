import ffmpeg
import random
import subprocess
import os
import whisper

class VideoProcessor:
    def __init__(self, video_file: str, audio_file: str, output_file: str = "processed_video.mp4", question: str = ""):
        self.video_file = video_file
        self.audio_file = audio_file
        self.output_file = output_file
        self.video_duration = self._get_duration(video_file)
        self.audio_duration = self._get_duration(audio_file)
        self.question = question
        self.trimmed_video = "trimmed_temp.mp4"  
        self.srt_file = "captions.srt" 
        self.whisper_model = whisper.load_model("base")

    def _get_duration(self, filename: str) -> float:
        """Return media duration in seconds using ffprobe."""
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", filename
            ],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        return float(result.stdout)

    def trim(self, random_start: bool = True, start_time: float = 0.0):
        """Trim the video to match audio duration."""
        if self.audio_duration > self.video_duration:
            raise ValueError("Audio file is longer than video!")

        if random_start:
            max_start = self.video_duration - self.audio_duration
            start_time = random.uniform(0, max_start)

        end_time = start_time + self.audio_duration
        print(f"Trimming video from {start_time:.2f}s to {end_time:.2f}s")

        (
            ffmpeg
            .input(self.video_file, ss=start_time, t=self.audio_duration)
            .output(self.trimmed_video, c="copy")
            .run(overwrite_output=True)
        )
        print(f"Trimmed video saved as {self.trimmed_video}")

    def attach_audio(self):
        """Attach the audio file to the captioned video."""
        temp_output = "temp_output_with_audio.mp4" 
        print(f"Attaching audio {self.audio_file} to video {self.output_file}")
        video = ffmpeg.input(self.output_file) 
        audio = ffmpeg.input(self.audio_file)

        ffmpeg.output(
            video['v'], audio['a'],
            temp_output,
            vcodec="copy",
            acodec="aac",
            strict="-2"
        ).run(overwrite_output=True)

        if os.path.exists(temp_output):
            os.replace(temp_output, self.output_file)
            print(f"Final video with audio saved as {self.output_file}")
        else:
            raise FileNotFoundError(f"Temporary output file {temp_output} not created")

    def _format_time_srt(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def generate_srt_captions(self):
        """Generate an SRT file from the audio clip with a maximum of 3 words per caption."""
        print(f"Transcribing audio {self.audio_file} using Whisper (base)...")
        result = self.whisper_model.transcribe(self.audio_file, word_timestamps=True)
        segments = result.get("segments", [])

        with open(self.srt_file, 'w', encoding='utf-8') as f:
            caption_index = 1
            for seg in segments:
                words = seg.get("words", [])
                if not words:
                    continue

                max_words_per_caption = 3
                chunks = [words[i:i + max_words_per_caption] for i in range(0, len(words), max_words_per_caption)]

                for chunk in chunks:
                    start_time = chunk[0]['start']
                    end_time = chunk[-1]['end']
                    text = " ".join(word['word'].strip() for word in chunk)

                    start_str = self._format_time_srt(start_time)
                    end_str = self._format_time_srt(end_time)

                    f.write(f"{caption_index}\n")
                    f.write(f"{start_str} --> {end_str}\n")
                    f.write(f"{text}\n\n")
                    print(f"Added SRT caption {caption_index}: {text} ({start_str} to {end_str})")
                    caption_index += 1

        print(f"SRT captions saved to {self.srt_file}")

    def add_text_overlays(self):
        """Add text overlays and image with question to the video using ffmpeg drawtext and overlay filters."""
        if not os.path.exists(self.srt_file):
            raise FileNotFoundError(f"SRT file not found: {self.srt_file}. Generate captions first.")

        temp_output = "text_overlay_temp.mp4"
        print(f"Adding text overlays and image with question from {self.srt_file} to {self.trimmed_video}")

        video_duration = self._get_duration(self.trimmed_video)

        video_stream = ffmpeg.input(self.trimmed_video)['v']
        image_stream = ffmpeg.input('redditQuestionTemplate.png')['v']

        # Split question into lines with max 15 characters
        if self.question:
            words = self.question.split()
            lines = []
            current_line = ""
            for word in words:
                # Add word with a space if it's not the first word
                test_line = f"{current_line} {word}" if current_line else word
                if len(test_line) <= 15:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            question_text = '\n'.join(lines)
        else:
            question_text = ""

        if self.question:
            image_with_text = ffmpeg.filter(
                [image_stream],
                'drawtext',
                text=question_text,
                fontsize=60,
                x='(w-text_w)/2',
                y='(h-text_h)/2',
                enable=f'between(t,0,{video_duration})',
                fontcolor='black@1.0',
                borderw=2,
                bordercolor='white@1.0',
                fontfile=r'verdana.ttf',
                text_align='center'
            )
            print(f"Applied question text '{question_text}' to image")
        else:
            image_with_text = image_stream

        overlaid_stream = ffmpeg.filter(
            [video_stream, image_with_text],
            'overlay',
            x=0,
            y=0,
            enable=f'between(t,0,{video_duration})'
        )
        print(f"Applied image overlay with question at top for {video_duration} seconds")

        with open(self.srt_file, 'r', encoding='utf-8') as f:
            srt_content = f.read().split('\n\n')

        current_stream = overlaid_stream

        for i, block in enumerate(srt_content, 1):
            if not block.strip():
                continue
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            index, times, text = lines[0], lines[1], lines[2]

            try:
                start_time, end_time = times.split(' --> ')
                start_hours, start_mins, start_secs = map(float, start_time.replace(',', '.').split(':'))
                end_hours, end_mins, end_secs = map(float, end_time.replace(',', '.').split(':'))
                start_seconds = start_hours * 3600 + start_mins * 60 + start_secs
                end_seconds = end_hours * 3600 + end_mins * 60 + end_secs
            except ValueError as e:
                print(f"Error parsing timestamps for caption {i}: {e}")
                continue

            current_stream = ffmpeg.filter(
                [current_stream],
                'drawtext',
                text=text,
                fontsize=100,
                x='(w-text_w)/2',
                y='20+((h-text_h)/2)',
                enable=f'between(t,{start_seconds},{end_seconds})',
                fontcolor='white@1.0',
                borderw=4,
                bordercolor='black@1.0',
                fontfile=r'bangers.ttf'
            )
            print(f"Filter for caption {i}: drawtext with text='{text}', start={start_seconds}, end={end_seconds}")

        try:
            (
                current_stream
                .output(temp_output, vcodec="libx264")
                .run(overwrite_output=True)
            )
        except ffmpeg.Error as e:
            print(f"ffmpeg error: {e.stderr.decode() if e.stderr else 'No stderr available'}")
            raise

        os.replace(temp_output, self.output_file)
        print(f"Captioned video with image and question saved as {self.output_file}")

    def process_video(self, random_start: bool = True):
        """Full workflow: trim, generate captions, add text overlays, then attach audio."""
        self.trim(random_start=random_start)
        self.generate_srt_captions()
        self.add_text_overlays()
        self.attach_audio()
        self.cleanup()

    def cleanup(self):
        """Remove temporary files except for the final output."""
        temp_files = [self.trimmed_video, self.srt_file, "text_overlay_temp.mp4", "temp_output_with_audio.mp4"]
        for file in temp_files:
            if os.path.exists(file) and file != self.output_file:
                os.remove(file)
                print(f"Removed temporary file: {file}")

