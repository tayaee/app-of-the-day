"""Game configuration and constants."""

import pygame
from dataclasses import dataclass
from typing import Tuple

# Screen settings
SCREEN_WIDTH: int = 400
SCREEN_HEIGHT: int = 600
FPS: int = 60

# Colors (vector-style palette)
COLOR_BG: Tuple[int, int, int] = (15, 20, 35)
COLOR_PLAYER: Tuple[int, int, int] = (100, 200, 255)
COLOR_ENEMY: Tuple[int, int, int] = (255, 100, 100)
COLOR_FLOOR: Tuple[int, int, int] = (80, 90, 110)
COLOR_TRAMPOLINE: Tuple[int, int, int] = (255, 180, 50)
COLOR_TRAMPOLINE_WARNING: Tuple[int, int, int] = (255, 100, 50)
COLOR_TRAMPOLINE_DANGER: Tuple[int, int, int] = (255, 50, 50)
COLOR_ITEM: Tuple[int, int, int] = (100, 255, 150)
COLOR_TEXT: Tuple[int, int, int] = (240, 240, 250)
COLOR_UI: Tuple[int, int, int] = (100, 100, 120)

# Physics
GRAVITY: float = 0.5
JUMP_STRENGTH: float = -12.0
TRAMPOLINE_JUMP_STRENGTH: float = -14.0
TRAMPOLINE_BOOST: float = 2.0
MAX_FALL_SPEED: float = 12.0
MOVE_SPEED: float = 4.0
ENEMY_MOVE_SPEED: float = 1.5

# Player settings
PLAYER_SIZE: int = 20
PLAYER_SPAWN_X: int = SCREEN_WIDTH // 2
PLAYER_SPAWN_Y: int = SCREEN_HEIGHT - 80

# Floor/Trampoline settings
FLOOR_HEIGHT: int = 16
FLOORS_COUNT: int = 6
FLOOR_GAP: int = 90
TRAMPOLINE_WIDTH: int = 40
TRAMPOLINE_HEIGHT: int = 8
MAX_BOUNCES: int = 4

# Item settings
ITEM_SIZE: int = 12
ITEMS_PER_FLOOR: int = 2

# Enemy settings
ENEMY_SIZE: int = 22
ENEMIES_PER_LEVEL: int = 2

# Scoring
POINTS_PER_ITEM: int = 100
POINTS_PER_LEVEL: int = 1000
SURVIVAL_REWARD: float = 0.01
COLLECT_REWARD: float = 2.0
LEVEL_COMPLETE_REWARD: float = 10.0
DEATH_PENALTY: float = -5.0
TRAMPOLINE_BREAK_PENALTY: float = -2.0

# Game states
STATE_MENU: str = "menu"
STATE_PLAYING: str = "playing"
STATE_GAMEOVER: str = "gameover"
STATE_LEVEL_COMPLETE: str = "level_complete"

# Actions for AI agents
@dataclass
class Action:
    NONE: int = 0
    LEFT: int = 1
    RIGHT: int = 2

# Key mappings
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_EXIT = pygame.K_ESCAPE
KEY_JUMP = pygame.K_SPACE
KEY_JUMP_ALT = pygame.K_UP
