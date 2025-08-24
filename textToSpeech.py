import os
import re
import subprocess
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

class TextToSpeech:
    def __init__(
        self,
        device: str | None = None,
        voice_sample: str | None = None,   # path to your reference WAV (mono, 16/24/48 kHz)
        exaggeration: float = 0.5,         # emotion/intensity control
        cfg_weight: float = 0.5            # pacing/expressiveness control
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ChatterboxTTS.from_pretrained(device=self.device)
        self.voice_sample = voice_sample
        self.exaggeration = float(exaggeration)
        self.cfg_weight = float(cfg_weight)

    def _split_text(self, text: str, max_len: int = 500):
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks, buf = [], ""
        for p in parts:
            if not p:
                continue
            if len(buf) + len(p) + 1 <= max_len:
                buf = (buf + " " + p).strip() if buf else p
            else:
                if buf:
                    chunks.append(buf)
                buf = p
        if buf:
            chunks.append(buf)
        return chunks

    def synthesize(
        self,
        text: str,
        output_file: str,
        speed: float = 1.0,
        voice_sample: str | None = None,
        max_len: int = 700,           # target max chars per chunk
        trim_db: float = -45.0,       # silence threshold (dBFS) per chunk
        trim_margin_ms: float = 30.0  # protect phoneme onsets/ends
    ):
        """
        Auto-chunk → per-chunk silence trim → concat → pitch-preserving speed → MP3.
        Produces a single continuous file with minimal gaps.
        """
        import re
        import subprocess
        import os
        import torch
        import torchaudio as ta

        if getattr(self, "random_seed", None) is not None:
            torch.manual_seed(int(self.random_seed))

        # --- helpers (local) ---
        def split_text(t: str, limit: int):
            t = re.sub(r"\s+", " ", t.strip())
            # split on end punctuation but keep it
            parts = re.split(r"(?<=[\.\!\?\:\;])\s+", t)
            chunks, buf = [], ""
            for p in parts:
                if not p:
                    continue
                if len(buf) + len(p) + 1 <= limit:
                    buf = (buf + " " + p).strip() if buf else p
                else:
                    if buf:
                        chunks.append(buf)
                    buf = p
            if buf:
                chunks.append(buf)
            return chunks if chunks else [t]

        def trim_silence(wav_1d: torch.Tensor, sr: int, db_thresh: float, margin_ms: float):
            if wav_1d.numel() == 0:
                return wav_1d
            amp_thresh = 10 ** (db_thresh / 20.0)
            x = wav_1d.abs()
            idx = torch.where(x >= amp_thresh)[0]
            if idx.numel() == 0:
                return wav_1d  # all near-silence; keep as-is
            pad = int(sr * (margin_ms / 1000.0))
            start = max(int(idx[0]) - pad, 0)
            end = min(int(idx[-1]) + pad, wav_1d.numel() - 1)
            return wav_1d[start:end + 1]

        # --- chunk, synthesize, trim, concat ---
        chunks = split_text(text, max_len)
        sr = self.model.sr
        pieces = []

        with torch.no_grad():
            for chunk in chunks:
                wav = self.model.generate(
                    chunk,
                    audio_prompt_path=voice_sample or self.voice_sample,
                    exaggeration=self.exaggeration,
                    cfg_weight=self.cfg_weight,
                )
                # normalize to 1-D mono tensor [T]
                if isinstance(wav, torch.Tensor):
                    if wav.dim() == 2:
                        if wav.size(0) > 1:  # downmix stereo if any
                            wav = wav.mean(dim=0, keepdim=True)
                        wav = wav.squeeze(0)
                else:
                    wav = torch.tensor(wav)

                wav = trim_silence(wav, sr, trim_db, trim_margin_ms)
                pieces.append(wav)

        if not pieces:
            raise RuntimeError("No audio generated.")

        full = torch.cat(pieces)
        temp_wav = "tempOutput.wav"
        temp_fast_wav = "tempFast.wav"

        ta.save(temp_wav, full.unsqueeze(0), sr)
        print(f"Synthesized speech saved to {temp_wav} (single continuous file)")

        # --- pitch-preserving speed change + MP3 transcode ---
        if abs(speed - 1.0) > 1e-3:
            # chain atempo if speed outside 0.5–2.0
            s = float(speed)
            filters = []
            while s > 2.0:
                filters.append("atempo=2.0"); s /= 2.0
            while s < 0.5:
                filters.append("atempo=0.5"); s /= 0.5
            filters.append(f"atempo={s:.6f}")
            chain = ",".join(filters)

            subprocess.run(
                ["ffmpeg", "-y", "-i", temp_wav, "-filter:a", chain, temp_fast_wav],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            subprocess.run(
                ["ffmpeg", "-y", "-i", temp_fast_wav, output_file],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            os.remove(temp_fast_wav)
        else:
            subprocess.run(
                ["ffmpeg", "-y", "-i", temp_wav, output_file],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )

        os.remove(temp_wav)
        print(f"Final Audio File Saved as {output_file}")