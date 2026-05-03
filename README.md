# 贪吃蛇游戏 Snake Game V4

基于 Python + Pygame 的贪吃蛇游戏，支持多难度、穿墙模式、金色限时食物、音效系统和 SQLite 数据库。

## 功能亮点

- **tkinter 登录** — 原生中文输入法支持，深色主题对话框
- **三级难度** — 简单 / 普通 / 困难，不同速度与加速率
- **穿墙模式** — 可选开启，蛇穿越边界从对面出现
- **金色限时食物** — +30 分，8 秒后消失，快消失时闪烁提示
- **音效系统** — 吃食物、金色食物、游戏结束、按钮点击各有音效
- **SQLite 数据库** — 用户账号与游戏日志持久化存储
- **UI 美化** — 粒子特效、分数飘字、按钮悬停动画
- **独立 exe** — PyInstaller 打包，双击即可运行

## 快速开始

### 环境要求

- Python 3.12+
- Pygame 2.6+

### 安装依赖

```bash
pip install pygame
```

### 运行游戏

```bash
python snake_game.py
```

启动后先弹出 tkinter 登录对话框，注册/登录成功后进入游戏。

## 操作说明

| 按键 | 功能 |
|------|------|
| ↑ ↓ ← → | 控制蛇的移动方向 |
| ESC / P | 暂停 / 继续游戏 |
| 鼠标点击 | 界面按钮交互 |

## 项目结构

```
Tanchishe/
├── snake_game.py                # 主程序入口
├── login_dialog.py              # tkinter 登录/注册对话框
├── game/
│   ├── constants.py             # 常量配置
│   ├── database.py              # SQLite 数据库层
│   ├── player.py                # 玩家类
│   ├── game_log.py              # 日志类
│   ├── sound_manager.py         # 音效管理器
│   └── resources/
│       ├── msyh.ttc             # 微软雅黑字体
│       └── sounds/              # 音效文件（自动生成）
├── snake_game.spec              # PyInstaller 打包配置
├── hook-rth-tkinter-fix.py     # Tcl/Tk 运行时修复钩子
├── 贪吃蛇游戏软件分析与设计说明书.md
└── README.md
```

## 打包为 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm snake_game.spec
```

产物位于 `dist/贪吃蛇游戏.exe`，双击即可运行，无需安装 Python。

> 打包后需将 `sounds/` 文件夹复制到 exe 同目录（首次运行也会自动生成）。

## 技术栈

| 组件 | 技术 |
|------|------|
| 游戏引擎 | Pygame 2.6 |
| 登录界面 | tkinter |
| 数据库 | SQLite3 |
| 音效生成 | wave + struct |
| 打包 | PyInstaller |

## 许可证

MIT License
