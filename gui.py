import sys
import os
from pathlib import Path
import shutil
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextBrowser, QFileDialog,
    QProgressBar, QMessageBox, QGroupBox, QLineEdit, QDialog,
    QFormLayout, QDialogButtonBox, QComboBox, QSplitter, QTextEdit,
    QStyle
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Get the base directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Configure logging with the correct base directory
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "med_note.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Update directory paths
AUDIO_DIR = BASE_DIR / "audio_recordings"
TRANSCRIPTIONS_DIR = BASE_DIR / "transcriptions"
CASE_NOTES_DIR = BASE_DIR / "case_notes"
TEMPLATES_DIR = BASE_DIR / "templates"

from utils import (
    ensure_directories_exist,
    list_audio_files,
    transcribe_audio,
    generate_case_notes,
    save_case_notes,
    load_dotenv,
    load_template,
    TEMPLATES_DIR,
    AUDIO_DIR,
    TRANSCRIPTIONS_DIR,
    CASE_NOTES_DIR,
    BASE_DIR
)

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Settings")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # API Key section
        api_group = QGroupBox("OpenAI API Key")
        api_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("API Key:", self.api_key_input)
        
        self.test_button = QPushButton("Test API Key")
        self.test_button.clicked.connect(self.test_api_key)
        api_layout.addRow("", self.test_button)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Model selection section
        model_group = QGroupBox("Language Model")
        model_layout = QVBoxLayout()
        
        model_description = QLabel(
            "Select the OpenAI model to use for generating medical notes. "
            "More capable models may provide better results but cost more."
        )
        model_description.setWordWrap(True)
        model_layout.addWidget(model_description)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo"
        ])
        
        # Add model descriptions
        self.model_combo.setItemData(0, "Fast and cost-effective, good for most cases", Qt.ItemDataRole.ToolTipRole)
        self.model_combo.setItemData(1, "More accurate and better at complex medical terminology", Qt.ItemDataRole.ToolTipRole)
        self.model_combo.setItemData(2, "Latest model with improved capabilities and knowledge", Qt.ItemDataRole.ToolTipRole)
        
        model_layout.addWidget(self.model_combo)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Load existing settings
        load_dotenv()
        existing_key = os.getenv("OPENAI_API_KEY", "")
        existing_model = os.getenv("GPT_MODEL", "gpt-3.5-turbo")
        if existing_key:
            self.api_key_input.setText(existing_key)
        if existing_model:
            index = self.model_combo.findText(existing_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
    
    def test_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key")
            return
        
        try:
            import openai
            openai.api_key = api_key
            openai.models.list()
            QMessageBox.information(self, "Success", "API key is valid!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid API key: {str(e)}")

class TemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit System Prompt")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Enter the system prompt that defines how the AI should process medical transcripts. "
            "This prompt will be used for all transcriptions."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # System prompt section
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlaceholderText("Enter your system prompt here...")
        layout.addWidget(self.system_prompt)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_template)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Load existing template
        self.load_existing_template()
    
    def load_existing_template(self):
        try:
            template_data = load_template()
            self.system_prompt.setText(template_data["system_content"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load existing template: {str(e)}")
    
    def save_template(self):
        system_content = self.system_prompt.toPlainText().strip()
        
        if not system_content:
            QMessageBox.warning(self, "Error", "System prompt is required.")
            return
        
        try:
            os.makedirs(TEMPLATES_DIR, exist_ok=True)
            
            template_content = "---\n"
            template_content += "role: system\n"
            template_content += f"content: {system_content}\n"
            template_content += "---\n\n"
            template_content += "Please analyze the following transcript and generate structured medical notes:\n\n{{TRANSCRIPT}}"
            
            template_path = TEMPLATES_DIR / "prompt.txt"
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(template_content)
            
            QMessageBox.information(self, "Success", "System prompt saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save template: {str(e)}")

class TranscriptionWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path
        self._is_running = True
    
    def run(self):
        try:
            # Check if API key is set
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key not found. Please set it in the API Settings.")
            
            # Check if file exists and is accessible
            if not self.audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {self.audio_path}")
            
            # Check file size (max 25MB for OpenAI API)
            file_size = self.audio_path.stat().st_size
            if file_size > 25 * 1024 * 1024:  # 25MB in bytes
                raise ValueError("Audio file is too large. Maximum size is 25MB.")
            
            # Check file format
            valid_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma', '.aiff', '.alac', '.opus', '.webm'}
            if self.audio_path.suffix.lower() not in valid_extensions:
                raise ValueError(f"Unsupported file format: {self.audio_path.suffix}. Supported formats: {', '.join(valid_extensions)}")
            
            # Check if file is readable
            if not os.access(self.audio_path, os.R_OK):
                raise PermissionError(f"Cannot read file: {self.audio_path}")
            
            self.progress.emit(30, "Transcribing audio...")
            
            # Check internet connection
            try:
                import socket
                socket.create_connection(("www.google.com", 80), timeout=5)
            except OSError:
                raise ConnectionError("No internet connection. Please check your network.")
            
            # Perform transcription
            transcript = transcribe_audio(self.audio_path)
            
            if not self._is_running:
                return
                
            self.progress.emit(100, "Transcription complete!")
            self.finished.emit(transcript)
            
        except FileNotFoundError as e:
            self.error.emit(f"File error: {str(e)}")
        except ValueError as e:
            self.error.emit(f"Validation error: {str(e)}")
        except PermissionError as e:
            self.error.emit(f"Permission error: {str(e)}")
        except ConnectionError as e:
            self.error.emit(f"Connection error: {str(e)}")
        except openai.OpenAIError as e:
            self.error.emit(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")
        finally:
            self._is_running = False
    
    def stop(self):
        """Stop the transcription process."""
        self._is_running = False

class NotesWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, str)  # Now emits both raw notes and HTML content
    error = pyqtSignal(str)
    
    def __init__(self, transcript, audio_stem, parent=None):
        super().__init__(parent)
        self.transcript = transcript
        self.audio_stem = audio_stem
        self._is_running = True
    
    def run(self):
        try:
            # Validate transcript
            if not self.transcript or not isinstance(self.transcript, str):
                raise ValueError("Invalid transcript provided")
            
            # Check if API key is set
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key not found. Please set it in the API Settings.")
            
            # Check internet connection
            try:
                import socket
                socket.create_connection(("www.google.com", 80), timeout=5)
            except OSError:
                raise ConnectionError("No internet connection. Please check your network.")
            
            self.progress.emit(30, "Generating medical notes...")
            
            # Generate notes
            notes, html_content = generate_case_notes(self.transcript)
            
            if not self._is_running:
                return
            
            self.progress.emit(60, "Saving notes...")
            
            # Save notes
            output_path = save_case_notes(self.audio_stem, notes, html_content)
            
            if not self._is_running:
                return
            
            self.progress.emit(100, "Notes generated successfully!")
            self.finished.emit(notes, html_content)
            
        except ValueError as e:
            self.error.emit(f"Validation error: {str(e)}")
        except ConnectionError as e:
            self.error.emit(f"Connection error: {str(e)}")
        except openai.OpenAIError as e:
            self.error.emit(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")
        finally:
            self._is_running = False
    
    def stop(self):
        """Stop the notes generation process."""
        self._is_running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Note Taker")
        self.setMinimumSize(1200, 800)
        
        # Initialize variables
        self.current_transcript = None
        self.current_audio_path = None
        self.transcribe_worker = None
        self.notes_worker = None
        
        # Ensure directories exist
        try:
            ensure_directories_exist()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create required directories: {str(e)}")
            raise
        
        # Check for API key
        self.check_api_key()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create horizontal splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: File management
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # File list group
        file_group = QGroupBox("Audio Files")
        file_layout = QVBoxLayout()
        file_layout.setSpacing(5)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.file_list.itemClicked.connect(self.on_file_selected)
        file_layout.addWidget(self.file_list)
        
        # File buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.upload_button = QPushButton("Upload File")
        self.upload_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart))
        self.upload_button.clicked.connect(self.upload_file)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.refresh_button.clicked.connect(self.refresh_file_list)
        
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.refresh_button)
        file_layout.addLayout(button_layout)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        # Action buttons
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout()
        action_layout.setSpacing(5)
        
        self.transcribe_button = QPushButton("Transcribe")
        self.transcribe_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.transcribe_button.clicked.connect(self.transcribe_file)
        self.transcribe_button.setEnabled(False)
        
        self.generate_button = QPushButton("Generate Medical Notes")
        self.generate_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.generate_button.clicked.connect(self.generate_notes)
        self.generate_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setEnabled(False)
        
        action_layout.addWidget(self.transcribe_button)
        action_layout.addWidget(self.generate_button)
        action_layout.addWidget(self.cancel_button)
        
        action_group.setLayout(action_layout)
        left_layout.addWidget(action_group)
        
        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)
        
        # Right side: Output
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Output group
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        try:
            self.output_view = QWebEngineView()
            self.output_view.setHtml("""
                <html>
                <head>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            padding: 20px;
                            color: #333;
                        }
                        h1 {
                            color: #2c3e50;
                            text-align: center;
                        }
                        .instructions {
                            background-color: #f8f9fa;
                            padding: 20px;
                            border-radius: 5px;
                            margin: 20px 0;
                        }
                    </style>
                </head>
                <body>
                    <h1>Medical Note Taker</h1>
                    <div class="instructions">
                        <p>1. Upload an audio file using the 'Upload File' button</p>
                        <p>2. Select the file from the list</p>
                        <p>3. Click 'Transcribe' to convert audio to text</p>
                        <p>4. Click 'Generate Medical Notes' to create structured notes</p>
                    </div>
                </body>
                </html>
            """)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize WebEngineView: {str(e)}")
            raise
        
        output_layout.addWidget(self.output_view)
        
        output_group.setLayout(output_layout)
        right_layout.addWidget(output_group)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])  # Set initial sizes
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        
        # Load initial file list
        self.refresh_file_list()
    
    def check_api_key(self):
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            reply = QMessageBox.question(
                self,
                "API Key Required",
                "No OpenAI API key found. Would you like to set one now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.set_api_key()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        api_key_action = QAction("API Settings", self)
        api_key_action.triggered.connect(self.set_api_key)
        settings_menu.addAction(api_key_action)
        
        template_action = QAction("Edit System Prompt", self)
        template_action.triggered.connect(self.edit_template)
        settings_menu.addAction(template_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def set_api_key(self):
        dialog = ApiKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_key = dialog.api_key_input.text().strip()
            model = dialog.model_combo.currentText()
            if api_key:
                with open(".env", "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key}\n")
                    f.write(f"GPT_MODEL={model}\n")
                self.status_label.setText("API settings updated successfully")
                load_dotenv(override=True)
    
    def edit_template(self):
        dialog = TemplateDialog(self)
        dialog.exec()
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About Medical Note Taker",
            "Medical Note Taker v1.0.0\n\n"
            "A tool for medical professionals to transcribe audio recordings\n"
            "and generate structured case notes using AI.\n\n"
            "© 2024 Your Organization"
        )
    
    def refresh_file_list(self):
        self.file_list.clear()
        audio_files = list_audio_files()
        for file in audio_files:
            self.file_list.addItem(file.name)
        self.status_label.setText(f"Found {len(audio_files)} audio files")
    
    def on_file_selected(self, item):
        self.transcribe_button.setEnabled(True)
        self.generate_button.setEnabled(False)
        self.current_transcript = None
        self.output_view.setHtml("<center><h2>Click 'Transcribe' to process the selected file</h2></center>")
        self.status_label.setText(f"Selected: {item.text()}")
    
    def upload_file(self):
        """Upload an audio file to the audio_recordings directory."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Audio File",
                "",
                "Audio Files (*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.aiff *.alac *.opus *.webm)"
            )
            
            if file_path:
                # Convert to Path object
                source_path = Path(file_path)
                
                # Validate file
                if not source_path.exists():
                    raise FileNotFoundError(f"Selected file does not exist: {file_path}")
                
                # Check file size (max 25MB for OpenAI API)
                file_size = source_path.stat().st_size
                if file_size > 25 * 1024 * 1024:  # 25MB in bytes
                    raise ValueError("Audio file is too large. Maximum size is 25MB.")
                
                # Ensure the audio directory exists
                os.makedirs(AUDIO_DIR, exist_ok=True)
                
                # Create destination path
                dest_path = AUDIO_DIR / source_path.name
                
                # Check if file already exists
                if dest_path.exists():
                    reply = QMessageBox.question(
                        self,
                        "File Exists",
                        f"A file named '{source_path.name}' already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                try:
                    # Copy the file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"File uploaded successfully: {dest_path}")
                    
                    # Refresh the file list
                    self.refresh_file_list()
                    
                    # Select the newly uploaded file
                    items = self.file_list.findItems(source_path.name, Qt.MatchFlag.MatchExactly)
                    if items:
                        self.file_list.setCurrentItem(items[0])
                        self.current_audio_path = dest_path
                        
                except Exception as e:
                    logger.error(f"Error copying file: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to copy file: {str(e)}")
                    
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            QMessageBox.critical(self, "Error", f"File not found: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid file: {e}")
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            logger.error(f"Error in file upload: {e}")
            QMessageBox.critical(self, "Error", f"Failed to upload file: {str(e)}")
    
    def transcribe_file(self):
        """Transcribe the selected audio file."""
        if not self.current_audio_path:
            QMessageBox.warning(self, "Error", "Please select an audio file first")
            return
        
        try:
            # Clean up any existing workers
            if self.transcribe_worker and self.transcribe_worker.isRunning():
                self.transcribe_worker.stop()
                self.transcribe_worker.wait()
            
            # Disable buttons during processing
            self.transcribe_button.setEnabled(False)
            self.generate_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Start transcription worker
            self.transcribe_worker = TranscriptionWorker(self.current_audio_path)
            self.transcribe_worker.progress.connect(self.update_progress)
            self.transcribe_worker.finished.connect(self.transcription_finished)
            self.transcribe_worker.error.connect(self.process_error)
            self.transcribe_worker.start()
            
        except Exception as e:
            logger.error(f"Error starting transcription: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start transcription: {str(e)}")
            self.process_error(str(e))
    
    def transcription_finished(self, transcript):
        """Handle successful transcription."""
        try:
            self.current_transcript = transcript
            self.progress_bar.setVisible(False)
            self.transcribe_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            
            # Display formatted transcript
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        padding: 20px;
                        color: #333;
                    }}
                    h1 {{
                        color: #2c3e50;
                        text-align: center;
                    }}
                    .transcript {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .next-step {{
                        background-color: #e8f4f8;
                        padding: 15px;
                        border-radius: 5px;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <h1>Transcription Complete</h1>
                <div class="transcript">{transcript.replace('\n', '<br>')}</div>
                <div class="next-step">
                    <p><strong>Next step:</strong> Click 'Generate Medical Notes' to create structured notes from this transcript.</p>
                </div>
            </body>
            </html>
            """
            self.output_view.setHtml(html_content)
            self.status_label.setText("Transcription complete! Ready to generate notes.")
            
        except Exception as e:
            logger.error(f"Error displaying transcription: {e}")
            self.process_error(str(e))
    
    def generate_notes(self):
        """Generate medical notes from the transcript."""
        if not self.current_transcript:
            QMessageBox.warning(self, "Error", "Please transcribe an audio file first")
            return
        
        try:
            # Clean up any existing workers
            if self.notes_worker and self.notes_worker.isRunning():
                self.notes_worker.stop()
                self.notes_worker.wait()
            
            # Get the selected file name
            selected_items = self.file_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Error", "Please select an audio file")
                return
            
            selected_file = selected_items[0].text()
            audio_stem = Path(selected_file).stem
            
            # Disable buttons during processing
            self.transcribe_button.setEnabled(False)
            self.generate_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Start notes worker
            self.notes_worker = NotesWorker(self.current_transcript, audio_stem)
            self.notes_worker.progress.connect(self.update_progress)
            self.notes_worker.finished.connect(self.notes_finished)
            self.notes_worker.error.connect(self.process_error)
            self.notes_worker.start()
            
        except Exception as e:
            logger.error(f"Error starting notes generation: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start notes generation: {str(e)}")
            self.process_error(str(e))
    
    def notes_finished(self, notes, html_content):
        """Handle successful notes generation."""
        try:
            self.progress_bar.setVisible(False)
            self.transcribe_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            
            # Display the formatted HTML content
            self.output_view.setHtml(html_content)
            self.status_label.setText("Medical notes generated successfully!")
            
        except Exception as e:
            logger.error(f"Error displaying notes: {e}")
            self.process_error(str(e))
    
    def process_error(self, error_message):
        """Handle and display error messages."""
        try:
            # Log the error
            logger.error(f"Error in application: {error_message}")
            
            # Show error message to user
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred:\n\n{error_message}\n\n"
                "Please check the following:\n"
                "1. Your OpenAI API key is set correctly\n"
                "2. The audio file is in a supported format\n"
                "3. The audio file is not too large (max 25MB)\n"
                "4. You have an active internet connection"
            )
            
            # Reset UI state
            self.progress_bar.setVisible(False)
            self.transcribe_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            
        except Exception as e:
            # If something goes wrong in error handling, log it
            logger.error(f"Error in error handling: {e}")
    
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Stop any running workers
            if self.transcribe_worker and self.transcribe_worker.isRunning():
                self.transcribe_worker.stop()
                self.transcribe_worker.wait()
            
            if self.notes_worker and self.notes_worker.isRunning():
                self.notes_worker.stop()
                self.notes_worker.wait()
            
            event.accept()
        except Exception as e:
            logger.error(f"Error during window close: {e}")
            event.accept()
    
    def cancel_operation(self):
        """Cancel the current operation."""
        try:
            if self.transcribe_worker and self.transcribe_worker.isRunning():
                self.transcribe_worker.stop()
                self.transcribe_worker.wait()
                self.status_label.setText("Transcription cancelled")
            
            if self.notes_worker and self.notes_worker.isRunning():
                self.notes_worker.stop()
                self.notes_worker.wait()
                self.status_label.setText("Notes generation cancelled")
            
            # Reset UI
            self.progress_bar.setVisible(False)
            self.transcribe_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            
        except Exception as e:
            logger.error(f"Error cancelling operation: {e}")
            self.process_error(f"Failed to cancel operation: {str(e)}")

def main():
    load_dotenv()  # Load environment variables
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 