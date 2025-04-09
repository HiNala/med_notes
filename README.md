# 📝 Transcript Summarization Tool

A command-line application that transforms audio recordings into structured summary notes using OpenAI's AI models. Originally designed for chiropractic notes, the tool has evolved to handle any type of transcript summarization.

## 🔍 Key Features

1. **Audio Transcription**: Converts your audio recordings to text using OpenAI's Whisper
2. **Flexible Summarization**: Creates structured summaries appropriate for the content type
3. **Template Customization**: Easily modify how the AI formats your summaries
4. **Graceful Fallback**: Uses local Whisper model if API transcription fails
5. **Beautiful Terminal Interface**: Clean, color-coded output with progress indicators

## 📋 Setup Guide

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

# FFmpeg is required for Whisper:
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### Step 4: Add your OpenAI API key
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

Optionally, specify a different model:
```
GPT_MODEL=gpt-4
```

## 🎯 How to Use

### One-Command Operation
Simply run the application and follow the prompts:
```bash
python main.py
```

### Specific Audio File
```bash
python main.py transcribe "your_recording.mp3"
```

### List Available Files
```bash
python main.py transcribe --list
```

### Output Options
```bash
# Only display in terminal (don't save)
python main.py transcribe --no-save

# Only save file (don't display)
python main.py transcribe --no-display
```

## 🛠️ Advanced Customization

### Template System

The application uses a powerful template system stored in `templates/prompt.txt` that controls how your content is summarized.

#### Template Structure
```
---
role: system
content: Your system instructions here
---

Your user message here with {{TRANSCRIPT}} placeholder
```

#### Example Uses

**For Medical Contexts:**
```
---
role: system
content: You are a medical assistant that structures clinical notes into standard SOAP format sections.
---

Please structure the following clinical transcript into SOAP format:

{{TRANSCRIPT}}
```

**For Meeting Summaries:**
```
---
role: system
content: You are an executive assistant who creates structured meeting notes.
---

Create a meeting summary with action items, decisions, and discussion points:

{{TRANSCRIPT}}
```

## 📁 Project Structure

```
med_notes/
│
├── audio_recordings/     # Place audio files here
├── transcriptions/       # Raw transcriptions stored here
├── case_notes/           # Generated summaries stored here
├── templates/            # Prompt templates for AI
│   └── prompt.txt        # Default prompt template
├── .env                  # Environment variables (API keys)
├── main.py               # CLI application
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
└── README.md             # This documentation
```

## 🆘 Troubleshooting

### Installation Issues
- **FFmpeg error**: Make sure FFmpeg is installed and in your PATH
- **OpenAI error**: Verify your API key in the `.env` file
- **Whisper installation**: May require additional system libraries

### Transcription Problems
- **Poor quality**: Ensure your audio is clear with minimal background noise
- **Long files**: May need to increase timeout settings or process in chunks
- **API failures**: The tool automatically falls back to local Whisper processing

### Output Formatting
- **Generic summaries**: Edit the template file to be more specific
- **Too verbose/brief**: Adjust the template to request specific detail level

## 🚀 Advanced Features

### Local Whisper Fallback
If the OpenAI API is unavailable or fails, the application automatically switches to a local Whisper model.

### Customizable AI Models
Set the `GPT_MODEL` variable in `.env` to use different OpenAI models:
```
GPT_MODEL=gpt-4-turbo
```

### Format Preservation
Transcriptions and summaries are saved as Markdown files with proper formatting.

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

# Medical Note Taker

A powerful tool for medical professionals to transcribe audio recordings and generate structured case notes using AI.

## Features

- 🎤 Record or upload audio files
- 🎯 Automatic transcription using OpenAI's Whisper
- 🤖 AI-powered case note generation
- 📝 Markdown output format
- 💻 Modern GUI interface
- 🚀 Standalone executable for easy distribution

## Installation

### Option 1: Using the Executable (Recommended)

1. Download the latest release from the [Releases](https://github.com/yourusername/medical-note-taker/releases) page
2. Extract the zip file
3. Edit the `.env` file to add your OpenAI API key
4. Run `Medical_Note_Taker.exe`

### Option 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/medical-note-taker.git
   cd medical-note-taker
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   python gui.py
   ```

## Building the Executable

To build the executable yourself:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build.py
   ```

The executable will be created in the `dist/Medical_Note_Taker` directory.

## Usage

1. **Record or Upload Audio**:
   - Click "Record New" to record audio directly (coming soon)
   - Click "Upload File" to select an existing audio file

2. **Process Audio**:
   - Select an audio file from the list
   - Click "Process Selected File"
   - Wait for the transcription and case note generation to complete

3. **View Results**:
   - Transcriptions are saved in the `transcriptions` directory
   - Case notes are saved in the `case_notes` directory
   - Both are saved in Markdown format for easy reading and editing

## Directory Structure

```
medical-note-taker/
├── audio_recordings/    # Store your audio files here
├── transcriptions/      # Generated transcriptions
├── case_notes/         # Generated case notes
├── templates/          # Prompt templates
├── gui.py             # GUI application
├── main.py            # CLI application
├── utils.py           # Core functionality
├── build.py           # Build script
└── requirements.txt   # Python dependencies
```

## Requirements

- Python 3.8 or higher
- OpenAI API key
- Windows 10 or higher (for the executable)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for their Whisper and GPT models
- PyQt6 for the GUI framework
- PyInstaller for creating standalone executables 