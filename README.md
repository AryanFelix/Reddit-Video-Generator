# Reddit-Video-Generator

Generate short-form videos from Reddit content and optionally upload them to YouTube. This repo contains Python scripts for fetching/formatting text, generating audio, composing video, and (optionally) uploading to YouTube.

👉 Check out the results of this program on my YouTube channel: [Have You Reddit Yet?](https://www.youtube.com/@HaveYouRedditYet/shorts)

---

## Features

* Fetches Reddit prompts/stories (via API or input file)
* Text-to-speech to generate narration audio
* Video composition with background, captions, and fonts
* Optional YouTube upload via OAuth (creates `token.json` on first auth)

> Note: The exact feature set depends on which modules you enable (e.g., `geminiClient.py`, `youtubeUploader.py`).

---

## Quick Start

### 1) Prerequisites

* **Python**: 3.10–3.11 recommended
* **ffmpeg**: required for audio/video processing (add to PATH)
* A GitHub clone of this repo

### 2) Clone & set up environment

```bash
# clone
git clone https://github.com/AryanFelix/Reddit-Video-Generator.git
cd Reddit-Video-Generator

# create virtual environment (Windows PowerShell example)
python -m venv .venv
. .venv/Scripts/Activate.ps1

# install dependencies
pip install -r requirements.txt
```

### 3) Configure environment variables

Copy `.env.example` to `.env` and fill in the values you use. Not all variables are required—only fill those relevant to your setup.

```bash
# Windows PowerShell
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 4) Run

```bash
python main.py
```

On first YouTube upload, you’ll be prompted to sign into your Google account in a browser. That step generates `token.json` (which is **ignored** by Git).

---

## Project Structure (key files)

```
main.py                    # entry point
videoGenerator.py          # video assembly logic
textToSpeech.py            # TTS utilities
youtubeUploader.py         # YouTube Data API upload helper (optional)
 geminiClient.py           # Google AI Studio (Gemini) helper (optional)
requirements.txt           # Python deps
.gitignore                 # ignores media, secrets, caches, etc.
```

Fonts & assets:

```
bangers.ttf, verdana.ttf   # fonts used for titles/captions
redditQuestionTemplate.png # optional overlay/template asset
```

---

## Environment Variables

Only set what you actually use.

### Reddit API (optional)

* `REDDIT_CLIENT_ID`
* `REDDIT_CLIENT_SECRET`
* `REDDIT_USERNAME`
* `REDDIT_PASSWORD`
* `REDDIT_USER_AGENT`

### Google AI Studio / Gemini (optional)

* `GOOGLE_API_KEY`
  Used by `geminiClient.py` if you generate scripts, summaries, or captions with Gemini.

### YouTube Upload (optional)

You typically use a `client_secret.json` file downloaded from Google Cloud → OAuth credentials. The uploader may read from environment variables or that file, then creates `token.json` after the first auth.

* `YT_CLIENT_ID` *(optional, if your code reads from env)*
* `YT_CLIENT_SECRET` *(optional)*
* `YT_REDIRECT_URI` *(optional)*

### Misc (optional)

* `OPENAI_API_KEY` *(if you switch to OpenAI for any step)*
* `TTS_PROVIDER` *(e.g., "kokoro", "edge", "elevenlabs")*
* `TTS_API_KEY` *(if your TTS provider requires it)*

---

## .gitignore & Large Files

This repo ignores generated media by default (`*.mp4`, `*.wav`, `*.png`, etc.). If you need to version large files, consider **Git LFS**:

```bash
git lfs install
git lfs track "*.mp4" "*.wav"
git add .gitattributes
git commit -m "Configure Git LFS"
```

> Tip: Don’t commit `.env`, `token.json`, or big media outputs. They’re already ignored.

---

## Troubleshooting

**ffmpeg not found** → Install ffmpeg and ensure it's on your PATH.
**ModuleNotFoundError: dotenv** → `pip install python-dotenv` (ensure it exists in `requirements.txt`).
**Git push rejected (large files)** → Remove media from git history and keep it locally; ensure `.gitignore` is applied.

---

## License

This project is licensed under the [MIT License](LICENSE).

![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

# `.env.example`

Copy this file to `.env` and fill in the keys you actually use. Leave the rest blank or remove them.

```dotenv
# ===== Reddit API (optional) =====
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=
REDDIT_USER_AGENT=Reddit-Video-Generator/1.0 by <your-username>

# ===== Google AI Studio / Gemini (optional) =====
GOOGLE_API_KEY=

# ===== YouTube OAuth / Upload (optional) =====
# If your uploader reads these from env instead of a client_secret.json file
YT_CLIENT_ID=
YT_CLIENT_SECRET=
YT_REDIRECT_URI=

# ===== TTS (optional) =====
TTS_PROVIDER=
TTS_API_KEY=

# ===== Misc (optional) =====
OPENAI_API_KEY=
```

---

## Contribution & Issues

PRs welcome. If you encounter issues, please include OS, Python version, and relevant log output.
