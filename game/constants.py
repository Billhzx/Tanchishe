# -*- coding: utf-8 -*-
"""
常量配置文件
定义游戏窗口、颜色、速度、难度等常量
"""

import os

# ==================== 窗口配置 ====================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60  # 帧率

# ==================== 网格配置 ====================
GRID_SIZE = 20        # 每格像素大小
GRID_WIDTH = 20       # 网格列数（游戏区域宽度）
GRID_HEIGHT = 20      # 网格行数（游戏区域高度）
GRID_OFFSET_X = 50    # 游戏区域左偏移
GRID_OFFSET_Y = 50    # 游戏区域上偏移

# ==================== 信息栏配置 ====================
INFO_PANEL_X = GRID_OFFSET_X + GRID_WIDTH * GRID_SIZE + 20  # 信息栏X位置
INFO_PANEL_WIDTH = 180                                          # 信息栏宽度

# ==================== 颜色配置 ====================
COLOR_BG = (30, 30, 40)                    # 背景色（深灰蓝）
COLOR_GRID = (50, 50, 60)                   # 网格线颜色
COLOR_SNAKE_HEAD = (0, 200, 100)            # 蛇头颜色（亮绿）
COLOR_SNAKE_BODY = (0, 180, 80)             # 蛇身颜色（绿）
COLOR_FOOD = (255, 80, 80)                  # 普通食物颜色（红）
COLOR_FOOD_GOLD = (255, 215, 0)             # 金色食物颜色（金色）
COLOR_WALL = (100, 100, 120)                # 墙壁颜色
COLOR_TEXT = (220, 220, 220)                # 文字颜色
COLOR_TEXT_HIGHLIGHT = (255, 200, 0)        # 高亮文字颜色（金色）
COLOR_TEXT_RED = (255, 80, 80)              # 红色提示文字
COLOR_TEXT_GREEN = (80, 255, 80)            # 绿色提示文字
COLOR_BTN_NORMAL = (60, 60, 80)             # 按钮正常颜色
COLOR_BTN_HOVER = (80, 80, 110)            # 按钮悬停颜色
COLOR_BTN_ACTIVE = (100, 100, 140)          # 按钮按下颜色
COLOR_BTN_GREEN = (40, 120, 60)             # 绿色按钮（确认）
COLOR_BTN_GREEN_HOVER = (50, 150, 75)       # 绿色按钮悬停
COLOR_BTN_RED = (140, 50, 50)               # 红色按钮（危险）
COLOR_BTN_RED_HOVER = (170, 65, 65)         # 红色按钮悬停
COLOR_INPUT_BG = (45, 45, 60)               # 输入框背景
COLOR_PANEL_BG = (40, 40, 55)              # 面板背景
COLOR_GOLD_GLOW = (255, 215, 0, 80)         # 金色光晕

# ==================== 难度配置 ====================
DIFFICULTY_EASY = 'easy'
DIFFICULTY_NORMAL = 'normal'
DIFFICULTY_HARD = 'hard'

DIFFICULTY_CONFIG = {
    DIFFICULTY_EASY: {
        'label': '简单',
        'initial_speed': 10,    # 帧计数阈值（越大越慢）
        'speed_increment': 0.3, # 每次加速量
        'min_speed': 5,         # 最大速度上限
        'score_per_food': 10,   # 每个食物得分
        'color': COLOR_TEXT_GREEN,
    },
    DIFFICULTY_NORMAL: {
        'label': '普通',
        'initial_speed': 8,
        'speed_increment': 0.5,
        'min_speed': 3,
        'score_per_food': 10,
        'color': COLOR_TEXT_HIGHLIGHT,
    },
    DIFFICULTY_HARD: {
        'label': '困难',
        'initial_speed': 5,
        'speed_increment': 0.8,
        'min_speed': 2,
        'score_per_food': 10,
        'color': COLOR_TEXT_RED,
    },
}

# ==================== 游戏速度配置（默认/兼容用） ====================
INITIAL_SPEED = 8      # 初始速度（每帧刷新次数，越小越快）
SPEED_INCREMENT = 0.5  # 每吃一个食物速度增量

# ==================== 金色食物配置 ====================
GOLD_FOOD_SCORE = 30           # 金色食物得分
GOLD_FOOD_CHANCE = 0.15        # 金色食物出现概率（15%）
GOLD_FOOD_DURATION = 8.0       # 金色食物存在时间（秒）
GOLD_FOOD_FLASH_RATE = 0.3     # 金色食物闪烁速率（秒）

# ==================== 方向配置 ====================
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# ==================== 方向键值 ====================
KEY_MAP = {
    'up': 0,
    'down': 1,
    'left': 2,
    'right': 3
}

# ==================== 字体配置 ====================
FONT_SIZE_TITLE = 36
FONT_SIZE_MENU = 24
FONT_SIZE_INFO = 18
FONT_SIZE_HINT = 14

# ==================== 状态常量 ====================
STATE_LOGIN = 'login'
STATE_REGISTER = 'register'
STATE_MENU = 'menu'
STATE_DIFFICULTY = 'difficulty'    # 新增：难度选择
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_GAMEOVER = 'gameover'
STATE_LOG = 'log'

# ==================== 音效文件路径 ====================
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'resources', 'sounds')
SOUND_EAT = os.path.join(SOUNDS_DIR, 'eat.wav')
SOUND_GOLD = os.path.join(SOUNDS_DIR, 'gold.wav')
SOUND_GAMEOVER = os.path.join(SOUNDS_DIR, 'gameover.wav')
SOUND_CLICK = os.path.join(SOUNDS_DIR, 'click.wav')
