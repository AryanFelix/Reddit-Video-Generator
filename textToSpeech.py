import os
import numpy
import subprocess

from kokoro import KPipeline
import soundfile as sf

class TextToSpeech:
    def __init__(self):
        self.pipeline = KPipeline(lang_code='a')
        

    def synthesize(self, text, output_file, speed):
        tempWAV = "tempOutput.wav"
        tempFastWAV = "tempFast.wav"

        self.generator = self.pipeline(text, voice='af_jessica')
        audioChunks = []
        
        for i, (gs, ps, audio) in enumerate(self.generator):
            print(i, gs, ps)
            audioChunks.append(audio)
        
        finalAudio = numpy.concatenate(audioChunks)
        sf.write(tempWAV, finalAudio, 24000)
        print(f"Synthesized speech saved to {tempWAV}")

        subprocess.run([
            "ffmpeg", "-y", "-i", tempWAV,
            "-filter:a", f"atempo={speed}",
            tempFastWAV
        ], check=True)

        subprocess.run([
            "ffmpeg", "-y", "-i", tempFastWAV, output_file
        ], check=True)

        os.remove(tempWAV)
        os.remove(tempFastWAV)

        print(f"Final Audio File Saved as {output_file}")
