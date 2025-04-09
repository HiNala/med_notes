import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextEdit, QFileDialog,
    QProgressBar, QMessageBox, QComboBox, QGroupBox, QLineEdit,
    QTabWidget, QSplitter, QToolBar, QStatusBar, QMenuBar, QMenu,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QIcon, QAction, QDesktopServices
from PyQt6.QtWebEngineWidgets import QWebEngineView

from utils import (
    ensure_directories_exist,
    list_audio_files,
    transcribe_audio,
    generate_case_notes,
    save_case_notes,
    logger,
    load_dotenv
)

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set OpenAI API Key")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("OpenAI API Key:", self.api_key_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Load existing API key if available
        load_dotenv()
        existing_key = os.getenv("OPENAI_API_KEY", "")
        if existing_key:
            self.api_key_input.setText(existing_key)

class WorkerThread(QThread):
    progress = pyqtSignal(int, str)  # progress percentage and status message
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path

    def run(self):
        try:
            # Transcribe audio
            self.progress.emit(30, "Transcribing audio...")
            transcript = transcribe_audio(self.audio_path)
            
            # Generate case notes
            self.progress.emit(60, "Generating case notes...")
            case_notes = generate_case_notes(transcript)
            
            # Save case notes
            self.progress.emit(90, "Saving output...")
            output_path = save_case_notes(self.audio_path.stem, case_notes)
            
            self.progress.emit(100, "Processing complete!")
            self.finished.emit(str(output_path))
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Note Taker")
        self.setMinimumSize(1000, 700)
        
        # Ensure directories exist
        ensure_directories_exist()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Create file management tab
        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        
        # Create file selection group
        file_group = QGroupBox("Audio Files")
        file_group_layout = QVBoxLayout()
        
        # File list with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: File list and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.refresh_file_list()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        self.record_button = QPushButton("Record New")
        self.record_button.clicked.connect(self.record_audio)
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.upload_button)
        
        left_layout.addWidget(self.file_list)
        left_layout.addLayout(button_layout)
        
        # Right side: File preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.preview_label = QLabel("Select a file to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.preview_label)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        file_group_layout.addWidget(splitter)
        file_group.setLayout(file_group_layout)
        
        file_layout.addWidget(file_group)
        tabs.addTab(file_tab, "Files")
        
        # Create processing tab
        process_tab = QWidget()
        process_layout = QVBoxLayout(process_tab)
        
        # Processing controls
        process_group = QGroupBox("Processing")
        process_group_layout = QVBoxLayout()
        
        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(100)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Process button
        self.process_button = QPushButton("Process Selected File")
        self.process_button.clicked.connect(self.process_file)
        self.process_button.setEnabled(False)
        
        process_group_layout.addWidget(self.status_display)
        process_group_layout.addWidget(self.progress_bar)
        process_group_layout.addWidget(self.process_button)
        process_group.setLayout(process_group_layout)
        
        process_layout.addWidget(process_group)
        tabs.addTab(process_tab, "Processing")
        
        # Create output tab
        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)
        
        # Output controls
        output_group = QGroupBox("Output")
        output_group_layout = QVBoxLayout()
        
        # Output navigation
        nav_layout = QHBoxLayout()
        self.open_transcription_button = QPushButton("Open Transcription")
        self.open_transcription_button.clicked.connect(self.open_transcription)
        self.open_notes_button = QPushButton("Open Case Notes")
        self.open_notes_button.clicked.connect(self.open_case_notes)
        
        nav_layout.addWidget(self.open_transcription_button)
        nav_layout.addWidget(self.open_notes_button)
        
        # Output preview
        self.output_preview = QWebEngineView()
        self.output_preview.setHtml("<center><h3>Select a file to process</h3></center>")
        
        output_group_layout.addLayout(nav_layout)
        output_group_layout.addWidget(self.output_preview)
        output_group.setLayout(output_group_layout)
        
        output_layout.addWidget(output_group)
        tabs.addTab(output_tab, "Output")
        
        # Add tabs to main layout
        layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 6px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
            }
            QPushButton {
                padding: 5px;
                min-width: 80px;
            }
            QTextEdit#status_display {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
        """)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        api_key_action = QAction("Set API Key", self)
        api_key_action.triggered.connect(self.set_api_key)
        file_menu.addAction(api_key_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add API key button
        api_key_action = QAction("Set API Key", self)
        api_key_action.triggered.connect(self.set_api_key)
        toolbar.addAction(api_key_action)
        
        toolbar.addSeparator()
        
        # Add refresh button
        refresh_action = QAction("Refresh Files", self)
        refresh_action.triggered.connect(self.refresh_file_list)
        toolbar.addAction(refresh_action)

    def set_api_key(self):
        dialog = ApiKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_key = dialog.api_key_input.text()
            if api_key:
                # Save API key to .env file
                with open(".env", "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key}")
                self.statusBar().showMessage("API key updated successfully")
                # Reload environment variables
                load_dotenv(override=True)

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
        self.statusBar().showMessage(f"Found {len(audio_files)} audio files")

    def on_file_selected(self, item):
        self.process_button.setEnabled(True)
        self.statusBar().showMessage(f"Selected: {item.text()}")
        
        # Update preview
        file_path = Path("audio_recordings") / item.text()
        if file_path.exists():
            self.preview_label.setText(f"Selected file: {item.text()}\nSize: {file_path.stat().st_size / 1024:.1f} KB")

    def process_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        selected_file = selected_items[0].text()
        audio_path = Path("audio_recordings") / selected_file
        
        # Disable UI during processing
        self.process_button.setEnabled(False)
        self.file_list.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_display.clear()
        
        # Create and start worker thread
        self.worker = WorkerThread(audio_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_display.append(f"{message} ({value}%)")
        self.statusBar().showMessage(message)

    def processing_finished(self, output_path):
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.file_list.setEnabled(True)
        self.statusBar().showMessage("Processing complete")
        
        # Update output preview
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.output_preview.setHtml(content)
        
        # Show success message
        QMessageBox.information(
            self,
            "Success",
            f"Processing complete!\nOutput saved to: {output_path}"
        )

    def processing_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.file_list.setEnabled(True)
        self.statusBar().showMessage("Error during processing")
        self.status_display.append(f"Error: {error_message}")
        
        # Show error message
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during processing:\n{error_message}"
        )

    def record_audio(self):
        QMessageBox.information(
            self,
            "Coming Soon",
            "Audio recording functionality will be implemented in a future update."
        )

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.ogg *.flac *.aac *.wma *.aiff *.alac *.opus *.webm)"
        )
        
        if file_path:
            # Copy file to audio_recordings directory
            dest_path = Path("audio_recordings") / Path(file_path).name
            import shutil
            shutil.copy2(file_path, dest_path)
            self.refresh_file_list()
            self.statusBar().showMessage(f"File uploaded: {dest_path.name}")

    def open_transcription(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        selected_file = selected_items[0].text()
        date_str = selected_file.split("_")[0]  # Assuming filename starts with date
        transcript_path = Path("transcriptions") / f"{date_str}_{Path(selected_file).stem}_transcript.md"
        
        if transcript_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(transcript_path)))
        else:
            QMessageBox.warning(
                self,
                "File Not Found",
                "Transcription file not found. Please process the audio file first."
            )

    def open_case_notes(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        selected_file = selected_items[0].text()
        date_str = selected_file.split("_")[0]  # Assuming filename starts with date
        notes_path = Path("case_notes") / f"{date_str}_{Path(selected_file).stem}_notes.md"
        
        if notes_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(notes_path)))
        else:
            QMessageBox.warning(
                self,
                "File Not Found",
                "Case notes file not found. Please process the audio file first."
            )

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 