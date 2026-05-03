# -*- mode: python ; coding: utf-8 -*-
"""贪吃蛇游戏 PyInstaller 打包配置"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ========== 资源路径 ==========
PROJECT_DIR = os.path.dirname(os.path.abspath(SPEC))
ANACONDA_DIR = 'F:/ananconda'

# 字体文件
font_data = [(os.path.join(PROJECT_DIR, 'game', 'resources', 'msyh.ttc'), 'game/resources')]

# Anaconda Tcl/Tk DLL（8.6.14，覆盖可能自动收集的旧版本）
tcl_dlls = [
    (os.path.join(ANACONDA_DIR, 'Library', 'bin', 'tcl86t.dll'), '.'),
    (os.path.join(ANACONDA_DIR, 'Library', 'bin', 'tk86t.dll'), '.'),
]

# 收集 tkinter 的所有子模块
tkinter_hidden = collect_submodules('tkinter')

a = Analysis(
    [os.path.join(PROJECT_DIR, 'snake_game.py')],
    pathex=[PROJECT_DIR],
    binaries=tcl_dlls,
    datas=font_data,
    hiddenimports=tkinter_hidden + ['tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(PROJECT_DIR, 'hook-rth-tkinter-fix.py')],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 移除自动收集的旧版 tcl/tk DLL（保留 Anaconda 的 tcl86t.dll/tk86t.dll）
to_remove_bin = []
for i, item in enumerate(a.binaries):
    name = os.path.basename(item[0]).lower()
    if name in ('tcl86.dll', 'tk86.dll'):
        to_remove_bin.append(i)
for i in sorted(to_remove_bin, reverse=True):
    removed = a.binaries.pop(i)
    print(f"Removed old DLL: {removed}")

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='贪吃蛇游戏',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
