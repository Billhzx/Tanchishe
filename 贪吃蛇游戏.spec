# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['snake_game.py'],
    pathex=[],
    binaries=[],
    datas=[('game/resources/msyh.ttc', 'game/resources'), ('F:/ananconda/Library/lib/tcl8.6', 'tcl/tcl8.6'), ('F:/ananconda/Library/lib/tk8.6', 'tcl/tk8.6')],
    hiddenimports=['tkinter', 'tkinter.messagebox'],
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
    name='贪吃蛇游戏',
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
)
