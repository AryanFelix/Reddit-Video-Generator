# Reddit-Video-Generator

Generate short-form videos from Reddit content and optionally upload them to YouTube. This repo contains Python scripts for fetching/formatting text, generating audio, composing video, and (optionally) uploading to YouTube.

👉 Check out the results of this program on my YouTube channel: [Have You Reddit Yet?](https://www.youtube.com/@haveyoureddityet)

## ✨ Features

- **Content Generation**: Uses Google Gemini AI to generate Reddit-style questions and stories
- **Voice Synthesis**: Advanced text-to-speech with voice cloning using Chatterbox TTS
- **Video Processing**: Automated video editing with captions, overlays, and background footage
- **YouTube Integration**: Direct upload to YouTube with playlist management
- **Multi-format Support**: Handles various video formats and audio processing
- **Automated Captioning**: Generates synchronized captions using Whisper AI

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10–3.11 recommended
- **ffmpeg**: Required for audio/video processing ([Download & install](https://ffmpeg.org/download.html), ensure it's in your PATH)
- **Git**: For cloning the repository

### 1) Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/AryanFelix/Reddit-Video-Generator.git
cd Reddit-Video-Generator

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2) Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

**Required variables for basic functionality:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_QUESTION_PROMPT=Generate a Reddit question and story for {subreddit} subreddit. Format: ~question~story
```

### 3) Add Required Media Files

Before running, you must provide these files (see [Required Files](#-required-local-files--directory-structure) section below):

- Background videos: `minecraft.mp4`, `gta.mp4`, `surfers.mp4`
- Question template: `redditQuestionTemplate.png`
- Voice sample: `voiceSample2.wav`

### 4) Run the Program

```bash
python main.py
```

On first YouTube upload (if enabled), you'll be prompted to authenticate with Google in your browser.

## 📦 Required Local Files & Directory Structure

### ✅ Core Python Files (Included)
All these files are included when you clone the repository:

| File | Purpose |
|------|---------|
| `main.py` | Entry point - orchestrates the entire pipeline |
| `videoGenerator.py` | Video processing, trimming, captioning, and overlay logic |
| `textToSpeech.py` | Text-to-speech conversion using Chatterbox TTS |
| `youtubeUploader.py` | YouTube upload functionality via OAuth |
| `geminiClient.py` | Google Gemini AI integration for content generation |
| `requirements.txt` | Python dependencies list |

### ⚙️ Configuration Files (Create Yourself)

| File | Required | Purpose |
|------|----------|---------|
| `.env` | ✅ **Required** | **You must create this** by copying `.env.example` and filling in your API keys |
| `client_secret.json` | Optional | Only needed for YouTube uploads - download from Google Cloud Console |

### 🎨 Assets & Media Files (Required for Default Setup)

| File/Folder | Status | Purpose |
|-------------|--------|---------|
| `bangers.ttf` | ✅ Included | Font for video captions |
| `verdana.ttf` | ✅ Included | Font for question text overlays |
| `redditQuestionTemplate.png` | ❌ **MISSING** | Background template for Reddit questions - **you need to create/provide this** |
| Background videos | ❌ **MISSING** | `minecraft.mp4`, `gta.mp4`, `surfers.mp4` - **you need to provide these** |
| Voice sample | ❌ **MISSING** | `voiceSample2.wav` - **you need to provide this** for voice cloning |

### 🤖 Generated Files (Auto-created)
These files are created automatically during execution:

- `token.json` - Generated on first YouTube upload (OAuth credentials)
- `output.mp3` - Generated audio file
- `finalOutput.mp4` - Final processed video
- `lastExecuted.txt` - Execution log
- Various temporary files (automatically cleaned up)

### 📁 Complete Directory Structure

After setup, your directory should look like this:

```
Reddit-Video-Generator/
│
├── 🐍 Python Scripts (Included)
│   ├── main.py
│   ├── videoGenerator.py
│   ├── textToSpeech.py
│   ├── youtubeUploader.py
│   └── geminiClient.py
│
├── ⚙️ Configuration (You Create)
│   ├── .env                           # ← CREATE THIS from .env.example
│   ├── .env.example                   # ← Template provided
│   └── client_secret.json             # ← Optional: from Google Cloud
│
├── 🎨 Assets (Mix of Included/Missing)
│   ├── bangers.ttf                    # ✅ Included
│   ├── verdana.ttf                    # ✅ Included
│   ├── redditQuestionTemplate.png     # ❌ YOU NEED THIS
│   ├── minecraft.mp4                  # ❌ YOU NEED THIS
│   ├── gta.mp4                        # ❌ YOU NEED THIS
│   ├── surfers.mp4                    # ❌ YOU NEED THIS
│   └── voiceSample2.wav               # ❌ YOU NEED THIS
│
├── 📄 Project Files
│   ├── requirements.txt               # ✅ Included
│   ├── .gitignore                     # ✅ Included
│   ├── LICENSE                        # ✅ Included
│   └── README.md                      # ✅ Included
│
└── 🤖 Generated (Auto-created)
    ├── token.json                     # OAuth credentials
    ├── output.mp3                     # Generated audio
    ├── finalOutput.mp4                # Final video
    └── lastExecuted.txt               # Execution log
```

### ⚠️ Critical Missing Files

**Before running the program, you MUST provide these files:**

1. **Background Videos**: Place these video files in the root directory:
   - `minecraft.mp4` - Minecraft gameplay footage
   - `gta.mp4` - GTA gameplay footage  
   - `surfers.mp4` - Subway Surfers gameplay footage

2. **Reddit Question Template**: Create or obtain `redditQuestionTemplate.png` - this is used as an overlay for displaying Reddit questions

3. **Voice Sample**: Provide `voiceSample2.wav` - a reference audio file for voice cloning (mono, 16/24/48 kHz recommended)

4. **Environment Variables**: Create `.env` file with your API keys (see Environment Variables section below)

## 🔧 Environment Variables

Create a `.env` file by copying `.env.example` and fill in the values you need. Not all variables are required—only fill those relevant to your setup.

### Google Gemini AI (Required)
```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_QUESTION_PROMPT=your_custom_prompt_template
```
Get your API key from [Google AI Studio](https://aistudio.google.com/).

### YouTube Upload (Optional)
For uploading videos directly to YouTube:

```bash
CLIENT_ID=your_youtube_oauth_client_id
CLIENT_SECRET=your_youtube_oauth_client_secret
REDIRECT_URI=urn:ietf:wg:oauth:2.0:oob
```

You need to:
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Download `client_secret.json` (optional alternative to env vars)

### Reddit API (Optional)
If you want to fetch real Reddit content:

```bash
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=Reddit-Video-Generator/1.0 by your-username
```

### Text-to-Speech (Optional)
For alternative TTS providers:

```bash
TTS_PROVIDER=kokoro  # or "edge", "elevenlabs"
TTS_API_KEY=your_tts_api_key
```

### Other Services (Optional)
```bash
OPENAI_API_KEY=your_openai_key  # If switching to OpenAI for any step
```

## 🎯 How It Works

1. **Content Generation**: Uses Gemini AI to create Reddit-style questions and stories based on popular subreddit themes
2. **Voice Synthesis**: Converts the generated story to speech using voice cloning technology
3. **Video Processing**: 
   - Selects random background footage
   - Trims video to match audio duration
   - Generates captions using Whisper AI
   - Overlays question template and captions
4. **YouTube Upload**: Automatically uploads the final video with proper tags, descriptions, and playlist assignment

## 🎨 Customization

### Supported Subreddit Types
The program generates content for these categories:
- Unsolved Mysteries
- True Crime
- Scary Stories
- Reddit Stories
- Karma Stories
- TIFU (Today I F*cked Up)
- AITA (Am I The A*shole)

### Video Customization
- **Background Videos**: Replace `minecraft.mp4`, `gta.mp4`, `surfers.mp4` with your own footage
- **Question Template**: Customize `redditQuestionTemplate.png` for your brand
- **Fonts**: Modify font files or paths in `videoGenerator.py`
- **Voice**: Replace `voiceSample2.wav` with your own voice sample

## 📋 Dependencies

The program uses these key libraries:
- `torch` & `torchaudio` - PyTorch for AI models
- `chatterbox` - Voice cloning TTS
- `whisper` - Audio transcription for captions
- `ffmpeg-python` - Video/audio processing
- `google-api-python-client` - YouTube API integration
- `google-generativeai` - Gemini AI integration

See `requirements.txt` for complete list.

## 🗂️ File Management & .gitignore

This repository automatically ignores:
- Generated media files (`*.mp4`, `*.wav`, `*.mp3`, etc.)
- Credentials (`.env`, `token.json`)
- Python cache files
- Large datasets and temporary files

**Important**: Don't commit sensitive files like `.env`, `token.json`, or large media files.

For versioning large files, consider using **Git LFS**:
```bash
git lfs install
git lfs track "*.mp4" "*.wav"
git add .gitattributes
git commit -m "Configure Git LFS"
```

## 🛠️ Troubleshooting

### Common Issues

**`ffmpeg not found`**
- Install ffmpeg and ensure it's in your system PATH
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**`ModuleNotFoundError: chatterbox`**
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.10-3.11

**`File not found: redditQuestionTemplate.png`**
- Create or provide this image file in the root directory
- This is used as the background for question overlays

**`No such file: minecraft.mp4`**
- Add the required background video files to the root directory
- You need to source these videos yourself (copyright considerations)

**`GEMINI_API_KEY not set`**
- Create `.env` file from `.env.example`
- Get API key from [Google AI Studio](https://aistudio.google.com/)

**YouTube upload fails**
- Set up OAuth credentials in Google Cloud Console
- Enable YouTube Data API v3
- Ensure `CLIENT_ID` and `CLIENT_SECRET` are correct

### Performance Tips
- Use GPU if available (CUDA) for faster TTS processing
- Background videos should be high quality but reasonably sized
- Voice samples work best when they're clear, mono, and 16-48kHz

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

When reporting issues, please include:
- Operating system and Python version
- Complete error messages
- Steps to reproduce the problem

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

- **Content**: This tool generates content for educational and entertainment purposes
- **Copyright**: Ensure you have rights to any background videos, images, or audio you use
- **Platform Terms**: Comply with YouTube's Terms of Service and Community Guidelines
- **AI Usage**: Be mindful of AI-generated content policies on platforms where you share

## 🔗 Links

- **YouTube Channel**: [Have You Reddit Yet?](https://www.youtube.com/@haveyoureddityet)
- **Issues**: [GitHub Issues](https://github.com/AryanFelix/Reddit-Video-Generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AryanFelix/Reddit-Video-Generator/discussions)

---

**Happy content creating! 🎬**