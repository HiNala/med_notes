# 📝 Chiropractic Case Notes Generator

A simple CLI tool that transforms recordings of chiropractic sessions into structured clinical case notes using OpenAI's AI models.

## 🔍 What it does

1. Takes your audio recording of a chiropractic session
2. Transcribes it using OpenAI's Whisper AI
3. Organizes the content into properly structured clinical notes
4. Shows the notes in your terminal and saves them as a markdown file

## 📋 Simple Setup Guide

### Step 1: Clone this repository
```bash
git clone https://github.com/HiNala/med_notes.git
cd med_notes
```

### Step 2: Set up Python environment
```bash
# Create a virtual environment
python -m venv venv

# Activate it on Windows
venv\Scripts\activate

# OR activate it on macOS/Linux
# source venv/bin/activate
```

### Step 3: Install dependencies
```bash
# Make sure pip is up to date
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# If you have issues with whisper installation, you might need to install FFmpeg:
# Windows: Download from https://www.ffmpeg.org/download.html or install with Chocolatey
# choco install ffmpeg
# 
# macOS: brew install ffmpeg
# 
# Linux: sudo apt install ffmpeg
```

### Step 4: Add your OpenAI API key
Either:
- Create a `.env` file with: `OPENAI_API_KEY=your_api_key_here`
- Or set it as an environment variable

## 🎯 How to Use

### Step 1: Add your audio recording
Place your audio file in the `audio_recordings` folder.

Supported formats:
- MP3 (.mp3)
- WAV (.wav)
- AAC/M4A (.m4a, .aac)
- OGG Vorbis (.ogg)
- FLAC (.flac)
- Windows Media Audio (.wma)
- AIFF (.aiff)
- Apple Lossless (.alac)
- Opus (.opus)
- WebM Audio (.webm)

### Step 2: Run the program
```bash
python main.py transcribe
```

### Step 3: Select your audio file
If you have multiple files, you'll be prompted to select one from the list.

### Step 4: View and save your notes
- The structured notes will display in your terminal
- They'll be automatically saved to the `case_notes` folder

## 📋 Available Commands

### List available audio files
```bash
python main.py transcribe --list
```

### Process a specific file
```bash
python main.py transcribe "your_recording.mp3"
```

### Don't save the notes (just view them)
```bash
python main.py transcribe --no-save
```

### Don't display the notes (just save them)
```bash
python main.py transcribe --no-display
```

## 🔧 Customizing the Prompt

You can edit the `templates/prompt.txt` file to customize how your notes are structured.

## 🆘 Troubleshooting

- **No audio files found?** Make sure your files are in the `audio_recordings` directory.
- **API key error?** Check that your OpenAI API key is correct in the `.env` file.
- **Transcription errors?** Ensure your audio is clear and in a supported format.
- **Installation issues?** 
  - Make sure you have Python 3.8+ installed
  - Try installing packages individually if there are conflicts
  - FFmpeg is required for whisper - make sure it's installed and in your PATH
  - If you encounter CUDA/GPU errors, try using CPU for transcription
- **Permission errors?** Try running your terminal as administrator or use `sudo` on Unix systems

## 📄 License

This project is licensed under the MIT License.

## 📁 Project Structure

```
med_notes/
│
├── audio_recordings/         # Place audio files here
├── transcriptions/           # Raw transcriptions are saved here
├── case_notes/               # Generated case notes are saved here
├── templates/                # Prompt templates for the LLM
│   └── prompt.txt            # Default prompt template
├── .env                      # Environment variables (API keys)
├── main.py                   # Main CLI application
├── utils.py                  # Helper functions
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation
```

## 🔄 Workflow

1. Place an audio recording in the `audio_recordings` directory
2. Run the transcribe command
3. The audio is transcribed using OpenAI's Whisper model (API or local)
4. The transcription is processed by an LLM using the prompt template
5. Structured case notes are displayed and saved

## 🛠️ Customizing the Prompt

You can modify the prompt template used for generating case notes by editing the `templates/prompt.txt` file. The template uses the placeholder `{{TRANSCRIPT}}` which will be replaced with the actual transcription text.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page. 