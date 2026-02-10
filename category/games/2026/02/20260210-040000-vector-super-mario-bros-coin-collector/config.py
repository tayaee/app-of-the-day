"""Game configuration and constants."""

import pygame
from dataclasses import dataclass
from typing import Tuple

# Screen settings
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60

# Colors (vector-style palette)
COLOR_BG: Tuple[int, int, int] = (25, 30, 50)
COLOR_PLAYER: Tuple[int, int, int] = (220, 70, 70)
COLOR_PLATFORM: Tuple[int, int, int] = (70, 180, 100)
COLOR_COIN: Tuple[int, int, int] = (255, 200, 50)
COLOR_TEXT: Tuple[int, int, int] = (240, 240, 250)
COLOR_UI: Tuple[int, int, int] = (100, 100, 120)
COLOR_GAMEOVER: Tuple[int, int, int] = (200, 50, 50)

# Physics
GRAVITY: float = 0.8
JUMP_STRENGTH: float = -15.0
MAX_FALL_SPEED: float = 12.0
MOVE_SPEED: float = 5.0
FRICTION: float = 0.85

# Platform settings
PLATFORM_HEIGHT: int = 16
PLATFORM_WIDTH: int = 700
PLATFORM_Y_BOTTOM: int = 500
PLATFORM_Y_MIDDLE: int = 350
PLATFORM_Y_TOP: int = 200

# Player settings
PLAYER_SIZE: int = 28
PLAYER_SPAWN_X: int = SCREEN_WIDTH // 2
PLAYER_SPAWN_Y: int = PLATFORM_Y_BOTTOM - PLAYER_SIZE

# Coin settings
COIN_SIZE: int = 16
COIN_SPAWN_INTERVAL_MIN: int = 60
COIN_SPAWN_INTERVAL_MAX: int = 180
COIN_FALL_SPEED_MIN: float = 1.5
COIN_FALL_SPEED_MAX: float = 3.5

# Scoring
POINTS_PER_COIN: int = 10
POINTS_PER_SECOND: int = 1
SURVIVAL_REWARD: float = 0.01
COIN_REWARD: float = 1.0
DEATH_PENALTY: float = -5.0

# Game states
STATE_MENU: str = "menu"
STATE_PLAYING: str = "playing"
STATE_GAMEOVER: str = "gameover"

# Actions for AI agents
@dataclass
class Action:
    NONE: int = 0
    LEFT: int = 1
    RIGHT: int = 2
    JUMP: int = 3

# Key mappings
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_JUMP = pygame.K_SPACE
KEY_JUMP_ALT = pygame.K_UP
KEY_EXIT = pygame.K_ESCAPE
