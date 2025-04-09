import os
import sys
import subprocess
import shutil
from pathlib import Path
import PyInstaller.__main__
import whisper

def build_executable():
    print("Building executable...")
    
    # Ensure the build directory exists
    build_dir = Path("build")
    dist_dir = Path("dist")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Create necessary directories
    os.makedirs("audio_recordings", exist_ok=True)
    os.makedirs("transcriptions", exist_ok=True)
    os.makedirs("case_notes", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Get Whisper model path
    whisper_model_path = Path(whisper.__file__).parent / "assets"
    
    # Create PyInstaller spec file
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('.env.example', '.'),
        ('audio_recordings', 'audio_recordings'),
        ('transcriptions', 'transcriptions'),
        ('case_notes', 'case_notes'),
        ('{whisper_model_path}', 'whisper/assets'),
    ],
    hiddenimports=[
        'openai',
        'whisper',
        'whisper.model',
        'whisper.tokenizer',
        'whisper.decoding',
        'whisper.audio',
        'tqdm',
        'PyQt6',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngine',
        'python_dotenv',
        'numpy',
        'torch',
        'torchaudio',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add binaries for Whisper
a.binaries += [
    ('whisper/assets/*.pt', 'whisper/assets', 'DATA'),
    ('whisper/assets/*.json', 'whisper/assets', 'DATA'),
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Medical_Note_Taker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""
    
    with open("medical_note.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller with additional options
    PyInstaller.__main__.run([
        'medical_note.spec',
        '--clean',
        '--noconfirm',
        '--add-data', f'{whisper_model_path};whisper/assets',
        '--hidden-import', 'whisper.model',
        '--hidden-import', 'whisper.tokenizer',
        '--hidden-import', 'whisper.decoding',
        '--hidden-import', 'whisper.audio',
        '--hidden-import', 'torch',
        '--hidden-import', 'torchaudio',
        '--hidden-import', 'numpy',
    ])
    
    # Create necessary directories in the dist folder
    dist_app_dir = dist_dir / "Medical_Note_Taker"
    
    # Create a README file for the distribution
    readme_content = """Medical Note Taker

A powerful tool for medical professionals to transcribe audio recordings and generate structured case notes using AI.

Installation:
1. Extract all files to a folder of your choice
2. Edit the .env file to add your OpenAI API key
3. Run Medical_Note_Taker.exe

Features:
- Record or upload audio files
- Automatic transcription using OpenAI's Whisper
- AI-powered case note generation
- Markdown output format
- Modern GUI interface

System Requirements:
- Windows 10 or higher
- OpenAI API key
- Internet connection for transcription and AI features

For support or issues, please visit the GitHub repository:
https://github.com/HiNala/med_notes
"""
    
    with open(dist_app_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    # Create a batch file to run the application
    batch_content = """@echo off
echo Starting Medical Note Taker...
start Medical_Note_Taker.exe
"""
    
    with open(dist_app_dir / "Run_Medical_Note_Taker.bat", "w") as f:
        f.write(batch_content)
    
    # Create a zip file of the distribution
    import zipfile
    zip_path = dist_dir / "Medical_Note_Taker.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_app_dir)
                zipf.write(file_path, arcname)
    
    print("\nBuild complete!")
    print(f"Executable created in: {dist_app_dir}")
    print(f"Distribution package created: {zip_path}")
    print("\nTo distribute the application:")
    print(f"1. Share the {zip_path} file")
    print("2. Recipients should extract the zip file")
    print("3. Edit the .env file to add their OpenAI API key")
    print("4. Run Medical_Note_Taker.exe or Run_Medical_Note_Taker.bat")

if __name__ == "__main__":
    build_executable() 