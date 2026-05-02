# -*- coding: utf-8 -*-
"""
贪吃蛇游戏主程序 V4
Python + Pygame 版本
增强功能：SQLite数据库、难度选择、穿墙模式、UI美化、音效、金色限时食物
"""

import pygame
import sys
import random
import os
import time as time_module
from datetime import datetime
from game.constants import *
from game.player import Player
from game.game_log import GameLog
from game.database import init_database, migrate_from_txt
from game.sound_manager import SoundManager


class Button:
    """增强按钮类 - 支持自定义颜色、圆角、悬停动画"""

    def __init__(self, x, y, width, height, text, font_size=24,
                 color_normal=COLOR_BTN_NORMAL, color_hover=COLOR_BTN_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.is_hovered = False
        self.press_scale = 1.0  # 按下缩放效果

    def draw(self, surface, fonts):
        # 选择颜色
        color = self.color_hover if self.is_hovered else self.color_normal

        # 绘制按钮阴影
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(surface, (20, 20, 30), shadow_rect, border_radius=8)

        # 绘制按钮主体
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        # 边框
        border_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

        # 文字
        font = fonts.get('menu', pygame.font.Font(None, self.font_size))
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class InputBox:
    """输入框类"""

    def __init__(self, x, y, width, height, placeholder="", hidden=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = None
        self.hidden = hidden

    def draw(self, surface):
        color = COLOR_TEXT_HIGHLIGHT if self.active else COLOR_INPUT_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        border_color = COLOR_TEXT_HIGHLIGHT if self.active else (80, 80, 100)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)

        # 密码模式显示星号
        display_text = "*" * len(self.text) if self.hidden else self.text
        placeholder_text = "password" if self.hidden else self.placeholder

        if display_text:
            text_surf = self.font.render(display_text, True, COLOR_TEXT)
        else:
            text_surf = self.font.render(placeholder_text, True, (120, 120, 140))
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))

        # 光标闪烁
        if self.active and display_text:
            cursor_x = self.rect.x + 10 + self.font.size(display_text)[0]
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.line(surface, COLOR_TEXT,
                                 (cursor_x + 2, self.rect.y + 6),
                                 (cursor_x + 2, self.rect.y + self.rect.height - 6), 2)

    def activate(self):
        self.active = True
        pygame.key.start_text_input()

    def deactivate(self):
        self.active = False
        pygame.key.stop_text_input()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.activate()
            else:
                self.deactivate()

        if event.type == pygame.TEXTINPUT and self.active:
            self.text += event.text

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True


