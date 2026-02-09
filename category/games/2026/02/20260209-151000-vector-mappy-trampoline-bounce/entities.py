"""Game entities and state management."""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import config


@dataclass
class Item:
    """A collectible treasure item."""
    x: float
    y: float
    collected: bool = False

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        half_size = config.ITEM_SIZE / 2
        return (self.x - half_size, self.y - half_size,
                config.ITEM_SIZE, config.ITEM_SIZE)


@dataclass
class Trampoline:
    """A trampoline that bounces the player higher."""
    x: float
    y: float
    bounce_count: int = 0
    broken: bool = False

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        half_width = config.TRAMPOLINE_WIDTH / 2
        return (self.x - half_width, self.y - config.TRAMPOLINE_HEIGHT,
                config.TRAMPOLINE_WIDTH, config.TRAMPOLINE_HEIGHT)

    def get_color(self) -> Tuple[int, int, int]:
        """Get color based on bounce count."""
        if self.bounce_count >= config.MAX_BOUNCES - 1:
            return config.COLOR_TRAMPOLINE_DANGER
        elif self.bounce_count >= config.MAX_BOUNCES - 2:
            return config.COLOR_TRAMPOLINE_WARNING
        return config.COLOR_TRAMPOLINE


@dataclass
class Floor:
    """A floor platform with optional trampoline."""
    x: float
    y: float
    width: float
    trampoline: Optional[Trampoline] = None
    items: List[Item] = field(default_factory=list)

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.width, config.FLOOR_HEIGHT)

    def has_trampoline_at(self, x: float) -> bool:
        """Check if there's a trampoline at the given x position."""
        if self.trampoline is None or self.trampoline.broken:
            return False
        half_width = config.TRAMPOLINE_WIDTH / 2
        return self.trampoline.x - half_width <= x <= self.trampoline.x + half_width


@dataclass
class Enemy:
    """A cat enemy that chases the player."""
    x: float
    y: float
    floor_index: int
    direction: int = 1

    def update(self) -> None:
        """Update enemy position."""
        self.x += config.ENEMY_MOVE_SPEED * self.direction

    def reverse(self) -> None:
        """Reverse enemy direction."""
        self.direction *= -1

    @property
    def rect(self) -> Tuple[float, float, float, float]:
        half_size = config.ENEMY_SIZE / 2
        return (self.x - half_size, self.y - config.ENEMY_SIZE,
                config.ENEMY_SIZE, config.ENEMY_SIZE)


