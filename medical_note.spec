
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('templates', 'templates'), ('audio_recordings', 'audio_recordings'), ('transcriptions', 'transcriptions'), ('case_notes', 'case_notes'), ('.env.example', '.')],
    hiddenimports=['openai', 'whisper', 'torch', 'torchaudio', 'numpy', 'tqdm', 'rich', 'python_dotenv', 'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineQuick', 'PyQt6.QtNetwork', 'PyQt6.QtPositioning', 'PyQt6.QtPrintSupport', 'PyQt6.QtQuick', 'PyQt6.QtQuickWidgets', 'PyQt6.QtWebChannel', 'PyQt6.QtOpenGL', 'PyQt6.QtQml'],
    hookspath=[],
    hooksconfig={},
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
    icon='icon.ico',
)
