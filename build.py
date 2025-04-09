import os
import shutil
import logging
import PyInstaller.__main__
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler()
    ]
)

def clean_build_dirs():
    """Clean build and dist directories"""
    logging.info("Cleaning build directories...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            logging.info(f"Cleaned {dir_name} directory")

def create_required_dirs():
    """Create required directories"""
    logging.info("Creating required directories...")
    dirs_to_create = ['audio_recordings', 'transcriptions', 'case_notes', 'templates']
    for dir_name in dirs_to_create:
        os.makedirs(dir_name, exist_ok=True)
        logging.info(f"Created {dir_name} directory")

def check_required_files():
    """Check if all required files exist"""
    logging.info("Checking for required files...")
    required_files = [
        'main.py',
        'gui.py',
        'utils.py',
        'requirements.txt',
        'icon.ico',
        'templates/prompt.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        error_msg = f"Missing required files: {', '.join(missing_files)}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logging.info("All required files found")

def build_executable():
    """Build the executable using PyInstaller"""
    logging.info("Starting build process...")
    try:
        # Get PyQt6 paths
        import PyQt6
        pyqt_path = os.path.dirname(PyQt6.__file__)
        qt_path = os.path.join(pyqt_path, "Qt6")
        webengine_path = os.path.join(qt_path, "plugins", "webengine")
        resources_path = os.path.join(qt_path, "resources")
        bin_path = os.path.join(qt_path, "bin")

        PyInstaller.__main__.run([
            'main.py',
            '--name=Medical_Note_Taker',
            '--onefile',
            '--windowed',
            '--icon=icon.ico',
            '--add-data=templates;templates',
            '--add-data=icon.ico;.',
            f'--add-data={os.path.join(resources_path, "qtwebengine_resources.pak")};PyQt6/Qt6/resources',
            f'--add-data={os.path.join(resources_path, "qtwebengine_resources_100p.pak")};PyQt6/Qt6/resources',
            f'--add-data={os.path.join(resources_path, "qtwebengine_devtools_resources.pak")};PyQt6/Qt6/resources',
            f'--add-data={os.path.join(bin_path, "QtWebEngineProcess.exe")};PyQt6/Qt6/bin',
            '--hidden-import=PyQt6.QtWebEngineWidgets',
            '--hidden-import=PyQt6.QtWebEngineCore',
            '--collect-all=PyQt6',
            '--collect-all=openai',
            '--collect-all=tiktoken',
            '--collect-all=regex',
            '--collect-all=tqdm',
            '--collect-all=requests',
            '--collect-all=certifi',
            '--collect-all=charset_normalizer',
            '--collect-all=idna',
            '--collect-all=urllib3',
            '--collect-all=typing_extensions'
        ])
        logging.info("Build completed successfully")
    except Exception as e:
        logging.error(f"Build failed: {str(e)}")
        raise

def main():
    try:
        clean_build_dirs()
        create_required_dirs()
        check_required_files()
        build_executable()
    except Exception as e:
        logging.error(f"Build process failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()