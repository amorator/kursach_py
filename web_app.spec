# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['web_app.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('app', 'app'),  # Включаем всю папку app
    ],
    hiddenimports=[
        'flask',
        'app.optim.methods',
        'app.optim.selection', 
        'app.visualize',
        'numpy',
        'sympy',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'matplotlib.pyplot',
        'io',
        'base64',
        'json',
        'traceback',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='optimization_web_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
