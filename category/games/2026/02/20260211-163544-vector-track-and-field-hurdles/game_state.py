"""
Game state management for Track and Field Hurdles.
"""

from enum import Enum
from dataclasses import dataclass, field
import random


class GameState(Enum):
    MENU = "menu"
    RUNNING = "running"
    FINISHED = "finished"
    COLLISION = "collision"


@dataclass
class State:
    """Core game state for hurdles race."""
    distance: float = 0.0
    velocity: float = 0.0
    vertical_velocity: float = 0.0
    vertical_position: float = 0.0
    last_key: str = None
    time_elapsed: float = 0.0
    finish_time: float = None
    state: GameState = GameState.MENU
    collision_timer: float = 0.0
    hurdles_cleared: int = 0
    hurdles_hit: int = 0

    # Track constants
    TARGET_DISTANCE = 1000.0  # 1000 meters
    MAX_VELOCITY = 15.0
    VELOCITY_INCREMENT = 0.5
    FRICTION = 0.01

    # Jump physics
    GRAVITY = 800.0
    JUMP_FORCE = 350.0
    JUMP_CLEAR_HEIGHT = 40.0

    # Collision penalty
    COLLISION_DURATION = 1.5

    # Hurdle spacing
    MIN_HURDLE_SPACING = 40.0
    MAX_HURDLE_SPACING = 60.0

    def is_jumping(self) -> bool:
        return self.vertical_position < 0 or self.vertical_velocity != 0

    def is_in_collision(self) -> bool:
        return self.state == GameState.COLLISION and self.collision_timer > 0

    def trigger_collision(self):
        self.state = GameState.COLLISION
        self.collision_timer = self.COLLISION_DURATION
        self.velocity = 0.0
        self.vertical_velocity = 0.0
        self.vertical_position = 0.0
        self.hurdles_hit += 1

    def reset(self):
        self.distance = 0.0
        self.velocity = 0.0
        self.vertical_velocity = 0.0
        self.vertical_position = 0.0
        self.last_key = None
        self.time_elapsed = 0.0
        self.finish_time = None
        self.state = GameState.MENU
        self.collision_timer = 0.0
        self.hurdles_cleared = 0
        self.hurdles_hit = 0

    def calculate_score(self) -> int:
        if self.finish_time is None or self.finish_time <= 0:
            return 0
        base_score = int(50000 / self.finish_time)
        clear_bonus = self.hurdles_cleared * 100
        hit_penalty = self.hurdles_hit * 50
        return max(0, base_score + clear_bonus - hit_penalty)

    def generate_hurdle_positions(self) -> list:
        positions = []
        pos = 50.0
        while pos < self.TARGET_DISTANCE - 20:
            positions.append(pos)
            spacing = random.uniform(self.MIN_HURDLE_SPACING, self.MAX_HURDLE_SPACING)
            pos += spacing
        return positions
