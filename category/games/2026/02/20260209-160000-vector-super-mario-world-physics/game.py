"""Game state and physics logic for Vector Super Mario World Physics."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Vec2:
    x: float
    y: float


class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.vel = Vec2(0.0, 0.0)
        self.width = 24
        self.height = 32
        self.on_ground = False
        self.jump_held = False
        self.jump_timer = 0.0
        self.max_jump_time = 0.25
        self.facing_right = True
        self.alive = True
        self.finished = False

    def update(self, dt: float, inputs: dict, platforms: List[dict]):
        if not self.alive or self.finished:
            return

        # Physics constants
        accel = 800.0
        friction = 0.85
        gravity = 1800.0
        max_speed = 250.0
        jump_velocity = 550.0
        variable_jump_gravity = 3000.0

        # Horizontal movement
        if inputs['left']:
            self.vel.x -= accel * dt
            self.facing_right = False
        if inputs['right']:
            self.vel.x += accel * dt
            self.facing_right = True

        # Apply friction
        if not (inputs['left'] or inputs['right']):
            self.vel.x *= friction

        # Clamp horizontal velocity
        self.vel.x = max(-max_speed, min(max_speed, self.vel.x))

        # Jump handling - variable height based on hold duration
        if inputs['jump'] and self.on_ground:
            self.vel.y = -jump_velocity
            self.on_ground = False
            self.jump_held = True
            self.jump_timer = 0.0

        # Track jump hold time for variable height
        if self.jump_held:
            self.jump_timer += dt
            if not inputs['jump'] or self.jump_timer >= self.max_jump_time:
                self.jump_held = False

        # Apply gravity (stronger when releasing jump early)
        current_gravity = variable_jump_gravity if (not self.jump_held and self.vel.y < 0) else gravity
        self.vel.y += current_gravity * dt

        # Update position
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt

        # Platform collision
        self.on_ground = False
        for plat in platforms:
            px, py, pw, ph = plat['x'], plat['y'], plat['w'], plat['h']
            if self.vel.y > 0:  # Only check when falling
                if (self.pos.x + self.width > px and self.pos.x < px + pw and
                    self.pos.y + self.height >= py and self.pos.y + self.height <= py + ph + self.vel.y * dt + 10):
                    self.pos.y = py - self.height
                    self.vel.y = 0
                    self.on_ground = True

        # Pit death
        if self.pos.y > 500:
            self.alive = False


class Enemy:
    def __init__(self, x: float, y: float, patrol_range: float):
        self.pos = Vec2(x, y)
        self.start_x = x
        self.vel = Vec2(50.0, 0.0)
        self.width = 28
        self.height = 28
        self.patrol_range = patrol_range
        self.alive = True

    def update(self, dt: float):
        if not self.alive:
            return

        self.pos.x += self.vel.x * dt

        # Reverse direction at patrol limits
        if abs(self.pos.x - self.start_x) > self.patrol_range:
            self.vel.x *= -1


class Coin:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.radius = 10
        self.collected = False


class GameState:
    def __init__(self):
        self.width = 800
        self.height = 400
        self.reset()

    def reset(self):
        self.player = Player(50, 300)
        self.score = 0
        self.game_over = False
        self.win = False

        # Level definition - platforms
        self.platforms = [
            {'x': 0, 'y': 360, 'w': 200, 'h': 40},      # Ground start
            {'x': 250, 'y': 360, 'w': 100, 'h': 40},    # Platform 1
            {'x': 400, 'y': 320, 'w': 80, 'h': 20},     # Platform 2
            {'x': 520, 'y': 280, 'w': 100, 'h': 20},    # Platform 3
            {'x': 680, 'y': 240, 'w': 120, 'h': 160},   # End platform
            {'x': 180, 'y': 260, 'w': 60, 'h': 20},     # High platform
            {'x': 350, 'y': 200, 'w': 80, 'h': 20},     # Higher platform
        ]

        # Enemies
        self.enemies = [
            Enemy(280, 332, 40),
            Enemy(540, 252, 40),
            Enemy(700, 212, 40),
        ]

        # Coins
        self.coins = [
            Coin(200, 320),
            Coin(270, 320),
            Coin(430, 280),
            Coin(550, 240),
            Coin(210, 220),
            Coin(380, 160),
            Coin(710, 200),
        ]

        # Goal flag position
        self.flag_x = 750
        self.flag_y = 140

    def update(self, dt: float, inputs: dict):
        if self.game_over:
            return

        self.player.update(dt, inputs, self.platforms)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt)

        # Enemy collision
        player_rect = (self.player.pos.x, self.player.pos.y, self.player.width, self.player.height)

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            enemy_rect = (enemy.pos.x, enemy.pos.y, enemy.width, enemy.height)

            if self._rects_collide(player_rect, enemy_rect):
                # Check if player is landing on top (stomping)
                if self.player.vel.y > 0 and self.player.pos.y + self.player.height - 10 < enemy.pos.y + enemy.height / 2:
                    enemy.alive = False
                    self.player.vel.y = -300.0  # Bounce
                    self.score += 500
                else:
                    # Player hit from side - death
                    self.player.alive = False
                    self.score -= 1000
                    self.game_over = True

        # Coin collection
        for coin in self.coins:
            if not coin.collected:
                dx = self.player.pos.x + self.player.width / 2 - coin.pos.x
                dy = self.player.pos.y + self.player.height / 2 - coin.pos.y
                if (dx * dx + dy * dy) < (coin.radius + 16) ** 2:
                    coin.collected = True
                    self.score += 100

        # Flag goal
        if (self.player.pos.x + self.player.width > self.flag_x and
            self.player.pos.x < self.flag_x + 10 and
            not self.player.finished):
            self.player.finished = True
            self.score += 1000
            self.win = True
            self.game_over = True

        # Pit death handling
        if not self.player.alive:
            self.game_over = True

    def _rects_collide(self, r1, r2) -> bool:
        return (r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1])
