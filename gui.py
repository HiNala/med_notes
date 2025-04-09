import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTextEdit, QFileDialog,
    QProgressBar, QMessageBox, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from utils import (
    ensure_directories_exist,
    list_audio_files,
    transcribe_audio,
    generate_case_notes,
    save_case_notes,
    logger
)

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path

    def run(self):
        try:
            # Transcribe audio
            self.progress.emit(30)
            transcript = transcribe_audio(self.audio_path)
            
            # Generate case notes
            self.progress.emit(60)
            case_notes = generate_case_notes(transcript)
            
            # Save case notes
            self.progress.emit(90)
            output_path = save_case_notes(self.audio_path.stem, case_notes)
            
            self.progress.emit(100)
            self.finished.emit(str(output_path))
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Note Taker")
        self.setMinimumSize(800, 600)
        
        # Ensure directories exist
        ensure_directories_exist()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create file selection group
        file_group = QGroupBox("Audio Files")
        file_layout = QVBoxLayout()
        
        # File list
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
        
        file_layout.addWidget(self.file_list)
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        
        # Create processing group
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Process button
        self.process_button = QPushButton("Process Selected File")
        self.process_button.clicked.connect(self.process_file)
        self.process_button.setEnabled(False)
        
        process_layout.addWidget(self.progress_bar)
        process_layout.addWidget(self.process_button)
        process_group.setLayout(process_layout)
        
        # Create output group
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        
        # Add all groups to main layout
        layout.addWidget(file_group)
        layout.addWidget(process_group)
        layout.addWidget(output_group)
        
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
        """)

    def refresh_file_list(self):
        self.file_list.clear()
        audio_files = list_audio_files()
        for file in audio_files:
            self.file_list.addItem(file.name)

    def on_file_selected(self, item):
        self.process_button.setEnabled(True)
        self.statusBar().showMessage(f"Selected: {item.text()}")

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
        
        # Create and start worker thread
        self.worker = WorkerThread(audio_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def processing_finished(self, output_path):
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.file_list.setEnabled(True)
        self.statusBar().showMessage(f"Processing complete. Output saved to: {output_path}")
        
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
        
        # Show error message
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during processing:\n{error_message}"
        )

    def record_audio(self):
        # TODO: Implement audio recording functionality
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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 