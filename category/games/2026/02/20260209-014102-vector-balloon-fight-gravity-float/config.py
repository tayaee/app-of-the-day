"""Configuration constants for Vector Balloon Fight."""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class Color(Enum):
    """Game colors."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    BLUE = (50, 100, 255)
    GREEN = (50, 200, 50)
    YELLOW = (255, 200, 50)
    WATER = (30, 100, 200)
    PLATFORM = (150, 100, 50)
    GRAY = (100, 100, 100)


@dataclass
class Physics:
    """Physics constants."""
    GRAVITY: float = 0.5
    FLAP_FORCE: float = -10.0
    MAX_FALL_SPEED: float = 12.0
    HORIZONTAL_ACCEL: float = 0.8
    HORIZONTAL_FRICTION: float = 0.9
    MAX_HORIZONTAL_SPEED: float = 6.0
    FLAP_COOLDOWN: int = 10  # frames


@dataclass
class Game:
    """Game constants."""
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 600
    FPS: int = 60
    PLATFORM_COUNT: int = 5
    ENEMY_COUNT: int = 2
    KILL_SCORE: int = 500
    SURVIVAL_SCORE_PER_SEC: int = 10
    MAX_BALLOONS: int = 2


@dataclass
class Entity:
    """Entity dimensions."""
    PLAYER_WIDTH: int = 30
    PLAYER_HEIGHT: int = 20
    BALLOON_RADIUS: int = 15
    BALLOON_OFFSET: int = 25
