# -*- coding: utf-8 -*-
"""
玩家类
处理用户注册、登录，使用SQLite数据库
"""

import os
from datetime import datetime
from game.database import get_connection, init_database


class Player:
    """玩家类，管理用户注册和登录（SQLite版）"""

    def __init__(self, username="", password="", user_id=0, reg_time=""):
        self.username = username
        self.password = password
        self.user_id = user_id
        self.reg_time = reg_time
        self.is_logged_in = False
        # 确保数据库已初始化
        init_database()

    def register(self, username, password):
        """注册新用户"""
        if not username or not password:
            return False, "用户名和密码不能为空"

        if len(username) < 3:
            return False, "用户名至少3个字符"

        if len(password) < 3:
            return False, "密码至少3个字符"

        conn = get_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "用户名已存在"

        # 插入新用户
        reg_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            'INSERT INTO users (username, password, reg_time) VALUES (?, ?, ?)',
            (username, password, reg_time)
        )
        conn.commit()

        # 获取新用户信息
        user_id = cursor.lastrowid
        conn.close()

        self.username = username
        self.password = password
        self.user_id = user_id
        self.reg_time = reg_time
        self.is_logged_in = True

        return True, "注册成功"

    def login(self, username, password):
        """登录用户"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, username, password, reg_time FROM users WHERE username = ? AND password = ?',
            (username, password)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            self.username = row['username']
            self.password = row['password']
            self.user_id = row['id']
            self.reg_time = row['reg_time']
            self.is_logged_in = True
            return True, "登录成功"

        return False, "用户名或密码错误"

    def logout(self):
        """登出"""
        self.username = ""
        self.password = ""
        self.user_id = 0
        self.reg_time = ""
        self.is_logged_in = False

    def get_info_text(self):
        """获取玩家信息用于显示"""
        if self.is_logged_in:
            return f"玩家: {self.username}"
        return "未登录"

    def get_total_games(self):
        """获取玩家总游戏次数"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as cnt FROM game_logs WHERE user_id = ?', (self.user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    def get_high_score(self):
        """获取玩家最高分"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(score) as hs FROM game_logs WHERE user_id = ?', (self.user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['hs'] if row and row['hs'] else 0