class SnakeGame:
    """贪吃蛇游戏主类 V4"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("贪吃蛇游戏 V4")

        # 创建窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # 初始化字体
        self.fonts = self._init_fonts()

        # 初始化数据库（自动迁移txt数据）
        init_database()
        migrate_from_txt()

        # 初始化音效
        self.sound = SoundManager()
        self.sound.init()

        # 初始化游戏对象
        self.player = Player()
        self.game_log = GameLog()

        # 游戏状态
        self.state = STATE_LOGIN

        # 游戏数据
        self.snake = []
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.food = (0, 0)
        self.gold_food = None          # 金色食物位置
        self.gold_food_timer = 0       # 金色食物出现时间
        self.gold_food_flash = False   # 金色食物闪烁状态
        self.gold_food_flash_timer = 0
        self.score = 0
        self.speed = INITIAL_SPEED
        self.frame_counter = 0
        self.game_start_time = None
        self.game_duration = 0

        # 难度和模式
        self.difficulty = DIFFICULTY_NORMAL
        self.wall_mode = False          # 穿墙模式

        # 粒子效果
        self.particles = []

        # 分数飘字效果
        self.score_popups = []

        # 登录界面组件
        self.login_input_username = InputBox(300, 250, 200, 40, "请输入用户名")
        self.login_input_username.font = self.fonts['info']
        self.login_input_password = InputBox(300, 320, 200, 40, "请输入密码", hidden=True)
        self.login_input_password.font = self.fonts['info']

        # 注册界面组件
        self.reg_input_username = InputBox(300, 230, 200, 40, "请输入用户名")
        self.reg_input_username.font = self.fonts['info']
        self.reg_input_password = InputBox(300, 290, 200, 40, "请输入密码", hidden=True)
        self.reg_input_password.font = self.fonts['info']
        self.reg_input_password_confirm = InputBox(300, 350, 200, 40, "请确认密码", hidden=True)
        self.reg_input_password_confirm.font = self.fonts['info']

        # 按钮
        self.login_btn = Button(300, 400, 200, 50, "登 录")
        self.register_btn = Button(300, 470, 200, 50, "注 册")
        self.reg_back_btn = Button(300, 420, 200, 50, "返 回")
        self.reg_submit_btn = Button(300, 490, 200, 50, "确认注册",
                                     color_normal=COLOR_BTN_GREEN, color_hover=COLOR_BTN_GREEN_HOVER)

        # 主菜单按钮
        self.menu_btns = [
            Button(300, 270, 200, 50, "开始游戏",
                   color_normal=COLOR_BTN_GREEN, color_hover=COLOR_BTN_GREEN_HOVER),
            Button(300, 340, 200, 50, "查看日志"),
            Button(300, 410, 200, 50, "退出游戏",
                   color_normal=COLOR_BTN_RED, color_hover=COLOR_BTN_RED_HOVER),
        ]

        # 难度选择按钮
        self.difficulty_btns = [
            Button(300, 220, 200, 50, "简 单",
                   color_normal=(40, 100, 50), color_hover=(50, 130, 65)),
            Button(300, 290, 200, 50, "普 通",
                   color_normal=(80, 80, 40), color_hover=(110, 110, 55)),
            Button(300, 360, 200, 50, "困 难",
                   color_normal=(120, 40, 40), color_hover=(150, 55, 55)),
        ]
        self.wall_mode_btn = Button(300, 440, 200, 50, "穿墙模式: 关")
        self.diff_back_btn = Button(300, 510, 200, 50, "返 回")

        # 游戏结束按钮
        self.gameover_btns = [
            Button(300, 400, 200, 50, "返回主菜单"),
        ]

        # 日志界面按钮
        self.log_btns = [
            Button(300, 530, 200, 50, "返回主菜单"),
        ]

        # 消息提示
        self.message = ""
        self.message_timer = 0

        # 日志显示
        self.log_entries = []

    def _init_fonts(self):
        """初始化字体"""
        font_path = os.path.join(os.path.dirname(__file__), 'game', 'resources', 'msyh.ttc')
        fonts = {}
        for size_key, size in [('title', FONT_SIZE_TITLE), ('menu', FONT_SIZE_MENU),
                                ('info', FONT_SIZE_INFO), ('hint', FONT_SIZE_HINT)]:
            try:
                fonts[size_key] = pygame.font.Font(font_path, size)
            except Exception:
                fonts[size_key] = pygame.font.Font(None, size)
        return fonts

    def show_message(self, msg):
        """显示消息提示"""
        self.message = msg
        self.message_timer = 120

    def draw_text(self, text, pos, size='info', color=COLOR_TEXT):
        """绘制文本"""
        surf = self.fonts[size].render(text, True, color)
        self.screen.blit(surf, pos)

    def draw_text_center(self, text, y, size='info', color=COLOR_TEXT):
        """居中绘制文本"""
        surf = self.fonts[size].render(text, True, color)
        x = (WINDOW_WIDTH - surf.get_width()) // 2
        self.screen.blit(surf, (x, y))

    def draw_panel(self, x, y, width, height, title=""):
        """绘制面板"""
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (x, y, width, height), border_radius=10)
        # 面板边框
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=10)
        if title:
            self.draw_text(title, (x + 10, y + 10), 'info', COLOR_TEXT_HIGHLIGHT)

    def add_particles(self, x, y, color, count=8):
        """添加粒子效果"""
        for _ in range(count):
            self.particles.append({
                'x': float(x),
                'y': float(y),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': random.randint(10, 25),
                'color': color,
                'size': random.randint(2, 5),
            })

    def add_score_popup(self, x, y, score, color=COLOR_TEXT_HIGHLIGHT):
        """添加分数飘字"""
        self.score_popups.append({
            'x': x,
            'y': float(y),
            'score': f"+{score}",
            'life': 40,
            'color': color,
        })

    def update_particles(self):
        """更新粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['size'] = max(0, p['size'] - 0.1)
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw_particles(self):
        """绘制粒子"""
        for p in self.particles:
            alpha = min(255, p['life'] * 15)
            color = p['color']
            pygame.draw.circle(self.screen, color, (int(p['x']), int(p['y'])), int(p['size']))

    def update_score_popups(self):
        """更新分数飘字"""
        for sp in self.score_popups[:]:
            sp['y'] -= 1.5
            sp['life'] -= 1
            if sp['life'] <= 0:
                self.score_popups.remove(sp)

    def draw_score_popups(self):
        """绘制分数飘字"""
        for sp in self.score_popups:
            alpha = min(255, sp['life'] * 8)
            surf = self.fonts['info'].render(sp['score'], True, sp['color'])
            self.screen.blit(surf, (sp['x'], int(sp['y'])))

    # ==================== 登录/注册界面 ====================

    def draw_login_screen(self):
        """绘制登录界面"""
        self.screen.fill(COLOR_BG)

        # 装饰：蛇形图案
        for i in range(5):
            x = 200 + i * 25
            y = 40 + abs(i - 2) * 8
            color = COLOR_SNAKE_HEAD if i == 0 else (0, 180 - i * 30, 80 - i * 15)
            pygame.draw.circle(self.screen, color, (x, y), 8)

        self.draw_text_center("贪吃蛇游戏", 70, 'title', COLOR_TEXT_HIGHLIGHT)
        self.draw_text_center("用户登录", 140, 'menu')

        self.login_input_username.draw(self.screen)
        self.login_input_password.draw(self.screen)

        self.login_btn.draw(self.screen, self.fonts)
        self.register_btn.draw(self.screen, self.fonts)

        if self.message:
            self.draw_text(self.message, (250, 480), 'hint', COLOR_TEXT_RED)

    def draw_register_screen(self):
        """绘制注册界面"""
        self.screen.fill(COLOR_BG)
        self.draw_text_center("用户注册", 100, 'menu')

        self.reg_input_username.draw(self.screen)
        self.reg_input_password.draw(self.screen)
        self.reg_input_password_confirm.draw(self.screen)

        self.reg_submit_btn.draw(self.screen, self.fonts)
        self.reg_back_btn.draw(self.screen, self.fonts)

        if self.message:
            self.draw_text(self.message, (250, 450), 'hint', COLOR_TEXT_RED)

    def handle_login_input(self, event):
        """处理登录界面输入"""
        self.login_input_username.handle_event(event)
        self.login_input_password.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.login_btn.is_clicked(pos):
                self.sound.play('click')
                success, msg = self.player.login(
                    self.login_input_username.text,
                    self.login_input_password.text
                )
                if success:
                    self.login_input_username.deactivate()
                    self.login_input_password.deactivate()
                    self.state = STATE_MENU
                    self.show_message("登录成功！")
                else:
                    self.show_message(msg)

            elif self.register_btn.is_clicked(pos):
                self.sound.play('click')
                self.login_input_username.deactivate()
                self.login_input_password.deactivate()
                self.state = STATE_REGISTER
                self.login_input_username.text = ""
                self.login_input_password.text = ""
                self.message = ""

    def handle_register_input(self, event):
        """处理注册界面输入"""
        self.reg_input_username.handle_event(event)
        self.reg_input_password.handle_event(event)
        self.reg_input_password_confirm.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.reg_submit_btn.is_clicked(pos):
                self.sound.play('click')
                username = self.reg_input_username.text
                password = self.reg_input_password.text
                confirm = self.reg_input_password_confirm.text

                if not username or not password:
                    self.show_message("用户名和密码不能为空")
                elif password != confirm:
                    self.show_message("两次密码不一致")
                else:
                    success, msg = self.player.register(username, password)
                    if success:
                        self.reg_input_username.deactivate()
                        self.reg_input_password.deactivate()
                        self.reg_input_password_confirm.deactivate()
                        self.state = STATE_MENU
                        self.show_message("注册成功！")
                    else:
                        self.show_message(msg)

            elif self.reg_back_btn.is_clicked(pos):
                self.sound.play('click')
                self.reg_input_username.deactivate()
                self.reg_input_password.deactivate()
                self.reg_input_password_confirm.deactivate()
                self.state = STATE_LOGIN
                self.reg_input_username.text = ""
                self.reg_input_password.text = ""
                self.reg_input_password_confirm.text = ""
                self.message = ""

    # ==================== 主菜单界面 ====================

    def draw_menu_screen(self):
        """绘制主菜单"""
        self.screen.fill(COLOR_BG)

        # 装饰蛇形
        for i in range(8):
            x = 150 + i * 22
            y = 55 + int(10 * math.sin(i * 0.8 + pygame.time.get_ticks() * 0.003))
            color = COLOR_SNAKE_HEAD if i == 0 else (0, max(0, 180 - i * 20), max(0, 80 - i * 10))
            pygame.draw.circle(self.screen, color, (x, y), 7)

        self.draw_text_center("贪吃蛇游戏", 70, 'title', COLOR_TEXT_HIGHLIGHT)
        self.draw_text_center("SNAKE GAME", 120, 'info')

        # 玩家信息面板
        self.draw_panel(250, 165, 300, 75)
        self.draw_text(f"欢迎, {self.player.username}", (270, 178), 'info', COLOR_TEXT)
        total_games = self.player.get_total_games()
        high_score = self.player.get_high_score()
        self.draw_text(f"总场次: {total_games}  最高分: {high_score}", (270, 205), 'hint', COLOR_TEXT_HIGHLIGHT)

        for btn in self.menu_btns:
            btn.draw(self.screen, self.fonts)

        self.draw_text_center("方向键移动 | P键暂停 | ESC退出", 490, 'hint')

        # 音效开关
        sound_status = "音效: 开" if self.sound.enabled else "音效: 关"
        self.draw_text(sound_status, (15, 575), 'hint', COLOR_TEXT)
        self.draw_text("M键切换音效", (15, 555), 'hint', (100, 100, 120))

    def handle_menu_input(self, event):
        """处理主菜单输入"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.menu_btns[0].is_clicked(pos):
                self.sound.play('click')
                self.state = STATE_DIFFICULTY
            elif self.menu_btns[1].is_clicked(pos):
                self.sound.play('click')
                self.state = STATE_LOG
                self.log_entries = self.game_log.get_all_logs()
            elif self.menu_btns[2].is_clicked(pos):
                self.sound.play('click')
                self.player.logout()
                self.state = STATE_LOGIN

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.sound.toggle()

    # ==================== 难度选择界面 ====================

    def draw_difficulty_screen(self):
        """绘制难度选择界面"""
        self.screen.fill(COLOR_BG)
        self.draw_text_center("选择难度", 100, 'title', COLOR_TEXT_HIGHLIGHT)

        # 难度说明
        configs = DIFFICULTY_CONFIG
        labels_y = [232, 302, 372]
        for i, (key, cfg) in enumerate(configs.items()):
            info = f"{cfg['label']} - 速度x{cfg['initial_speed']} 加速x{cfg['speed_increment']}"
            self.draw_text(info, (530, labels_y[i]), 'hint', cfg['color'])

        for btn in self.difficulty_btns:
            btn.draw(self.screen, self.fonts)

        # 穿墙模式按钮
        wall_text = "穿墙模式: 开" if self.wall_mode else "穿墙模式: 关"
        self.wall_mode_btn.text = wall_text
        if self.wall_mode:
            self.wall_mode_btn.color_normal = (40, 100, 50)
            self.wall_mode_btn.color_hover = (50, 130, 65)
        else:
            self.wall_mode_btn.color_normal = COLOR_BTN_NORMAL
            self.wall_mode_btn.color_hover = COLOR_BTN_HOVER
        self.wall_mode_btn.draw(self.screen, self.fonts)

        self.diff_back_btn.draw(self.screen, self.fonts)

    def handle_difficulty_input(self, event):
        """处理难度选择输入"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            difficulty_keys = [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD]
            for i, btn in enumerate(self.difficulty_btns):
                if btn.is_clicked(pos):
                    self.sound.play('click')
                    self.difficulty = difficulty_keys[i]
                    self.start_new_game()
                    return

            if self.wall_mode_btn.is_clicked(pos):
                self.sound.play('click')
                self.wall_mode = not self.wall_mode

            elif self.diff_back_btn.is_clicked(pos):
                self.sound.play('click')
                self.state = STATE_MENU

    # ==================== 游戏界面 ====================

    def start_new_game(self):
        """开始新游戏"""
        config = DIFFICULTY_CONFIG[self.difficulty]
        self.state = STATE_PLAYING
        self.score = 0
        self.speed = config['initial_speed']
        self.frame_counter = 0
        self.game_start_time = datetime.now()
        self.gold_food = None
        self.gold_food_timer = 0
        self.particles = []
        self.score_popups = []

        # 初始化蛇
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y)
        ]

        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.spawn_food()

    def spawn_food(self):
        """生成普通食物"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake and (x, y) != self.gold_food:
                self.food = (x, y)
                break

    def try_spawn_gold_food(self):
        """尝试生成金色食物"""
        if self.gold_food is not None:
            return
        if random.random() < GOLD_FOOD_CHANCE:
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if (x, y) not in self.snake and (x, y) != self.food:
                    self.gold_food = (x, y)
                    self.gold_food_timer = time_module.time()
                    break

    def draw_game_screen(self):
        """绘制游戏界面"""
        self.screen.fill(COLOR_BG)

        # 游戏区域背景
        game_rect = pygame.Rect(
            GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2,
            GRID_WIDTH * GRID_SIZE + 4, GRID_HEIGHT * GRID_SIZE + 4
        )
        pygame.draw.rect(self.screen, (20, 20, 30), game_rect, border_radius=4)

        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            px = GRID_OFFSET_X + x * GRID_SIZE
            pygame.draw.line(self.screen, COLOR_GRID,
                             (px, GRID_OFFSET_Y),
                             (px, GRID_OFFSET_Y + GRID_HEIGHT * GRID_SIZE))
        for y in range(GRID_HEIGHT + 1):
            py = GRID_OFFSET_Y + y * GRID_SIZE
            pygame.draw.line(self.screen, COLOR_GRID,
                             (GRID_OFFSET_X, py),
                             (GRID_OFFSET_X + GRID_WIDTH * GRID_SIZE, py))

        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            px = GRID_OFFSET_X + x * GRID_SIZE + 1
            py = GRID_OFFSET_Y + y * GRID_SIZE + 1
            rect = pygame.Rect(px, py, GRID_SIZE - 2, GRID_SIZE - 2)

            if i == 0:
                # 蛇头
                pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD, rect, border_radius=4)
                # 眼睛
                eye_size = 3
                if self.direction == DIR_RIGHT:
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + GRID_SIZE - 5, py + 5), eye_size)
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + GRID_SIZE - 5, py + GRID_SIZE - 6), eye_size)
                elif self.direction == DIR_LEFT:
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + 5, py + 5), eye_size)
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + 5, py + GRID_SIZE - 6), eye_size)
                elif self.direction == DIR_UP:
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + 5, py + 5), eye_size)
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + GRID_SIZE - 6, py + 5), eye_size)
                else:
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + 5, py + GRID_SIZE - 5), eye_size)
                    pygame.draw.circle(self.screen, (0, 0, 0), (px + GRID_SIZE - 6, py + GRID_SIZE - 5), eye_size)
            else:
                # 蛇身渐变
                body_color = (0, max(0, 180 - i * 5), max(0, 80 - i * 3))
                pygame.draw.rect(self.screen, body_color, rect, border_radius=3)

        # 绘制普通食物
        fx = GRID_OFFSET_X + self.food[0] * GRID_SIZE + 1
        fy = GRID_OFFSET_Y + self.food[1] * GRID_SIZE + 1
        food_rect = pygame.Rect(fx, fy, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(self.screen, COLOR_FOOD, food_rect, border_radius=10)

        # 绘制金色食物
        if self.gold_food is not None:
            # 闪烁效果
            elapsed = time_module.time() - self.gold_food_timer
            remaining = max(0, GOLD_FOOD_DURATION - elapsed)
            flash = int(elapsed / GOLD_FOOD_FLASH_RATE) % 2 == 0

            # 快消失时加速闪烁
            if remaining < 3:
                flash = int(elapsed / 0.1) % 2 == 0

            if flash:
                gx = GRID_OFFSET_X + self.gold_food[0] * GRID_SIZE
                gy = GRID_OFFSET_Y + self.gold_food[1] * GRID_SIZE
                # 金色光晕
                glow_surf = pygame.Surface((GRID_SIZE + 10, GRID_SIZE + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 215, 0, 60), (0, 0, GRID_SIZE + 10, GRID_SIZE + 10), border_radius=12)
                self.screen.blit(glow_surf, (gx - 5, gy - 5))

                gold_rect = pygame.Rect(gx + 1, gy + 1, GRID_SIZE - 2, GRID_SIZE - 2)
                pygame.draw.rect(self.screen, COLOR_FOOD_GOLD, gold_rect, border_radius=10)

            # 倒计时提示
            if remaining > 0:
                timer_text = f"{remaining:.0f}s"
                self.draw_text(timer_text,
                               (GRID_OFFSET_X + self.gold_food[0] * GRID_SIZE,
                                GRID_OFFSET_Y + self.gold_food[1] * GRID_SIZE - 15),
                               'hint', COLOR_FOOD_GOLD)

        # 绘制粒子
        self.draw_particles()

        # 绘制分数飘字
        self.draw_score_popups()

        # 绘制信息面板
        self.draw_panel(INFO_PANEL_X, GRID_OFFSET_Y, INFO_PANEL_WIDTH, 300, "游戏信息")

        config = DIFFICULTY_CONFIG[self.difficulty]
        self.draw_text(f"玩家: {self.player.username}", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 45), 'info')
        self.draw_text(f"得分: {self.score}", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 75), 'info', COLOR_TEXT_HIGHLIGHT)
        self.draw_text(f"难度: {config['label']}", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 105), 'info', config['color'])
        self.draw_text(f"穿墙: {'开' if self.wall_mode else '关'}", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 135), 'info')

        # 时长
        if self.game_start_time:
            elapsed = (datetime.now() - self.game_start_time).seconds
            self.draw_text(f"时长: {GameLog.format_duration(elapsed)}", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 165), 'info')

        # 操作提示
        self.draw_text("操作提示", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 210), 'info', COLOR_TEXT_HIGHLIGHT)
        self.draw_text("方向键/WASD", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 235), 'hint')
        self.draw_text("P键 暂停", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 255), 'hint')
        self.draw_text("ESC 返回", (INFO_PANEL_X + 15, GRID_OFFSET_Y + 275), 'hint')

        # 暂停覆盖层
        if self.state == STATE_PAUSED:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            self.draw_text_center("游戏暂停", 250, 'title', COLOR_TEXT_HIGHLIGHT)
            self.draw_text_center("按 P 键继续", 310, 'info')

    def update_game(self):
        """更新游戏逻辑"""
        if self.state != STATE_PLAYING:
            return

        # 更新粒子
        self.update_particles()
        self.update_score_popups()

        # 更新金色食物
        if self.gold_food is not None:
            elapsed = time_module.time() - self.gold_food_timer
            if elapsed >= GOLD_FOOD_DURATION:
                self.gold_food = None
                self.gold_food_timer = 0

        # 帧节流控制速度
        self.frame_counter += 1
        if self.frame_counter < self.speed:
            return
        self.frame_counter = 0

        # 更新方向
        self.direction = self.next_direction

        # 计算新头部位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 碰撞检测：墙壁
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            if self.wall_mode:
                # 穿墙模式：从对面出来
                new_x = new_head[0] % GRID_WIDTH
                new_y = new_head[1] % GRID_HEIGHT
                new_head = (new_x, new_y)
            else:
                self.game_over()
                return

        # 碰撞检测：自身
        if new_head in self.snake:
            self.game_over()
            return

        # 移动蛇
        self.snake.insert(0, new_head)

        config = DIFFICULTY_CONFIG[self.difficulty]

        # 检测普通食物
        if new_head == self.food:
            self.score += config['score_per_food']
            self.speed = max(config['min_speed'], self.speed - config['speed_increment'])
            self.sound.play('eat')

            # 粒子效果
            px = GRID_OFFSET_X + self.food[0] * GRID_SIZE + GRID_SIZE // 2
            py = GRID_OFFSET_Y + self.food[1] * GRID_SIZE + GRID_SIZE // 2
            self.add_particles(px, py, COLOR_FOOD)
            self.add_score_popup(px - 10, py - 15, config['score_per_food'])

            self.spawn_food()
            self.try_spawn_gold_food()
        elif self.gold_food and new_head == self.gold_food:
            # 吃到金色食物
            self.score += GOLD_FOOD_SCORE
            self.sound.play('gold')

            px = GRID_OFFSET_X + self.gold_food[0] * GRID_SIZE + GRID_SIZE // 2
            py = GRID_OFFSET_Y + self.gold_food[1] * GRID_SIZE + GRID_SIZE // 2
            self.add_particles(px, py, COLOR_FOOD_GOLD, count=15)
            self.add_score_popup(px - 10, py - 15, GOLD_FOOD_SCORE, COLOR_FOOD_GOLD)

            self.gold_food = None
            self.gold_food_timer = 0
        else:
            self.snake.pop()

    def game_over(self):
        """游戏结束"""
        self.state = STATE_GAMEOVER
        self.sound.play('gameover')

        if self.game_start_time:
            self.game_duration = (datetime.now() - self.game_start_time).seconds

        # 记录日志
        log = GameLog()
        log.user_id = self.player.user_id
        log.username = self.player.username
        log.start_time = self.game_start_time.strftime('%Y-%m-%d %H:%M:%S')
        log.duration = self.game_duration
        log.score = self.score
        log.difficulty = self.difficulty
        log.wall_mode = 1 if self.wall_mode else 0
        log.save_log()

    def handle_game_input(self, event):
        """处理游戏输入"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU
                return

            if event.key == pygame.K_p:
                if self.state == STATE_PLAYING:
                    self.state = STATE_PAUSED
                elif self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                return

            if event.key == pygame.K_m:
                self.sound.toggle()
                return

            if self.state == STATE_PLAYING:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if self.direction != DIR_DOWN:
                        self.next_direction = DIR_UP
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if self.direction != DIR_UP:
                        self.next_direction = DIR_DOWN
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if self.direction != DIR_RIGHT:
                        self.next_direction = DIR_LEFT
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if self.direction != DIR_LEFT:
                        self.next_direction = DIR_RIGHT

    # ==================== 游戏结束界面 ====================

    def draw_gameover_screen(self):
        """绘制游戏结束界面"""
        self.screen.fill(COLOR_BG)

        self.draw_text_center("游戏结束", 100, 'title', COLOR_TEXT_RED)

        # 统计面板
        config = DIFFICULTY_CONFIG[self.difficulty]
        self.draw_panel(230, 160, 340, 200)
        self.draw_text(f"玩家: {self.player.username}", (260, 180), 'info')
        self.draw_text(f"得分: {self.score}", (260, 215), 'info', COLOR_TEXT_HIGHLIGHT)
        self.draw_text(f"时长: {GameLog.format_duration(self.game_duration)}", (260, 250), 'info')
        self.draw_text(f"难度: {config['label']}", (260, 285), 'info', config['color'])
        self.draw_text(f"穿墙: {'开' if self.wall_mode else '关'}", (260, 320), 'info')

        for btn in self.gameover_btns:
            btn.draw(self.screen, self.fonts)

    def handle_gameover_input(self, event):
        """处理游戏结束输入"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.gameover_btns[0].is_clicked(pos):
                self.sound.play('click')
                self.state = STATE_MENU

    # ==================== 日志查看界面 ====================

    def draw_log_screen(self):
        """绘制日志查看界面"""
        self.screen.fill(COLOR_BG)
        self.draw_text_center("游戏日志", 30, 'title', COLOR_TEXT_HIGHLIGHT)

        # 表头
        headers = ["玩家", "难度", "时间", "时长", "得分"]
        header_x = [70, 170, 250, 370, 450]
        for h, x in zip(headers, header_x):
            self.draw_text(h, (x, 80), 'hint', COLOR_TEXT_HIGHLIGHT)

        pygame.draw.line(self.screen, COLOR_GRID, (60, 103), (540, 103))

        # 日志条目
        y = 115
        for log in self.log_entries[:13]:
            diff_key = log.get('difficulty', 'normal')
            diff_label = DIFFICULTY_CONFIG.get(diff_key, DIFFICULTY_CONFIG[DIFFICULTY_NORMAL])['label']
            self.draw_text(str(log.get('username', '')), (70, y), 'hint')
            self.draw_text(diff_label, (170, y), 'hint',
                           DIFFICULTY_CONFIG.get(diff_key, DIFFICULTY_CONFIG[DIFFICULTY_NORMAL])['color'])
            start = log.get('start_time', '')
            self.draw_text(start[5:16] if len(start) > 16 else start[:11], (250, y), 'hint')
            self.draw_text(GameLog.format_duration(log.get('duration', 0)), (370, y), 'hint')
            self.draw_text(str(log.get('score', 0)), (450, y), 'hint', COLOR_TEXT_HIGHLIGHT)
            y += 30

        self.log_btns[0].draw(self.screen, self.fonts)

    def handle_log_input(self, event):
        """处理日志界面输入"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.log_btns[0].is_clicked(pos):
                self.sound.play('click')
                self.state = STATE_MENU

    # ==================== 主循环 ====================

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # 处理鼠标悬停
            pos = pygame.mouse.get_pos()
            for btn in self.get_current_buttons():
                btn.check_hover(pos)

            # 状态分发
            if self.state == STATE_LOGIN:
                self.handle_login_input(event)
            elif self.state == STATE_REGISTER:
                self.handle_register_input(event)
            elif self.state == STATE_MENU:
                self.handle_menu_input(event)
            elif self.state == STATE_DIFFICULTY:
                self.handle_difficulty_input(event)
            elif self.state in (STATE_PLAYING, STATE_PAUSED):
                self.handle_game_input(event)
            elif self.state == STATE_GAMEOVER:
                self.handle_gameover_input(event)
            elif self.state == STATE_LOG:
                self.handle_log_input(event)

            # 消息计时器
            if event.type == pygame.KEYDOWN:
                if self.message_timer > 0:
                    self.message_timer -= 1
                    if self.message_timer == 0:
                        self.message = ""

        return True

    def get_current_buttons(self):
        """获取当前界面的按钮列表"""
        if self.state == STATE_LOGIN:
            return [self.login_btn, self.register_btn]
        elif self.state == STATE_REGISTER:
            return [self.reg_submit_btn, self.reg_back_btn]
        elif self.state == STATE_MENU:
            return self.menu_btns
        elif self.state == STATE_DIFFICULTY:
            return self.difficulty_btns + [self.wall_mode_btn, self.diff_back_btn]
        elif self.state == STATE_GAMEOVER:
            return self.gameover_btns
        elif self.state == STATE_LOG:
            return self.log_btns
        return []

    def draw(self):
        """绘制当前界面"""
        if self.state == STATE_LOGIN:
            self.draw_login_screen()
        elif self.state == STATE_REGISTER:
            self.draw_register_screen()
        elif self.state == STATE_MENU:
            self.draw_menu_screen()
        elif self.state == STATE_DIFFICULTY:
            self.draw_difficulty_screen()
        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self.draw_game_screen()
        elif self.state == STATE_GAMEOVER:
            self.draw_gameover_screen()
        elif self.state == STATE_LOG:
            self.draw_log_screen()

        pygame.display.flip()

    def run(self):
        """主循环"""
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# 需要 math 模块用于菜单动画
import math


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
