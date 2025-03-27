#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import List
import logging

import typer
from rich.panel import Panel
from rich import print as rprint

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
    audio_file: str = typer.Argument(None, help="Path to the audio file to transcribe"),
    list_files: bool = typer.Option(False, "--list", "-l", help="List available audio files"),
    save: bool = typer.Option(True, help="Save the case notes to a file"),
    display: bool = typer.Option(True, help="Display the case notes in the terminal"),
):
    """
    Transcribe an audio recording and generate structured case notes.
    
    If no audio file is specified, the application will list available files
    and prompt you to select one.
    """
    # Ensure all necessary directories exist
    ensure_directories_exist()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print(Panel(
            "[bold red]OpenAI API key not found![/bold red]\n"
            "Please set your API key in a .env file or as an environment variable:\n"
            "OPENAI_API_KEY=your_api_key_here",
            title="Error"
        ))
        raise typer.Exit(code=1)
    
    # List audio files and exit if requested
    if list_files:
        audio_files = list_audio_files()
        if not audio_files:
            console.print("[yellow]No audio files found in the 'audio_recordings' directory.[/yellow]")
            return
        
        console.print("[bold]Available audio files:[/bold]")
        for i, file in enumerate(audio_files, 1):
            console.print(f"{i}. {file.name}")
        return
    
    # Get the audio file to process
    audio_path = None
    
    if audio_file:
        # User provided a file
        audio_path = Path(audio_file)
        if not audio_path.exists():
            # Try looking in the audio_recordings directory
            audio_path = Path("audio_recordings") / audio_path.name
            if not audio_path.exists():
                console.print(f"[bold red]Error:[/bold red] Audio file not found: {audio_file}")
                raise typer.Exit(code=1)
    else:
        # No file provided, let user select from list
        audio_files = list_audio_files()
        
        if not audio_files:
            console.print(
                "[yellow]No audio files found in the 'audio_recordings' directory.[/yellow]\n"
                "Please add audio files to this directory and try again."
            )
            raise typer.Exit(code=1)
        
        console.print("[bold]Available audio files:[/bold]")
        for i, file in enumerate(audio_files, 1):
            console.print(f"{i}. {file.name}")
        
        # Prompt user to select a file
        selection = typer.prompt("Select a file by number", type=int)
        
        try:
            audio_path = audio_files[selection - 1]
        except IndexError:
            console.print("[bold red]Invalid selection[/bold red]")
            raise typer.Exit(code=1)
    
    # Process the audio file
    console.print(Panel(f"Processing audio file: [bold]{audio_path.name}[/bold]", title="🔊 Audio Processing"))
    
    try:
        # Transcribe audio file
        transcript = transcribe_audio(audio_path)
        console.print("[green]✓[/green] Transcription completed")
        
        # Generate case notes
        case_notes = generate_case_notes(transcript)
        console.print("[green]✓[/green] Case notes generated")
        
        # Display case notes if requested
        if display:
            console.print(Panel(
                "[bold cyan]The following are the structured case notes generated from your audio:[/bold cyan]",
                title="📝 Generated Case Notes"
            ))
            display_markdown(case_notes)
            
            # Add a separator after the case notes for clarity
            console.print("\n" + "-" * 80 + "\n")
        
        # Save case notes if requested
        if save:
            output_path = save_case_notes(audio_path.stem, case_notes)
            console.print(f"[green]✓[/green] Case notes saved to: [bold]{output_path}[/bold]")
        
        console.print("[bold green]Processing complete![/bold green]")
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


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
    pass


if __name__ == "__main__":
    # If no arguments are provided, run the transcribe command
    if len(sys.argv) == 1:
        sys.argv.append("transcribe")
    app() 