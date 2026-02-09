"""Game configuration and constants."""

import pygame
from dataclasses import dataclass
from typing import Tuple

# Screen settings
SCREEN_WIDTH: int = 400
SCREEN_HEIGHT: int = 600
FPS: int = 60

# Colors (vector-style palette)
COLOR_BG: Tuple[int, int, int] = (20, 25, 40)
COLOR_PLAYER: Tuple[int, int, int] = (230, 80, 80)
COLOR_PLATFORM: Tuple[int, int, int] = (80, 200, 120)
COLOR_PLATFORM_MOVING: Tuple[int, int, int] = (200, 150, 80)
COLOR_POWERUP: Tuple[int, int, int] = (220, 180, 50)
COLOR_TEXT: Tuple[int, int, int] = (240, 240, 250)
COLOR_UI: Tuple[int, int, int] = (100, 100, 120)

# Physics
GRAVITY: float = 0.8
JUMP_STRENGTH: float = -15.0
SUPER_JUMP_STRENGTH: float = -20.0
MAX_FALL_SPEED: float = 10.0
MOVE_SPEED: float = 5.0

# Platform settings
PLATFORM_WIDTH_MIN: int = 60
PLATFORM_WIDTH_MAX: int = 100
PLATFORM_HEIGHT: int = 12
PLATFORM_GAP_MIN: int = 70
PLATFORM_GAP_MAX: int = 130
PLATFORM_Y_START: int = 500
MOVING_PLATFORM_SPEED: float = 2.0
MOVING_PLATFORM_START_SCORE: int = 100

# Powerup settings
POWERUP_SIZE: int = 20
POWERUP_CHANCE: float = 0.15
POWERUP_DURATION: int = 1  # Number of jumps

# Player settings
PLAYER_SIZE: int = 24
PLAYER_SPAWN_X: int = SCREEN_WIDTH // 2
PLAYER_SPAWN_Y: int = SCREEN_HEIGHT - 100

# Scoring
POINTS_PER_PLATFORM: int = 10
SURVIVAL_REWARD: float = 0.01
NEW_HEIGHT_REWARD: float = 0.5
DEATH_PENALTY: float = -5.0
LANDING_REWARD: float = 1.0

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
