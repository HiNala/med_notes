import os
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import tempfile

import openai
import whisper
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("med_note.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
console = Console()

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ensure_directories_exist():
    """Ensure all required directories exist."""
    directories = ["audio_recordings", "transcriptions", "case_notes", "templates"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


def list_audio_files() -> List[Path]:
    """List all audio files in the audio_recordings directory."""
    audio_dir = Path("audio_recordings")
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
        audio_files.extend(audio_dir.glob(ext))
    
    return sorted(audio_files)


def transcribe_audio(audio_path: Path) -> str:
    """
    Transcribe audio file using OpenAI's Whisper API or local model.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Transcribed text
    """
    logger.info(f"Transcribing audio: {audio_path}")
    console.print(f"[bold blue]Transcribing[/bold blue] {audio_path.name}...")
    
    try:
        # First try using OpenAI's API
        try:
            with open(audio_path, "rb") as audio_file:
                with tqdm(total=100, desc="Transcribing with OpenAI API") as pbar:
                    # Create transcription
                    response = client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        response_format="text"
                    )
                    pbar.update(100)
                    
                    transcription = response
        except Exception as e:
            # If API fails, fall back to local model
            logger.warning(f"OpenAI API transcription failed, falling back to local model: {e}")
            console.print("[yellow]API transcription failed, using local Whisper model...[/yellow]")
            
            # Load the Whisper model
            with tqdm(total=100, desc="Loading Whisper model") as pbar:
                model = whisper.load_model("base")
                pbar.update(100)
            
            # Transcribe the audio
            with tqdm(total=100, desc="Transcribing with local model") as pbar:
                result = model.transcribe(str(audio_path))
                pbar.update(100)
                
                transcription = result["text"]
        
        # Save transcription to file
        transcript_filename = f"{audio_path.stem}.txt"
        transcript_path = Path("transcriptions") / transcript_filename
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcription)
            
        logger.info(f"Transcription saved to: {transcript_path}")
        console.print(f"[green]Transcription saved to:[/green] {transcript_path}")
        
        return transcription
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        console.print(f"[bold red]Error transcribing audio:[/bold red] {str(e)}")
        raise


def load_template() -> str:
    """Load the prompt template from file."""
    template_path = Path("templates") / "prompt.txt"
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        return template
    
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        console.print(f"[bold red]Template file not found:[/bold red] {template_path}")
        raise


def generate_case_notes(transcript: str) -> str:
    """
    Generate structured case notes from transcript using OpenAI API.
    
    Args:
        transcript: Transcribed text from audio
        
    Returns:
        Structured case notes as markdown text
    """
    logger.info("Generating case notes from transcript")
    console.print("[bold blue]Generating[/bold blue] structured case notes...")
    
    # Load prompt template and replace placeholder
    template = load_template()
    prompt = template.replace("{{TRANSCRIPT}}", transcript)
    
    try:
        with tqdm(total=100, desc="Processing with AI") as pbar:
            response = client.chat.completions.create(
                model="gpt-4",  # Can be configured based on needs
                messages=[
                    {"role": "system", "content": "You are a medical assistant specialized in chiropractic care documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            pbar.update(100)
            
        case_notes = response.choices[0].message.content
        logger.info("Case notes generated successfully")
        return case_notes
    
    except Exception as e:
        logger.error(f"Error generating case notes: {e}")
        console.print(f"[bold red]Error generating case notes:[/bold red] {str(e)}")
        raise


def save_case_notes(filename: str, content: str) -> Path:
    """
    Save case notes to a markdown file.
    
    Args:
        filename: Name of the file (without extension)
        content: Markdown content to save
        
    Returns:
        Path to the saved file
    """
    # Create filename with date
    date_str = datetime.now().strftime("%Y%m%d")
    output_filename = f"{date_str}_{filename}.md"
    output_path = Path("case_notes") / output_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    logger.info(f"Case notes saved to: {output_path}")
    console.print(f"[green]Case notes saved to:[/green] {output_path}")
    
    return output_path


def display_markdown(content: str):
    """Display markdown content in the console."""
    md = Markdown(content)
    console.print(md) 