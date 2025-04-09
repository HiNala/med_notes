import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    print("Building executable...")
    
    # Ensure the build directory exists
    build_dir = Path("build")
    dist_dir = Path("dist")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
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
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

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
    console=False,
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
    
    # Run PyInstaller
    subprocess.run([
        "pyinstaller",
        "--clean",
        "medical_note.spec"
    ], check=True)
    
    # Create necessary directories in the dist folder
    dist_app_dir = dist_dir / "Medical_Note_Taker"
    os.makedirs(dist_app_dir / "audio_recordings", exist_ok=True)
    os.makedirs(dist_app_dir / "transcriptions", exist_ok=True)
    os.makedirs(dist_app_dir / "case_notes", exist_ok=True)
    
    # Copy .env.example to dist folder
    shutil.copy2(".env.example", dist_app_dir / ".env")
    
    print("\nBuild complete!")
    print(f"Executable created in: {dist_app_dir}")
    print("\nTo run the application:")
    print(f"1. Navigate to: {dist_app_dir}")
    print("2. Edit the .env file to add your OpenAI API key")
    print("3. Run Medical_Note_Taker.exe")

if __name__ == "__main__":
    build_executable() 