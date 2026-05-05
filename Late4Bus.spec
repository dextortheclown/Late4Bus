# transit.spec
import os
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('data/last_trains.py', 'data'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'pystray',
        'requests',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Late4Bus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # no terminal window
    icon='icon.ico',
    onefile=True,         # single .exe output
)