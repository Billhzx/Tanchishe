# -*- coding: utf-8 -*-
"""
数据库模块
使用SQLite3管理用户数据和游戏日志
"""

import sqlite3
import os
import sys


def _get_app_dir():
    """获取应用根目录（exe所在目录 或 项目根目录）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，exe 所在目录
        return os.path.dirname(sys.executable)
    return os.path.join(os.path.dirname(__file__), '..')


APP_DIR = _get_app_dir()
DB_PATH = os.path.join(APP_DIR, 'snake_db.sqlite')


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库，创建表结构"""
    conn = get_connection()
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            reg_time TEXT NOT NULL
        )
    ''')

    # 创建游戏日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            difficulty TEXT DEFAULT 'normal',
            wall_mode INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


def migrate_from_txt():
    """从txt文件迁移数据到SQLite"""
    init_database()
    conn = get_connection()
    cursor = conn.cursor()

    # 迁移用户数据
    users_file = os.path.join(APP_DIR, 'users.txt')
    if os.path.exists(users_file):
        with open(users_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    try:
                        cursor.execute(
                            'INSERT OR IGNORE INTO users (id, username, password, reg_time) VALUES (?, ?, ?, ?)',
                            (int(parts[2]), parts[0], parts[1], parts[3])
                        )
                    except (ValueError, sqlite3.IntegrityError):
                        continue

    # 迁移日志数据
    log_file = os.path.join(APP_DIR, 'gamelog.txt')
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 6:
                    try:
                        cursor.execute(
                            'INSERT OR IGNORE INTO game_logs (id, user_id, username, start_time, duration, score) VALUES (?, ?, ?, ?, ?, ?)',
                            (int(parts[0]), int(parts[1]), parts[2], parts[3], int(parts[4]), int(parts[5]))
                        )
                    except (ValueError, sqlite3.IntegrityError):
                        continue

    conn.commit()
    conn.close()
