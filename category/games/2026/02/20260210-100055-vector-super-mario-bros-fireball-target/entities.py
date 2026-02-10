import pygame
import random
import math
from config import *


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

    def draw(self, screen):
        # Body (red)
        pygame.draw.rect(screen, MARIO_COLOR, (self.x, self.y + 10, self.width, self.height - 10))
        # Overalls (blue)
        pygame.draw.rect(screen, MARIO_OVERALLS_COLOR, (self.x, self.y + 20, self.width, self.height - 20))
        # Hat
        pygame.draw.rect(screen, MARIO_COLOR, (self.x - 2, self.y, self.width + 4, 12))
        # Face
        pygame.draw.circle(screen, (255, 220, 177), (self.x + self.width // 2, self.y + 18), 8)
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (self.x + self.width // 2 - 3, self.y + 16), 2)
        pygame.draw.circle(screen, (0, 0, 0), (self.x + self.width // 2 + 3, self.y + 16), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_launch_pos(self):
        return (self.x + self.width, self.y + 15)


class Fireball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = FIREBALL_RADIUS
        self.vel_x = FIREBALL_SPEED_X / FPS
        self.vel_y = FIREBALL_SPEED_Y / FPS
        self.bounces = 0
        self.max_bounces = 2
        self.active = True
        self.enemies_hit = []

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY / FPS / FPS

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Ground bounce
        if self.y + self.radius >= GROUND_Y:
            self.y = GROUND_Y - self.radius
            self.vel_y = -self.vel_y * 0.7  # Bounce with energy loss
            self.bounces += 1

            if self.bounces >= self.max_bounces:
                self.active = False

        # Remove if off screen
        if self.x - self.radius > SCREEN_WIDTH:
            self.active = False

        return self.active

    def draw(self, screen):
        if self.active:
            # Outer glow
            pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.radius + 3)
            # Core
            pygame.draw.circle(screen, FIREBALL_COLOR, (int(self.x), int(self.y)), self.radius)
            # Highlight
            pygame.draw.circle(screen, (255, 255, 200), (int(self.x - 2), int(self.y - 2)), 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

    def has_hit(self, enemy):
        return enemy in self.enemies_hit

    def mark_hit(self, enemy):
        self.enemies_hit.append(enemy)


class Enemy:
    def __init__(self, difficulty=1):
        self.x = SCREEN_WIDTH + random.randint(50, 150)
        self.y = GROUND_Y - self.height if hasattr(self, 'height') else GROUND_Y - 30
        self.difficulty = difficulty
        self.alive = True
        self.hit_animation = 0

    def update(self):
        self.x -= self.speed

        # Remove if off screen (missed)
        if self.x + self.width < 0:
            self.alive = False
            return "missed"
        return None

    def draw(self, screen):
        pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def hit(self):
        self.hit_animation = 10
        self.alive = False


class Goomba(Enemy):
    def __init__(self, difficulty=1):
        self.width = 30
        self.height = 30
        super().__init__(difficulty)
        self.y = GROUND_Y - self.height
        self.speed = 2 + difficulty * 0.5
        self.bob_offset = random.random() * 6.28

    def update(self):
        result = super().update()
        self.bob_offset += 0.1
        return result

    def draw(self, screen):
        if not self.alive and self.hit_animation <= 0:
            return

        # Bobbing animation
        bob = 0
        if self.alive:
            bob = int(math.sin(self.bob_offset) * 2)

        # Body (brown mushroom shape)
        y_pos = self.y + bob
        pygame.draw.ellipse(screen, GOOMBA_COLOR, (self.x, y_pos, self.width, self.height))

        # Stem
        pygame.draw.rect(screen, (210, 180, 140), (self.x + 10, y_pos + 20, 10, 10))

        # Eyes
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 10), int(y_pos + 10)), 5)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 20), int(y_pos + 10)), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 10), int(y_pos + 10)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 20), int(y_pos + 10)), 2)

        # Feet
        pygame.draw.ellipse(screen, (0, 0, 0), (self.x - 2, y_pos + 22, 12, 8))
        pygame.draw.ellipse(screen, (0, 0, 0), (self.x + 20, y_pos + 22, 12, 8))

        if self.hit_animation > 0:
            # Hit effect
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x + self.width//2), int(y_pos + self.height//2)), 20 - self.hit_animation)
            self.hit_animation -= 1


