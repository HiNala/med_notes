@echo off
echo Building Medical Note Taker...

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create icon
echo Creating application icon...
python create_icon.py

REM Build executable
echo Building executable...
python build.py

echo.
echo Build complete!
echo The executable and distribution package can be found in the dist folder.
echo.
pause 