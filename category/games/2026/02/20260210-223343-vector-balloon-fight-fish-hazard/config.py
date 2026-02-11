"""Configuration constants for Vector Balloon Fight: Fish Hazard."""

from enum import Enum
from dataclasses import dataclass


class Color(Enum):
    """Game colors."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    BLUE = (50, 150, 255)
    GREEN = (50, 200, 50)
    YELLOW = (255, 200, 50)
    WATER = (20, 80, 180)
    WATER_DEEP = (10, 50, 120)
    PLATFORM = (150, 100, 50)
    PLATFORM_HIGHLIGHT = (180, 130, 70)
    GRAY = (100, 100, 100)
    FISH = (80, 200, 120)
    FISH_DARK = (50, 150, 90)


@dataclass
class Physics:
    """Physics constants."""
    GRAVITY: float = 0.4
    FLAP_FORCE: float = -7.0
    MAX_FALL_SPEED: float = 10.0
    HORIZONTAL_ACCEL: float = 0.6
    HORIZONTAL_FRICTION: float = 0.85
    MAX_HORIZONTAL_SPEED: float = 5.0
    FLAP_COOLDOWN: int = 8
    BALLOON_LIFT: float = 0.12


@dataclass
class Game:
    """Game constants."""
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 600
    FPS: int = 60
    WATER_LEVEL: int = 520
    MAX_BALLOONS: int = 2
    ENEMY_COUNT: int = 3


@dataclass
class Scoring:
    """Scoring constants."""
    ENEMY_POPPED: int = 100
    SURVIVAL_PER_FRAME: float = 0.1
    BALLOON_LOST: int = -50
    GAME_OVER_FISH: int = -200
    GAME_OVER_FALL: int = -200
    WAVE_BONUS: int = 500


@dataclass
class Entity:
    """Entity dimensions."""
    PLAYER_WIDTH: int = 28
    PLAYER_HEIGHT: int = 24
    BALLOON_RADIUS: int = 14
    BALLOON_OFFSET: int = 28


@dataclass
class Fish:
    """Fish hazard constants."""
    WIDTH: int = 120
    HEIGHT: int = 60
    JUMP_SPEED: float = -12.0
    WARNING_FRAMES: int = 60
    COOLDOWN_MIN: int = 120
    COOLDOWN_MAX: int = 300
