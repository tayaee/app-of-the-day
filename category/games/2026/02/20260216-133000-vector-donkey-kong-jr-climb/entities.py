"""
Game entities for Vector Donkey Kong Jr Climb
"""

import pygame
import random
from config import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED,
    CLIMB_SPEED_NORMAL, CLIMB_SPEED_DOUBLE,
    VINE_WIDTH, VINE_TOP_Y, VINE_BOTTOM_Y,
    SNAPJAW_WIDTH, SNAPJAW_HEIGHT, SNAPJAW_SPEED,
    BIRD_WIDTH, BIRD_HEIGHT, BIRD_SPEED,
    FRUIT_SIZE, FRUIT_DROP_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_PLAYER, COLOR_VINE, COLOR_SNAPJAW, COLOR_BIRD,
    COLOR_FRUIT, COLOR_KEY, COLOR_CAGE, COLOR_PLATFORM, COLOR_PLATFORM_EDGE,
    GRAVITY, FALL_DEATH_VELOCITY, NUM_VINES, VINE_SPACING, VINE_START_X,
    NUM_PLATFORMS, PLATFORM_HEIGHT, MAX_FRUITS
)


class Vine:
    """Climbable vine that spans vertically."""

    def __init__(self, x):
        self.x = x
        self.y_top = VINE_TOP_Y
        self.y_bottom = VINE_BOTTOM_Y
        self.width = VINE_WIDTH

    def get_rect(self):
        return pygame.Rect(self.x, self.y_top, self.width, self.y_bottom - self.y_top)

    def get_climb_zone(self):
        """Return the zone where player can grab this vine."""
        return pygame.Rect(self.x - 15, self.y_top, self.width + 30, self.y_bottom - self.y_top)

    def draw(self, surface):
        pygame.draw.line(surface, COLOR_VINE, (self.x, self.y_top), (self.x, self.y_bottom), self.width)

        # Draw vine segments for visual detail
        for y in range(self.y_top + 20, self.y_bottom, 30):
            pygame.draw.line(surface, (50, 150, 50), (self.x - 3, y), (self.x + 3, y + 5), 2)


class Platform:
    """Horizontal platform for walking."""

    def __init__(self, y, width):
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.x = (SCREEN_WIDTH - width) // 2

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_PLATFORM, rect)
        pygame.draw.rect(surface, COLOR_PLATFORM_EDGE, (self.x, self.y, self.width, 3))


class Player:
    """The player character (Junior) that climbs vines."""

    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = 50
        self.y = SCREEN_HEIGHT - 80
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.on_vines = []
        self.alive = True
        self.score = 0
        self.holding_two_vines = False
        self.fruits_collected = 0
        self.can_drop_fruit = True
        self.fruit_drop_cooldown = 0
        self.max_fall_velocity = 0

    def update(self, keys, vines, platforms):
        if not self.alive:
            return

        # Update fruit drop cooldown
        if self.fruit_drop_cooldown > 0:
            self.fruit_drop_cooldown -= 1
        else:
            self.can_drop_fruit = True

        # Check vine overlap
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_vines = []
        for vine in vines:
            if vine.get_climb_zone().colliderect(player_rect):
                self.on_vines.append(vine)

        # Check if holding two vines (overlap zone)
        self.holding_two_vines = len(self.on_vines) >= 2

        # Check platform collision
        self.on_ground = False
        for platform in platforms:
            platform_rect = platform.get_rect()
            if (platform_rect.colliderect(pygame.Rect(self.x, self.y + self.vel_y + 1, self.width, self.height)) and
                self.vel_y >= 0 and self.y + self.height - 5 <= platform.y + self.vel_y):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                break

        # Horizontal movement (only when on ground or not on vines)
        self.vel_x = 0
        if self.on_ground or not self.on_vines:
            if keys[pygame.K_LEFT]:
                self.vel_x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.vel_x = PLAYER_SPEED

        # Vertical climbing (when on vines)
        if self.on_vines:
            if keys[pygame.K_UP]:
                speed = CLIMB_SPEED_DOUBLE if self.holding_two_vines else CLIMB_SPEED_NORMAL
                self.vel_y = -speed
            elif keys[pygame.K_DOWN]:
                speed = CLIMB_SPEED_DOUBLE if self.holding_two_vines else CLIMB_SPEED_NORMAL
                self.vel_y = speed
            else:
                self.vel_y = 0
        else:
            # Apply gravity when not on vines or ground
            self.vel_y += GRAVITY

        # Track max fall velocity for death check
        if self.vel_y > self.max_fall_velocity:
            self.max_fall_velocity = self.vel_y

        # Apply movement
        self.x += self.vel_x
        self.y += self.vel_y

        # Screen boundaries
        self.x = max(10, min(self.x, SCREEN_WIDTH - self.width - 10))
        self.y = max(10, min(self.y, SCREEN_HEIGHT - self.height - 10))

        # Check fall death
        if not self.on_ground and not self.on_vines and self.vel_y > 0:
            self.max_fall_velocity = self.vel_y
            if self.max_fall_velocity > FALL_DEATH_VELOCITY and self.y > SCREEN_HEIGHT - 100:
                self.alive = False

    def drop_fruit(self):
        """Create a dropped fruit if available."""
        if self.can_drop_fruit and self.fruits_collected > 0:
            self.can_drop_fruit = False
            self.fruit_drop_cooldown = 60
            self.fruits_collected -= 1
            return Fruit(self.x + self.width // 2, self.y + self.height)
        return None

    def draw(self, surface):
        # Body
        body_rect = pygame.Rect(self.x, self.y + 12, self.width, self.height - 12)
        pygame.draw.rect(surface, COLOR_PLAYER, body_rect)

        # Head
        head_rect = pygame.Rect(self.x + 5, self.y, 20, 16)
        pygame.draw.rect(surface, COLOR_PLAYER, head_rect)

        # Eyes
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 10), int(self.y + 6)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 20), int(self.y + 6)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 10), int(self.y + 6)), 1)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 20), int(self.y + 6)), 1)

        # Visual indicator when holding two vines
        if self.holding_two_vines:
            pygame.draw.circle(surface, (255, 255, 0), (int(self.x + 15), int(self.y - 10)), 5)


