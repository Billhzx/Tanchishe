# -*- coding: utf-8 -*-
"""
音效管理器
自动生成并播放游戏音效
"""

import pygame
import os
import wave
import struct
import math

from game.constants import SOUNDS_DIR, SOUND_EAT, SOUND_GOLD, SOUND_GAMEOVER, SOUND_CLICK


def _generate_tone(filename, frequency, duration, volume=0.3, sample_rate=22050):
    """生成简单的正弦波音效文件"""
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = i / sample_rate
        # 淡出效果
        fade = 1.0
        if i > n_samples * 0.7:
            fade = (n_samples - i) / (n_samples * 0.3)
        value = volume * fade * math.sin(2 * math.pi * frequency * t)
        data.append(int(value * 32767))

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack('<' + 'h' * len(data), *data))


def _generate_gameover_sound(filename, sample_rate=22050):
    """生成游戏结束音效（下降音调）"""
    duration = 0.5
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = i / sample_rate
        # 频率从440Hz下降到220Hz
        freq = 440 - (220 * t / duration)
        fade = 1.0
        if i > n_samples * 0.5:
            fade = (n_samples - i) / (n_samples * 0.5)
        value = 0.3 * fade * math.sin(2 * math.pi * freq * t)
        data.append(int(value * 32767))

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack('<' + 'h' * len(data), *data))


def _generate_gold_sound(filename, sample_rate=22050):
    """生成金色食物音效（上升双音）"""
    duration = 0.2
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = i / sample_rate
        fade = 1.0
        if i > n_samples * 0.6:
            fade = (n_samples - i) / (n_samples * 0.4)
        # 双音叠加（C5 + E5 和弦）
        value = 0.2 * fade * (
            math.sin(2 * math.pi * 1047 * t) +   # C6
            math.sin(2 * math.pi * 1319 * t)      # E6
        )
        data.append(int(value * 32767))

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack('<' + 'h' * len(data), *data))


def ensure_sounds():
    """确保所有音效文件存在，不存在则自动生成"""
    if not os.path.exists(SOUND_EAT):
        _generate_tone(SOUND_EAT, 880, 0.1)
    if not os.path.exists(SOUND_GOLD):
        _generate_gold_sound(SOUND_GOLD)
    if not os.path.exists(SOUND_GAMEOVER):
        _generate_gameover_sound(SOUND_GAMEOVER)
    if not os.path.exists(SOUND_CLICK):
        _generate_tone(SOUND_CLICK, 600, 0.05, volume=0.15)


class SoundManager:
    """音效管理器"""

    def __init__(self):
        self.enabled = True
        self.initialized = False
        self.sounds = {}

    def init(self):
        """初始化音效系统"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            ensure_sounds()
            self.sounds = {
                'eat': pygame.mixer.Sound(SOUND_EAT),
                'gold': pygame.mixer.Sound(SOUND_GOLD),
                'gameover': pygame.mixer.Sound(SOUND_GAMEOVER),
                'click': pygame.mixer.Sound(SOUND_CLICK),
            }
            # 设置音量
            for sound in self.sounds.values():
                sound.set_volume(0.5)
            self.sounds['click'].set_volume(0.3)
            self.initialized = True
        except pygame.error:
            self.initialized = False
            self.enabled = False

    def play(self, name):
        """播放音效"""
        if not self.enabled or not self.initialized:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def toggle(self):
        """切换音效开关"""
        self.enabled = not self.enabled
        return self.enabled
