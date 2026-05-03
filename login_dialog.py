# -*- coding: utf-8 -*-
"""
tkinter 登录/注册对话框
在 Pygame 启动前完成用户认证，解决 Pygame 输入框不支持中文输入法的问题
"""

import os
import sys

# PyInstaller 打包后修复 Tcl/Tk 路径
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    tcl_dir = os.path.join(base_path, '_tcl_data')
    if os.path.isdir(tcl_dir):
        os.environ.setdefault('TCL_LIBRARY', os.path.join(tcl_dir, 'tcl8.6'))
        os.environ.setdefault('TK_LIBRARY', os.path.join(tcl_dir, 'tk8.6'))

import tkinter as tk
from tkinter import ttk, messagebox
from game.player import Player
from game.database import init_database, migrate_from_txt


class LoginDialog:
    """登录/注册对话框"""

    def __init__(self):
        self.player = None       # 登录成功后的 Player 对象
        self._result = None      # 对话框结果

    def show(self):
        """显示登录对话框，返回 Player 对象或 None"""
        init_database()
        migrate_from_txt()

        self.root = tk.Tk()
        self.root.title("贪吃蛇游戏 - 登录")
        self.root.resizable(False, False)

        # 窗口居中
        window_w, window_h = 380, 320
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - window_w) // 2
        y = (screen_h - window_h) // 2
        self.root.geometry(f"{window_w}x{window_h}+{x}+{y}")

        # 设置主题色
        self.root.configure(bg="#1e1e2e")

        self._build_login_ui()
        self.root.mainloop()

        return self.player

    # ==================== 登录界面 ====================

    def _build_login_ui(self):
        """构建登录界面"""
        self._clear_window()

        # 标题
        tk.Label(self.root, text="贪吃蛇游戏", font=("Microsoft YaHei", 20, "bold"),
                 fg="#ffc800", bg="#1e1e2e").pack(pady=(25, 5))
        tk.Label(self.root, text="SNAKE GAME", font=("Microsoft YaHei", 10),
                 fg="#888", bg="#1e1e2e").pack(pady=(0, 20))

        # 输入框容器
        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(pady=5)

        # 用户名
        tk.Label(frame, text="用户名:", font=("Microsoft YaHei", 11),
                 fg="#ddd", bg="#1e1e2e").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=8)
        self.login_username = tk.Entry(frame, width=20, font=("Microsoft YaHei", 11),
                                        bg="#2d2d3d", fg="#eee", insertbackground="#eee",
                                        relief="flat", highlightthickness=1,
                                        highlightcolor="#ffc800", highlightbackground="#444")
        self.login_username.grid(row=0, column=1, pady=8, ipady=4)

        # 密码
        tk.Label(frame, text="密  码:", font=("Microsoft YaHei", 11),
                 fg="#ddd", bg="#1e1e2e").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=8)
        self.login_password = tk.Entry(frame, width=20, font=("Microsoft YaHei", 11),
                                        bg="#2d2d3d", fg="#eee", insertbackground="#eee",
                                        show="*", relief="flat", highlightthickness=1,
                                        highlightcolor="#ffc800", highlightbackground="#444")
        self.login_password.grid(row=1, column=1, pady=8, ipady=4)

        # 按钮容器
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="登 录", font=("Microsoft YaHei", 11, "bold"),
                  width=10, bg="#28784c", fg="white", activebackground="#309060",
                  activeforeground="white", relief="flat", cursor="hand2",
                  command=self._do_login).pack(side="left", padx=8)

        tk.Button(btn_frame, text="注 册", font=("Microsoft YaHei", 11, "bold"),
                  width=10, bg="#3c3c5c", fg="white", activebackground="#4c4c6c",
                  activeforeground="white", relief="flat", cursor="hand2",
                  command=self._show_register).pack(side="left", padx=8)

        # 提示
        tk.Label(self.root, text="输入用户名和密码后点击登录", font=("Microsoft YaHei", 9),
                 fg="#666", bg="#1e1e2e").pack(pady=(5, 0))

        # 绑定回车键
        self.login_password.bind("<Return>", lambda e: self._do_login())
        self.login_username.bind("<Return>", lambda e: self.login_password.focus_set())

        # 默认焦点
        self.login_username.focus_set()

    def _do_login(self):
        """执行登录"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "用户名和密码不能为空", parent=self.root)
            return

        player = Player()
        success, msg = player.login(username, password)
        if success:
            self.player = player
            self.root.destroy()
        else:
            messagebox.showerror("登录失败", msg, parent=self.root)

    # ==================== 注册界面 ====================

    def _show_register(self):
        """切换到注册界面"""
        self._clear_window()
        self.root.title("贪吃蛇游戏 - 注册")

        # 标题
        tk.Label(self.root, text="用户注册", font=("Microsoft YaHei", 18, "bold"),
                 fg="#ffc800", bg="#1e1e2e").pack(pady=(25, 20))

        # 输入框容器
        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(pady=5)

        # 用户名
        tk.Label(frame, text="用户名:", font=("Microsoft YaHei", 11),
                 fg="#ddd", bg="#1e1e2e").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=6)
        self.reg_username = tk.Entry(frame, width=20, font=("Microsoft YaHei", 11),
                                      bg="#2d2d3d", fg="#eee", insertbackground="#eee",
                                      relief="flat", highlightthickness=1,
                                      highlightcolor="#ffc800", highlightbackground="#444")
        self.reg_username.grid(row=0, column=1, pady=6, ipady=4)

        # 密码
        tk.Label(frame, text="密  码:", font=("Microsoft YaHei", 11),
                 fg="#ddd", bg="#1e1e2e").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
        self.reg_password = tk.Entry(frame, width=20, font=("Microsoft YaHei", 11),
                                      bg="#2d2d3d", fg="#eee", insertbackground="#eee",
                                      show="*", relief="flat", highlightthickness=1,
                                      highlightcolor="#ffc800", highlightbackground="#444")
        self.reg_password.grid(row=1, column=1, pady=6, ipady=4)

        # 确认密码
        tk.Label(frame, text="确认密码:", font=("Microsoft YaHei", 11),
                 fg="#ddd", bg="#1e1e2e").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
        self.reg_password_confirm = tk.Entry(frame, width=20, font=("Microsoft YaHei", 11),
                                              bg="#2d2d3d", fg="#eee", insertbackground="#eee",
                                              show="*", relief="flat", highlightthickness=1,
                                              highlightcolor="#ffc800", highlightbackground="#444")
        self.reg_password_confirm.grid(row=2, column=1, pady=6, ipady=4)

        # 按钮容器
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="确认注册", font=("Microsoft YaHei", 11, "bold"),
                  width=10, bg="#28784c", fg="white", activebackground="#309060",
                  activeforeground="white", relief="flat", cursor="hand2",
                  command=self._do_register).pack(side="left", padx=8)

        tk.Button(btn_frame, text="返 回", font=("Microsoft YaHei", 11, "bold"),
                  width=10, bg="#3c3c5c", fg="white", activebackground="#4c4c6c",
                  activeforeground="white", relief="flat", cursor="hand2",
                  command=self._build_login_ui).pack(side="left", padx=8)

        # 提示
        tk.Label(self.root, text="用户名和密码至少3个字符", font=("Microsoft YaHei", 9),
                 fg="#666", bg="#1e1e2e").pack(pady=(5, 0))

        # 绑定回车键
        self.reg_password_confirm.bind("<Return>", lambda e: self._do_register())
        self.reg_username.focus_set()

    def _do_register(self):
        """执行注册"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_password_confirm.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "用户名和密码不能为空", parent=self.root)
            return

        if password != confirm:
            messagebox.showwarning("提示", "两次密码不一致", parent=self.root)
            return

        player = Player()
        success, msg = player.register(username, password)
        if success:
            self.player = player
            self.root.destroy()
        else:
            messagebox.showerror("注册失败", msg, parent=self.root)

    # ==================== 工具方法 ====================

    def _clear_window(self):
        """清空窗口所有控件"""
        for widget in self.root.winfo_children():
            widget.destroy()


def show_login_dialog():
    """显示登录对话框的便捷函数，返回 Player 对象或 None"""
    dialog = LoginDialog()
    return dialog.show()