@dataclass
class Player:
    """The player character (mouse)."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    on_floor: bool = True
    on_trampoline: bool = False
    current_trampoline: Optional[Trampoline] = None
    consecutive_bounces: int = 0

    def move_left(self) -> None:
        """Move player left."""
        self.vx = -config.MOVE_SPEED

    def move_right(self) -> None:
        """Move player right."""
        self.vx = config.MOVE_SPEED

    def stop_horizontal(self) -> None:
        """Stop horizontal movement."""
        self.vx = 0

    def jump(self, is_trampoline: bool = False) -> None:
        """Make the player jump."""
        if is_trampoline:
            # Higher jump on trampoline, boost with consecutive bounces
            boost = self.consecutive_bounces * config.TRAMPOLINE_BOOST
            self.vy = config.TRAMPOLINE_JUMP_STRENGTH - boost
            if self.vy < -25:
                self.vy = -25  # Cap maximum jump velocity
        else:
            self.vy = config.JUMP_STRENGTH
            self.consecutive_bounces = 0
        self.on_floor = False
        self.on_trampoline = False

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
    level: int = 1
    floors: List[Floor] = field(default_factory=list)
    enemies: List[Enemy] = field(default_factory=list)
    player: Player = field(default_factory=lambda: Player(
        config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y))
    game_over: bool = False
    level_complete: bool = False
    total_reward: float = 0.0
    frames_survived: int = 0
    items_collected: int = 0
    total_items: int = 0

    def reset(self) -> None:
        """Reset game to initial state."""
        self.score = 0
        self.level = 1
        self.floors = self._generate_floors()
        self.enemies = self._generate_enemies()
        self.player = Player(config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y)
        self.game_over = False
        self.level_complete = False
        self.total_reward = 0.0
        self.frames_survived = 0
        self.items_collected = 0
        self.total_items = sum(len(floor.items) for floor in self.floors)

    def next_level(self) -> None:
        """Advance to next level."""
        self.level += 1
        self.floors = self._generate_floors()
        self.enemies = self._generate_enemies()
        self.player = Player(config.PLAYER_SPAWN_X, config.PLAYER_SPAWN_Y)
        self.level_complete = False
        self.items_collected = 0
        self.total_items = sum(len(floor.items) for floor in self.floors)

    def _generate_floors(self) -> List[Floor]:
        """Generate floors for the level."""
        floors = []
        y = config.SCREEN_HEIGHT - config.FLOOR_HEIGHT - 20

        for i in range(config.FLOORS_COUNT):
            # Floor width varies
            width = random.uniform(200, 350)
            x = random.uniform(0, config.SCREEN_WIDTH - width)

            # Add trampoline to most floors
            trampoline = None
            if i > 0:  # No trampoline on bottom floor (spawn floor)
                tramp_x = x + random.uniform(30, width - 30)
                trampoline = Trampoline(x=tramp_x, y=y)

            # Add items
            items = []
            if i > 0:  # No items on spawn floor
                num_items = min(config.ITEMS_PER_FLOOR, int(width / 80))
                for _ in range(num_items):
                    item_x = x + random.uniform(20, width - 20)
                    items.append(Item(x=item_x, y=y - config.ITEM_SIZE - 5))

            floors.append(Floor(x=x, y=y, width=width, trampoline=trampoline, items=items))
            y -= config.FLOOR_GAP

        return floors

    def _generate_enemies(self) -> List[Enemy]:
        """Generate enemies for the level."""
        enemies = []
        # Place enemies on random floors (not spawn floor)
        available_floors = list(range(1, len(self.floors)))
        random.shuffle(available_floors)

        num_enemies = min(config.ENEMIES_PER_LEVEL + self.level - 1, len(available_floors))
        for i in range(num_enemies):
            floor_idx = available_floors[i]
            floor = self.floors[floor_idx]
            enemy_x = floor.x + random.uniform(30, floor.width - 30)
            enemies.append(Enemy(
                x=enemy_x,
                y=floor.y - config.ENEMY_SIZE,
                floor_index=floor_idx
            ))

        return enemies

    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "score": self.score,
            "level": self.level,
            "player_x": self.player.x,
            "player_y": self.player.y,
            "player_vx": self.player.vx,
            "player_vy": self.player.vy,
            "consecutive_bounces": self.player.consecutive_bounces,
            "game_over": self.game_over,
            "items_collected": self.items_collected,
            "total_items": self.total_items,
            "enemies_count": len(self.enemies)
        }

    def get_observation(self) -> list:
        """Get normalized observation for AI agents."""
        obs = [
            self.player.x / config.SCREEN_WIDTH,
            self.player.y / config.SCREEN_HEIGHT,
            self.player.vx / config.MOVE_SPEED,
            self.player.vy / config.JUMP_STRENGTH,
            self.player.consecutive_bounces / config.MAX_BOUNCES,
            1.0 if self.player.on_floor else 0.0,
            1.0 if self.player.on_trampoline else 0.0,
            len(self.enemies) / 10.0,
            self.items_collected / max(self.total_items, 1),
            self.level / 10.0
        ]

        # Add nearest enemy info
        if self.enemies:
            nearest = min(self.enemies, key=lambda e: abs(e.y - self.player.y))
            enemy_dx = (nearest.x - self.player.x) / config.SCREEN_WIDTH
            enemy_dy = (nearest.y - self.player.y) / config.SCREEN_HEIGHT
            obs.extend([enemy_dx, enemy_dy])
        else:
            obs.extend([0.0, 0.0])

        # Add nearest trampoline info
        trampolines = [f.trampoline for f in self.floors if f.trampoline and not f.trampoline.broken]
        if trampolines:
            nearest = min(trampolines, key=lambda t: abs(t.y - self.player.y))
            tramp_dx = (nearest.x - self.player.x) / config.SCREEN_WIDTH
            tramp_dy = (nearest.y - self.player.y) / config.SCREEN_HEIGHT
            bounces_left = (config.MAX_BOUNCES - nearest.bounce_count) / config.MAX_BOUNCES
            obs.extend([tramp_dx, tramp_dy, bounces_left])
        else:
            obs.extend([0.0, 0.0, 0.0])

        return obs
