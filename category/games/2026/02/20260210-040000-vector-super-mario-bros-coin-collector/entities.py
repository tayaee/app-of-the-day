"""Game entities and state management."""

import random
from dataclasses import dataclass, field
from typing import List, Tuple
import config


@dataclass
class Platform:
    """A platform the player can land on."""
    x: float
    y: float
    width: float

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.width, config.PLATFORM_HEIGHT)

    def get_rect(self) -> Tuple[float, float, float, float]:
        """Get pygame Rect for collision detection."""
        return (self.x, self.y, self.width, config.PLATFORM_HEIGHT)


@dataclass
class Coin:
    """A falling coin to collect."""
    x: float
    y: float
    fall_speed: float
    rotation: float = 0.0

    def update(self) -> None:
        """Update coin position."""
        self.y += self.fall_speed
        self.rotation += 0.15

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        half_size = config.COIN_SIZE / 2
        return (self.x - half_size, self.y - half_size,
                config.COIN_SIZE, config.COIN_SIZE)

    def get_rect(self) -> Tuple[float, float, float, float]:
        """Get pygame Rect for collision detection."""
        half_size = config.COIN_SIZE / 2
        return (self.x - half_size, self.y - half_size,
                config.COIN_SIZE, config.COIN_SIZE)


@dataclass
class Player:
    """The player character."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = False

    def jump(self) -> None:
        """Make the player jump."""
        if self.on_ground:
            self.vy = config.JUMP_STRENGTH
            self.on_ground = False

    def move_left(self) -> None:
        """Move player left."""
        self.vx = -config.MOVE_SPEED

    def move_right(self) -> None:
        """Move player right."""
        self.vx = config.MOVE_SPEED

    def stop_horizontal(self) -> None:
        """Stop horizontal movement with friction."""
        self.vx *= config.FRICTION
        if abs(self.vx) < 0.1:
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

        # Screen bounds for horizontal movement
        if self.x < 0:
            self.x = 0
            self.vx = 0
        elif self.x > config.SCREEN_WIDTH - config.PLAYER_SIZE:
            self.x = config.SCREEN_WIDTH - config.PLAYER_SIZE
            self.vx = 0

        # Ground check (will be set by platform collision)
        self.on_ground = False

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, config.PLAYER_SIZE, config.PLAYER_SIZE)

    def get_rect(self) -> Tuple[float, float, float, float]:
        """Get pygame Rect for collision detection."""
        return (self.x, self.y, config.PLAYER_SIZE, config.PLAYER_SIZE)

    def get_center(self) -> Tuple[float, float]:
        return (self.x + config.PLAYER_SIZE / 2,
                self.y + config.PLAYER_SIZE / 2)


@dataclass
class GameState:
    """Complete game state for serialization and AI observation."""
    score: int = 0
    coins_collected: int = 0
    coins: List[Coin] = field(default_factory=list)
    player: Player = field(default_factory=lambda: Player(
        config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y))
    platforms: List[Platform] = field(default_factory=list)
    game_over: bool = False
    total_reward: float = 0.0
    frames_survived: int = 0
    coin_spawn_timer: int = 0

    def reset(self) -> None:
        """Reset game to initial state."""
        self.score = 0
        self.coins_collected = 0
        self.coins = []
        self.player = Player(config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y)
        self.platforms = self._create_platforms()
        self.game_over = False
        self.total_reward = 0.0
        self.frames_survived = 0
        self.coin_spawn_timer = 0

    def _create_platforms(self) -> List[Platform]:
        """Create the three fixed platforms."""
        platform_gap = (config.SCREEN_WIDTH - config.PLATFORM_WIDTH) // 2
        return [
            Platform(
                x=platform_gap,
                y=config.PLATFORM_Y_BOTTOM,
                width=config.PLATFORM_WIDTH
            ),
            Platform(
                x=platform_gap,
                y=config.PLATFORM_Y_MIDDLE,
                width=config.PLATFORM_WIDTH
            ),
            Platform(
                x=platform_gap,
                y=config.PLATFORM_Y_TOP,
                width=config.PLATFORM_WIDTH
            ),
        ]

    def spawn_coin(self) -> None:
        """Spawn a new coin at the top of the screen."""
        x = random.uniform(config.COIN_SIZE, config.SCREEN_WIDTH - config.COIN_SIZE)
        y = -config.COIN_SIZE
        fall_speed = random.uniform(config.COIN_FALL_SPEED_MIN, config.COIN_FALL_SPEED_MAX)
        self.coins.append(Coin(x=x, y=y, fall_speed=fall_speed))

    def update_coin_spawn(self) -> None:
        """Update coin spawn timer and spawn coins when ready."""
        self.coin_spawn_timer += 1
        if self.coin_spawn_timer >= self._next_spawn_interval():
            self.spawn_coin()
            self.coin_spawn_timer = 0

    def _next_spawn_interval(self) -> int:
        """Get the next coin spawn interval."""
        base_interval = random.uniform(config.COIN_SPAWN_INTERVAL_MIN,
                                       config.COIN_SPAWN_INTERVAL_MAX)
        # Spawn faster as score increases
        difficulty_factor = max(0.5, 1.0 - (self.coins_collected * 0.01))
        return int(base_interval * difficulty_factor)

    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "score": self.score,
            "coins_collected": self.coins_collected,
            "player_x": self.player.x,
            "player_y": self.player.y,
            "player_vx": self.player.vx,
            "player_vy": self.player.vy,
            "on_ground": self.player.on_ground,
            "game_over": self.game_over,
            "coins_count": len(self.coins),
            "frames_survived": self.frames_survived
        }

    def get_observation(self) -> list:
        """Get normalized observation for AI agents."""
        obs = [
            self.player.x / config.SCREEN_WIDTH,
            self.player.y / config.SCREEN_HEIGHT,
            self.player.vx / config.MOVE_SPEED,
            self.player.vy / config.JUMP_STRENGTH,
            1.0 if self.player.on_ground else 0.0,
            len(self.coins) / 20.0
        ]

        # Add info about nearest coin
        if self.coins:
            nearest = min(self.coins, key=lambda c:
                         ((c.x - self.player.x) ** 2 +
                          (c.y - self.player.y) ** 2) ** 0.5)
            player_center = self.player.get_center()
            dist_x = (nearest.x - player_center[0]) / config.SCREEN_WIDTH
            dist_y = (nearest.y - player_center[1]) / config.SCREEN_HEIGHT
            obs.extend([dist_x, dist_y])
        else:
            obs.extend([0.0, 0.0])

        return obs
