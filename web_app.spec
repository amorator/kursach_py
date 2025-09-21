# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['web_app.py'],
    pathex=[],
    binaries=[],
    datas=[('app', 'app')],
    hiddenimports=[
        'flask',
        'matplotlib.backends.backend_agg',
        'matplotlib.figure',
        'matplotlib.pyplot',
        'numpy',
        'sympy',
        'scipy',
        'app.optim.methods',
        'app.optim.selection',
        'app.visualize'
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
