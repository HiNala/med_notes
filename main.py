#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import List
import logging
from PyQt6.QtWidgets import QApplication
from gui import MainWindow

import typer
from rich.panel import Panel
from rich import print as rprint
from rich.markdown import Markdown

# Determine if we're running as a script or as a bundled executable
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (exe)
    BASE_DIR = Path(sys._MEIPASS)
else:
    # If the application is run as a script
    BASE_DIR = Path(__file__).parent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from utils import (
    ensure_directories_exist,
    list_audio_files,
    transcribe_audio,
    generate_case_notes,
    save_case_notes,
    display_markdown,
    console,
    logger
)

# Initialize Typer CLI app
app = typer.Typer(
    help="CLI tool for transcribing and summarizing audio content",
    add_completion=False
)


@app.command("transcribe")
def transcribe_command(
    audio_file: str = typer.Argument(..., help="Path to the audio file to transcribe"),
    output_file: str = typer.Option(None, "--output", "-o", help="Path to save the transcription"),
    model: str = typer.Option("gpt-4", "--model", "-m", help="OpenAI model to use for transcription"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing transcription file")
):
    """Transcribe an audio file using OpenAI's Whisper API."""
    try:
        # Convert paths to Path objects
        audio_path = Path(audio_file)
        output_path = Path(output_file) if output_file else None
        
        # If running as exe, look for files in the correct location
        if getattr(sys, 'frozen', False):
            if not audio_path.is_absolute():
                audio_path = BASE_DIR / "audio_recordings" / audio_path.name
            if output_path and not output_path.is_absolute():
                output_path = BASE_DIR / "transcriptions" / output_path.name
        
        # Validate audio file
        if not audio_path.exists():
            console.print(f"[red]Error: Audio file not found: {audio_path}[/red]")
            raise typer.Exit(1)
        
        if not audio_path.is_file():
            console.print(f"[red]Error: Not a valid file: {audio_path}[/red]")
            raise typer.Exit(1)
        
        # Check if output file exists
        if output_path and output_path.exists() and not overwrite:
            try:
                console.print(f"[yellow]Warning: Output file already exists: {output_path}[/yellow]")
                response = input("Do you want to overwrite it? (y/n): ").strip().lower()
                if response != 'y':
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)
            except Exception as e:
                console.print(f"[red]Error reading input: {e}[/red]")
                raise typer.Exit(1)
        
        # Transcribe the audio file
        with console.status("[bold green]Transcribing audio...[/bold green]"):
            try:
                transcript = transcribe_audio(audio_path)
            except Exception as e:
                console.print(f"[red]Error transcribing audio: {e}[/red]")
                raise typer.Exit(1)
        
        # Save the transcription
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                console.print(f"[green]Transcription saved to: {output_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving transcription: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Print the transcription to console
            console.print("\n[bold]Transcription:[/bold]")
            console.print(Markdown(transcript))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("version")
def version():
    """Display the application version."""
    console.print("Transcript Summarization Tool v1.0.0")


@app.command("help")
def help_command():
    """Show detailed help information and examples."""
    rprint(Panel.fit(
        "[bold blue]Transcript Summarization Tool[/bold blue]\n\n"
        "This tool helps you transcribe audio recordings and generate\n"
        "structured summaries using OpenAI's AI models.\n\n"
        "[bold yellow]Quick Start:[/bold yellow]\n"
        "1. Place your audio file in the [italic]audio_recordings[/italic] folder\n"
        "2. Run: [italic]python main.py transcribe[/italic]\n"
        "3. Select your file when prompted\n\n"
        "[bold yellow]Common Commands:[/bold yellow]\n"
        "- List audio files: [italic]python main.py transcribe --list[/italic]\n"
        "- Process a specific file: [italic]python main.py transcribe \"your_recording.mp3\"[/italic]\n"
        "- Just view notes (don't save): [italic]python main.py transcribe --no-save[/italic]\n"
        "- Just save notes (don't display): [italic]python main.py transcribe --no-display[/italic]\n\n"
        "[bold yellow]Need More Help?[/bold yellow]\n"
        "See the README.md file for detailed instructions and troubleshooting."
    ))


@app.callback()
def main():
    """
    Transcript Summarization Tool
    
    A tool for transcribing audio recordings and generating
    structured summaries using OpenAI's AI models.
    """
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # If no arguments are provided, run the transcribe command
    if len(sys.argv) == 1:
        sys.argv.append("transcribe")
    main() 