class Snapjaw:
    """Mechanical trap that moves along vines."""

    def __init__(self, vine, start_y, direction):
        self.vine = vine
        self.x = vine.x - SNAPJAW_WIDTH // 2
        self.y = start_y
        self.width = SNAPJAW_WIDTH
        self.height = SNAPJAW_HEIGHT
        self.direction = direction  # 1 for up, -1 for down
        self.speed = SNAPJAW_SPEED
        self.active = True

    def update(self):
        if not self.active:
            return

        # Move along vine
        self.y += self.speed * self.direction

        # Reverse direction at ends of vine
        if self.y <= self.vine.y_top + 20:
            self.direction = -1
        elif self.y >= self.vine.y_bottom - 20:
            self.direction = 1

        # Update x to follow vine
        self.x = self.vine.x - SNAPJAW_WIDTH // 2

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_SNAPJAW, rect)

        # Jaw lines
        pygame.draw.line(surface, (150, 10, 40), (self.x + 5, self.y), (self.x + 10, self.y + self.height), 2)
        pygame.draw.line(surface, (150, 10, 40), (self.x + self.width - 5, self.y), (self.x + self.width - 10, self.y + self.height), 2)


class Bird:
    """Flying bird that moves horizontally."""

    def __init__(self, y, direction):
        self.x = SCREEN_WIDTH if direction == -1 else -BIRD_WIDTH
        self.y = y
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.direction = direction  # 1 for right, -1 for left
        self.speed = BIRD_SPEED
        self.active = True
        self.frame = 0

    def update(self):
        if not self.active:
            return

        self.x += self.speed * self.direction
        self.frame += 0.2

        # Remove if off screen
        if self.x < -self.width * 2 or self.x > SCREEN_WIDTH + self.width * 2:
            self.active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.ellipse(surface, COLOR_BIRD, rect)

        # Wing animation
        wing_offset = 5 * abs(int(self.frame) % 4 - 2)
        pygame.draw.ellipse(surface, (70, 70, 200),
                          (self.x + 10, self.y + wing_offset, 20, 10))

        # Eye
        eye_x = self.x + self.width - 10 if self.direction > 0 else self.x + 10
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(self.y + 8)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(self.y + 8)), 2)


class Fruit:
    """Droppable fruit that can eliminate enemies."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = FRUIT_SIZE
        self.speed = FRUIT_DROP_SPEED
        self.active = True

    def update(self):
        if not self.active:
            return

        self.y += self.speed

        # Remove if off screen
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_FRUIT, (int(self.x), int(self.y)), self.size // 2)


class Key:
    """The goal object at the top of the screen."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 35
        self.collected = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        if self.collected:
            return

        # Key shaft
        pygame.draw.rect(surface, COLOR_KEY, (self.x + 8, self.y + 10, 10, 25))

        # Key head (ring)
        pygame.draw.circle(surface, COLOR_KEY, (int(self.x + 13), int(self.y + 8)), 8)
        pygame.draw.circle(surface, COLOR_BG, (int(self.x + 13), int(self.y + 8)), 4)

        # Key teeth
        pygame.draw.rect(surface, COLOR_KEY, (self.x + 8, self.y + 28, 6, 4))
        pygame.draw.rect(surface, COLOR_KEY, (self.x + 8, self.y + 33, 10, 2))


class Cage:
    """The cage holding the captured giant."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 50
        self.locked = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        # Cage frame
        pygame.draw.rect(surface, COLOR_CAGE, (self.x, self.y, self.width, self.height), 3)

        # Bars
        for i in range(10, self.width, 10):
            pygame.draw.line(surface, COLOR_CAGE, (self.x + i, self.y), (self.x + i, self.y + self.height), 2)

        # Lock indicator
        if self.locked:
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x + self.width // 2), int(self.y + self.height // 2)), 8)
