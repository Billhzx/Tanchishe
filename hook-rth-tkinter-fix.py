# -*- coding: utf-8 -*-
"""
PyInstaller 运行时钩子：修复 Anaconda 环境下 tkinter 的 Tcl/Tk 版本冲突
在 tkinter 导入前设置正确的 TCL_LIBRARY/TK_LIBRARY 环境变量
"""

import os
import sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    tcl_data_dir = os.path.join(base_path, '_tcl_data')
    if os.path.isdir(tcl_data_dir):
        os.environ['TCL_LIBRARY'] = os.path.join(tcl_data_dir, 'tcl8.6')
        os.environ['TK_LIBRARY'] = os.path.join(tcl_data_dir, 'tk8.6')
