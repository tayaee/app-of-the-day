"""Game entities: Player and Enemy classes."""

import pygame
import random
import config


class Player:
    """Player character with platformer physics."""

    def __init__(self):
        self.x = config.PLAYER_START_X
        self.y = config.PLAYER_START_Y
        self.width = config.PLAYER_SIZE
        self.height = config.PLAYER_SIZE
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True

    def move_left(self):
        """Start moving left."""
        self.vx -= config.MOVE_ACCEL
        self.facing_right = False

    def move_right(self):
        """Start moving right."""
        self.vx += config.MOVE_ACCEL
        self.facing_right = True

    def stop_horizontal(self):
        """Apply horizontal deceleration."""
        if self.vx > 0:
            self.vx = max(0, self.vx - config.MOVE_DECEL)
        elif self.vx < 0:
            self.vx = min(0, self.vx + config.MOVE_DECEL)

    def jump(self):
        """Jump if on ground."""
        if self.on_ground:
            self.vy = config.JUMP_FORCE
            self.on_ground = False

    def update(self):
        """Update physics."""
        # Apply gravity
        self.vy += config.GRAVITY

        # Limit horizontal speed
        self.vx = max(-config.MAX_SPEED, min(config.MAX_SPEED, self.vx))

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Screen boundaries
        if self.x < 0:
            self.x = 0
            self.vx = 0
        elif self.x + self.width > config.SCREEN_WIDTH:
            self.x = config.SCREEN_WIDTH - self.width
            self.vx = 0

        # Platform collision
        if self.y + self.height >= config.PLATFORM_Y:
            self.y = config.PLATFORM_Y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

    @property
    def rect(self):
        """Get hitbox rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center_x(self):
        """Get center X position."""
        return self.x + self.width / 2

    @property
    def center_y(self):
        """Get center Y position."""
        return self.y + self.height / 2

    def get_bottom_y(self):
        """Get bottom Y position."""
        return self.y + self.height


class Enemy:
    """Enemy that moves toward the player."""

    def __init__(self, spawn_side):
        """Initialize enemy from specified side."""
        self.width = config.ENEMY_SIZE
        self.height = config.ENEMY_SIZE
        self.speed = random.uniform(config.ENEMY_SPEED_MIN, config.ENEMY_SPEED_MAX)

        if spawn_side == "left":
            self.x = -self.width
            self.vx = self.speed
        else:
            self.x = config.SCREEN_WIDTH
            self.vx = -self.speed

        self.y = config.PLATFORM_Y - self.height
        self.squashed = False
        self.squash_timer = 0

    def update(self):
        """Update enemy position."""
        if self.squashed:
            self.squash_timer += 1
            return self.squash_timer < 10

        self.x += self.vx

        # Remove if off screen
        if self.x < -self.width - 50 or self.x > config.SCREEN_WIDTH + 50:
            return False

        return True

    @property
    def rect(self):
        """Get hitbox rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def top_y(self):
        """Get top Y position."""
        return self.y

    @property
    def center_y(self):
        """Get center Y position."""
        return self.y + self.height / 2

    def squash(self):
        """Mark enemy as squashed."""
        self.squashed = True
        self.vx = 0
