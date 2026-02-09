"""Game entities and state management."""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import config


@dataclass
class Platform:
    """A platform the player can land on."""
    x: float
    y: float
    width: float
    moving: bool = False
    move_direction: int = 1

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.width, config.PLATFORM_HEIGHT)

    def update(self) -> None:
        """Update platform position if moving."""
        if self.moving:
            self.x += config.MOVING_PLATFORM_SPEED * self.move_direction
            if self.x <= 0 or self.x + self.width >= config.SCREEN_WIDTH:
                self.move_direction *= -1


@dataclass
class PowerUp:
    """A powerup that enhances player abilities."""
    x: float
    y: float

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        half_size = config.POWERUP_SIZE / 2
        return (self.x - half_size, self.y - half_size,
                config.POWERUP_SIZE, config.POWERUP_SIZE)


@dataclass
class Player:
    """The player character."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = False
    super_jumps_remaining: int = 0

    def jump(self) -> None:
        """Make the player jump."""
        if self.on_ground:
            if self.super_jumps_remaining > 0:
                self.vy = config.SUPER_JUMP_STRENGTH
                self.super_jumps_remaining -= 1
            else:
                self.vy = config.JUMP_STRENGTH
            self.on_ground = False

    def move_left(self) -> None:
        """Move player left."""
        self.vx = -config.MOVE_SPEED

    def move_right(self) -> None:
        """Move player right."""
        self.vx = config.MOVE_SPEED

    def stop_horizontal(self) -> None:
        """Stop horizontal movement."""
        self.vx = 0

    def update(self) -> None:
        """Update player physics."""
        # Apply gravity
        self.vy += config.GRAVITY
        if self.vy > config.MAX_FALL_SPEED:
            self.vy = config.MAX_FALL_SPEED

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Screen wrapping for horizontal movement
        if self.x < 0:
            self.x = config.SCREEN_WIDTH
        elif self.x > config.SCREEN_WIDTH:
            self.x = 0

        # Ground check
        self.on_ground = False

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, config.PLAYER_SIZE, config.PLAYER_SIZE)

    def get_center(self) -> Tuple[float, float]:
        return (self.x + config.PLAYER_SIZE / 2,
                self.y + config.PLAYER_SIZE / 2)


@dataclass
class GameState:
    """Complete game state for serialization and AI observation."""
    score: int = 0
    max_height: int = 0
    platforms: List[Platform] = field(default_factory=list)
    powerups: List[PowerUp] = field(default_factory=list)
    player: Player = field(default_factory=lambda: Player(
        config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y))
    camera_y: float = 0.0
    game_over: bool = False
    platforms_landed: int = 0
    total_reward: float = 0.0
    frames_survived: int = 0

    def reset(self) -> None:
        """Reset game to initial state."""
        self.score = 0
        self.max_height = 0
        self.platforms = self._generate_initial_platforms()
        self.powerups = []
        self.player = Player(config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y)
        self.camera_y = 0.0
        self.game_over = False
        self.platforms_landed = 0
        self.total_reward = 0.0
        self.frames_survived = 0

    def _generate_initial_platforms(self) -> List[Platform]:
        """Generate starting platforms."""
        platforms = []
        y = config.PLATFORM_Y_START
        for i in range(7):
            platforms.append(Platform(
                x=random.uniform(0, config.SCREEN_WIDTH - config.PLATFORM_WIDTH_MAX),
                y=y,
                width=random.uniform(config.PLATFORM_WIDTH_MIN, config.PLATFORM_WIDTH_MAX)
            ))
            y -= random.uniform(config.PLATFORM_GAP_MIN, config.PLATFORM_GAP_MAX)
        return platforms

    def generate_platform(self) -> Platform:
        """Generate a new platform above the screen."""
        moving = self.score >= config.MOVING_PLATFORM_START_SCORE
        if moving and random.random() < 0.3:
            moving = True

        platform = Platform(
            x=random.uniform(0, config.SCREEN_WIDTH - config.PLATFORM_WIDTH_MAX),
            y=self.platforms[-1].y - random.uniform(config.PLATFORM_GAP_MIN, config.PLATFORM_GAP_MAX),
            width=random.uniform(config.PLATFORM_WIDTH_MIN, config.PLATFORM_WIDTH_MAX),
            moving=moving
        )

        # Add powerup chance
        if random.random() < config.POWERUP_CHANCE:
            self.powerups.append(PowerUp(
                x=platform.x + platform.width / 2,
                y=platform.y - config.POWERUP_SIZE / 2 - 5
            ))

        return platform

    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "score": self.score,
            "max_height": self.max_height,
            "player_x": self.player.x,
            "player_y": self.player.y,
            "player_vx": self.player.vx,
            "player_vy": self.player.vy,
            "camera_y": self.camera_y,
            "game_over": self.game_over,
            "super_jumps": self.player.super_jumps_remaining,
            "platforms_count": len(self.platforms),
            "powerups_count": len(self.powerups)
        }

    def get_observation(self) -> list:
        """Get normalized observation for AI agents."""
        player_center = self.player.get_center()
        obs = [
            self.player.x / config.SCREEN_WIDTH,
            self.player.y / config.SCREEN_HEIGHT,
            self.player.vx / config.MOVE_SPEED,
            self.player.vy / config.JUMP_STRENGTH,
            self.camera_y / config.SCREEN_HEIGHT,
            1.0 if self.player.on_ground else 0.0,
            float(self.player.super_jumps_remaining > 0),
            len(self.platforms) / 20.0,
            len(self.powerups) / 5.0
        ]

        # Add nearest platform info
        if self.platforms:
            nearest = min(self.platforms, key=lambda p: abs(p.y - self.player.y))
            obs.extend([
                nearest.x / config.SCREEN_WIDTH,
                nearest.y / config.SCREEN_HEIGHT,
                nearest.width / config.PLATFORM_WIDTH_MAX,
                1.0 if nearest.moving else 0.0
            ])
        else:
            obs.extend([0.0, 0.0, 0.0, 0.0])

        return obs