class Koopa(Enemy):
    def __init__(self, difficulty=1):
        self.width = 30
        self.height = 40
        super().__init__(difficulty)
        self.y = GROUND_Y - self.height
        self.speed = 1.5 + difficulty * 0.3
        self.walk_frame = 0

    def update(self):
        result = super().update()
        self.walk_frame += 0.15
        return result

    def draw(self, screen):
        if not self.alive and self.hit_animation <= 0:
            return

        # Shell animation
        shell_color = (139, 90, 43) if int(self.walk_frame * 2) % 2 == 0 else (160, 110, 60)

        # Shell
        pygame.draw.ellipse(screen, shell_color, (self.x + 2, self.y + 15, 26, 22))
        pygame.draw.ellipse(screen, (255, 215, 0), (self.x + 8, self.y + 18, 14, 14))

        # Head
        pygame.draw.circle(screen, (255, 220, 177), (int(self.x + 15), int(self.y + 10)), 8)

        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 12), int(self.y + 8)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 18), int(self.y + 8)), 2)

        # Beak
        pygame.draw.polygon(screen, (255, 200, 100), [
            (self.x + 15, self.y + 12),
            (self.x + 12, self.y + 15),
            (self.x + 18, self.y + 15)
        ])

        # Feet
        foot_y = self.y + 35
        if int(self.walk_frame) % 2 == 0:
            pygame.draw.ellipse(screen, (255, 220, 177), (self.x, foot_y, 10, 6))
            pygame.draw.ellipse(screen, (255, 220, 177), (self.x + 20, foot_y, 10, 6))
        else:
            pygame.draw.ellipse(screen, (255, 220, 177), (self.x + 5, foot_y, 10, 6))
            pygame.draw.ellipse(screen, (255, 220, 177), (self.x + 15, foot_y, 10, 6))

        if self.hit_animation > 0:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x + self.width//2), int(self.y + self.height//2)), 25 - self.hit_animation * 2)
            self.hit_animation -= 1


class FloatingBlock(Enemy):
    def __init__(self, difficulty=1):
        self.width = 35
        self.height = 35
        super().__init__(difficulty)
        base_y = GROUND_Y - 100 - random.randint(0, 150)
        self.y = base_y
        self.target_y = base_y
        self.speed = 1 + difficulty * 0.3
        self.float_offset = random.random() * 6.28
        self.float_speed = 0.05 + random.random() * 0.03
        self.float_amplitude = 20 + random.randint(0, 20)

    def update(self):
        self.x -= self.speed
        self.float_offset += self.float_speed
        self.y = self.target_y + int(math.sin(self.float_offset) * self.float_amplitude)

        if self.x + self.width < 0:
            self.alive = False
            return "missed"
        return None

    def draw(self, screen):
        if not self.alive and self.hit_animation <= 0:
            return

        # Block body (brick pattern)
        pygame.draw.rect(screen, (205, 133, 63), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

        # Brick lines
        pygame.draw.line(screen, (139, 90, 43), (self.x, self.y + 12), (self.x + self.width, self.y + 12), 1)
        pygame.draw.line(screen, (139, 90, 43), (self.x, self.y + 24), (self.x + self.width, self.y + 24), 1)
        pygame.draw.line(screen, (139, 90, 43), (self.x + 17, self.y + 12), (self.x + 17, self.y + 24), 1)

        # Question mark for blocks
        font = pygame.font.Font(None, 28)
        q_mark = font.render("?", True, (255, 215, 0))
        screen.blit(q_mark, (self.x + 10, self.y + 3))

        if self.hit_animation > 0:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x + self.width//2), int(self.y + self.height//2)), 25 - self.hit_animation * 2)
            self.hit_animation -= 1
