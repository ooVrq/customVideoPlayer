# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icons/icon.ico', 'icons'), ('keybinds.txt', '.'), ('saveData.txt', '.'), ('C:\\Users\\kwuh\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\tkinterdnd2', 'tkinterdnd2/')],
    hiddenimports=[],
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
    name='main',
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
    icon=['C:\\Users\\kwuh\\PycharmProjects\\customVideoPlayer\\icons\\icon.ico'],
)
