@echo off
setlocal enabledelayedexpansion

echo Starting build process...

REM Check Python version
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    exit /b 1
)

REM Create icon if it doesn't exist
if not exist icon.ico (
    echo Creating application icon...
    python create_icon.py
    if errorlevel 1 (
        echo Error: Failed to create icon
        exit /b 1
    )
)

REM Create required directories if they don't exist
echo Creating required directories...
mkdir audio_recordings 2>nul
mkdir transcriptions 2>nul
mkdir case_notes 2>nul
mkdir templates 2>nul

REM Run build script
echo Building executable...
python build.py
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)

REM Create distribution package
echo Creating distribution package...
if exist dist\Medical_Note_Taker.exe (
    echo Creating zip file...
    powershell Compress-Archive -Path "dist\Medical_Note_Taker.exe","audio_recordings","transcriptions","case_notes","templates",".env.example","README.md","requirements.txt" -DestinationPath "dist\Medical_Note_Taker.zip" -Force
    if errorlevel 1 (
        echo Error: Failed to create zip file
        exit /b 1
    )
)

echo Build completed successfully!
echo.
echo The following files have been created in the dist folder:
echo 1. Medical_Note_Taker.exe - A self-contained executable
echo 2. Medical_Note_Taker.zip - A distribution package containing all necessary files
echo.
echo To run the application:
echo 1. Edit the .env file to add your OpenAI API key
echo 2. Run Medical_Note_Taker.exe
echo.
exit /b 0 