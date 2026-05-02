# -*- coding: utf-8 -*-
"""
游戏日志类
处理游戏日志的记录和读取，使用SQLite数据库
"""

import os
from datetime import datetime
from game.database import get_connection, init_database


class GameLog:
    """游戏日志类（SQLite版）"""

    def __init__(self):
        self.log_id = 0
        self.user_id = 0
        self.username = ""
        self.start_time = ""
        self.duration = 0  # 秒
        self.score = 0
        self.difficulty = "normal"
        self.wall_mode = 0
        # 确保数据库已初始化
        init_database()

    def save_log(self):
        """保存日志到数据库"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO game_logs (user_id, username, start_time, duration, score, difficulty, wall_mode) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (self.user_id, self.username, self.start_time, self.duration, self.score, self.difficulty, self.wall_mode)
        )
        conn.commit()
        self.log_id = cursor.lastrowid
        conn.close()

    def get_user_logs(self, username):
        """获取指定用户的日志"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM game_logs WHERE username = ? ORDER BY start_time DESC',
            (username,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_logs(self):
        """获取所有日志，按时间倒序"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM game_logs ORDER BY start_time DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def format_duration(seconds):
        """格式化时长"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"
