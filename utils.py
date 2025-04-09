import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import sys
import shutil

import openai
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from tqdm import tqdm

# Get the base directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Path constants
TRANSCRIPTIONS_DIR = BASE_DIR / "transcriptions"
CASE_NOTES_DIR = BASE_DIR / "case_notes"
AUDIO_DIR = BASE_DIR / "audio_recordings"
TEMPLATES_DIR = BASE_DIR / "templates"

# Maximum file size for audio files (100MB)
MAX_AUDIO_SIZE = 100 * 1024 * 1024

def setup_logging():
    """Configure logging for the application."""
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(BASE_DIR / "med_note.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"Error setting up logging: {e}")
        raise

logger = setup_logging()
console = Console()

# Load environment variables
try:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    raise

def validate_audio_file(file_path: Path) -> None:
    """Validate an audio file for size and format."""
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Not a valid file: {file_path}")
    
    file_size = file_path.stat().st_size
    if file_size > MAX_AUDIO_SIZE:
        raise ValueError(f"Audio file too large: {file_size / (1024*1024):.2f}MB > {MAX_AUDIO_SIZE / (1024*1024):.2f}MB")
    
    valid_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma', '.aiff', '.alac', '.opus', '.webm']
    if file_path.suffix.lower() not in valid_extensions:
        raise ValueError(f"Invalid audio format. Supported formats: {', '.join(valid_extensions)}")

def ensure_directories_exist():
    """Create required directories if they don't exist."""
    try:
        dirs_to_create = [AUDIO_DIR, TRANSCRIPTIONS_DIR, CASE_NOTES_DIR, TEMPLATES_DIR]
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        raise


def list_audio_files() -> List[Path]:
    """List all audio files in the audio_recordings directory."""
    try:
        audio_files = []
        
        # Include all major audio formats
        audio_formats = [
            "*.mp3",    # MP3
            "*.wav",    # WAV
            "*.m4a",    # AAC/M4A
            "*.ogg",    # OGG Vorbis
            "*.flac",   # FLAC
            "*.aac",    # AAC
            "*.wma",    # Windows Media Audio
            "*.aiff",   # AIFF
            "*.alac",   # Apple Lossless
            "*.opus",   # Opus
            "*.webm",   # WebM Audio
        ]
        
        for ext in audio_formats:
            try:
                audio_files.extend(AUDIO_DIR.glob(ext))
            except Exception as e:
                logger.warning(f"Error searching for {ext} files: {e}")
        
        return sorted(audio_files)
    except Exception as e:
        logger.error(f"Error listing audio files: {e}")
        raise


def transcribe_audio(audio_file: Path) -> str:
    """Transcribe an audio file using OpenAI's Whisper API."""
    try:
        logger.info(f"Transcribing audio file: {audio_file}")
        
        # Validate the audio file
        validate_audio_file(audio_file)
        
        # Transcribe the audio file
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        
        # Save raw transcription
        raw_path = TRANSCRIPTIONS_DIR / f"{audio_file.stem}_raw.txt"
        try:
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            logger.info(f"Saved raw transcription to: {raw_path}")
        except Exception as e:
            logger.error(f"Error saving raw transcription: {e}")
            raise
        
        # Create formatted HTML version
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #2c3e50;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 30px;
                    margin: 20px 0;
                }}
                .header {{
                    background-color: #e3f2fd;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    border-left: 4px solid #2196f3;
                }}
                .transcript {{
                    white-space: pre-wrap;
                    background-color: #fff;
                    padding: 25px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 16px;
                    line-height: 1.8;
                }}
                .metadata {{
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
                h1 {{
                    color: #1976d2;
                    margin: 0 0 10px 0;
                    font-size: 24px;
                }}
                .subtitle {{
                    color: #666;
                    font-size: 16px;
                    margin: 0;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 2px 5px;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Medical Transcription</h1>
                    <p class="subtitle">Professional Audio Transcription</p>
                </div>
                <div class="transcript">
                    {transcript.replace('\n', '<br>')}
                </div>
                <div class="metadata">
                    <p><strong>File:</strong> {audio_file.name}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Generated by:</strong> OpenAI Whisper API</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML version
        html_path = TRANSCRIPTIONS_DIR / f"{audio_file.stem}_formatted.html"
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Saved formatted transcription to: {html_path}")
        except Exception as e:
            logger.error(f"Error saving HTML transcription: {e}")
            raise
        
        return transcript
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise


def load_template() -> Dict[str, str]:
    """
    Load the prompt template from file.
    
    Returns:
        Dictionary containing system message and user prompt template
    """
    template_path = TEMPLATES_DIR / "prompt.txt"
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
            
        # Check if the template has a system message section
        if template_content.startswith("---"):
            # Parse the YAML-like front matter for the system message
            parts = template_content.split("---", 2)
            if len(parts) >= 3:
                # Extract system message from the front matter
                system_content = ""
                for line in parts[1].strip().split("\n"):
                    if line.startswith("content:"):
                        system_content = line.replace("content:", "", 1).strip()
                    elif line.startswith("role:") and "system" not in line:
                        logger.warning("Template contains non-system role, ignoring")
                
                # Rest is the user prompt
                user_template = parts[2].strip()
                
                return {
                    "system_content": system_content,
                    "user_template": user_template
                }
        
        # If no system message found, return just the user template
        return {
            "system_content": "You are a helpful assistant that creates clear summaries of transcripts.",
            "user_template": template_content
        }
            
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        console.print(f"[bold red]Template file not found:[/bold red] {template_path}")
        raise


def generate_case_notes(transcript: str) -> tuple[str, str]:
    """Generate medical case notes from a transcript using OpenAI's API."""
    try:
        logger.info("Generating medical case notes from transcript")
        
        # Load the template
        template = load_template()
        
        # Prepare the messages for the API call
        messages = [
            {"role": "system", "content": template["system_content"]},
            {"role": "user", "content": f"Please analyze the following transcript and generate structured medical notes:\n\n{transcript}"}
        ]
        
        # Get the model from environment variables
        model = os.getenv("GPT_MODEL", "gpt-3.5-turbo")
        
        # Generate the case notes
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        notes = response.choices[0].message.content
        
        # Create formatted HTML version
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #2c3e50;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 30px;
                    margin: 20px 0;
                }}
                .header {{
                    background-color: #e8f5e9;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    border-left: 4px solid #4caf50;
                }}
                .notes {{
                    background-color: #fff;
                    padding: 25px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 16px;
                    line-height: 1.8;
                }}
                .metadata {{
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
                h1 {{
                    color: #2e7d32;
                    margin: 0 0 10px 0;
                    font-size: 24px;
                }}
                .subtitle {{
                    color: #666;
                    font-size: 16px;
                    margin: 0;
                }}
                .section {{
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #f5f5f5;
                    border-radius: 6px;
                }}
                .section-title {{
                    color: #1976d2;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 2px 5px;
                    border-radius: 3px;
                }}
                .important {{
                    color: #d32f2f;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Medical Case Notes</h1>
                    <p class="subtitle">AI-Generated Clinical Summary</p>
                </div>
                <div class="notes">
                    {notes.replace('\n', '<br>')}
                </div>
                <div class="metadata">
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Model:</strong> {model}</p>
                    <p><strong>Generated by:</strong> OpenAI API</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return notes, html_content
        
    except Exception as e:
        logger.error(f"Error generating case notes: {str(e)}")
        raise


def save_case_notes(audio_stem: str, notes: str, html_content: str) -> Path:
    """Save case notes to a file with proper formatting."""
    try:
        logger.info(f"Saving case notes for: {audio_stem}")
        
        # Ensure the directory exists
        os.makedirs(CASE_NOTES_DIR, exist_ok=True)
        
        # Save raw notes
        raw_path = CASE_NOTES_DIR / f"{audio_stem}_notes_raw.txt"
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(notes)
        
        # Save HTML version
        html_path = CASE_NOTES_DIR / f"{audio_stem}_notes_formatted.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Save Markdown version
        md_path = CASE_NOTES_DIR / f"{audio_stem}_notes.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Medical Case Notes\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {os.getenv('GPT_MODEL', 'gpt-3.5-turbo')}\n\n")
            f.write(notes)
        
        logger.info(f"Case notes saved to: {raw_path}, {html_path}, {md_path}")
        return html_path
        
    except Exception as e:
        logger.error(f"Error saving case notes: {str(e)}")
        raise


def display_markdown(content: str):
    """Display markdown content in the console."""
    md = Markdown(content)
    console.print(md) 