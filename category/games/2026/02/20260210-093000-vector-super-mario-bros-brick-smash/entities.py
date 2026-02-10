import pygame
from config import *


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def move_left(self):
        self.vel_x = -PLAYER_SPEED

    def move_right(self):
        self.vel_x = PLAYER_SPEED

    def stop_horizontal(self):
        self.vel_x = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Keep player on screen
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, screen):
        # Draw player body
        pygame.draw.rect(screen, PLAYER_COLOR, (int(self.x), int(self.y), self.width, self.height))
        # Draw hat (Mario-style)
        pygame.draw.rect(screen, (200, 0, 0), (int(self.x) - 2, int(self.y) - 8, self.width + 4, 10))
        # Draw eyes
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x) + 8, int(self.y) + 12), 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x) + 22, int(self.y) + 12), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x) + 9, int(self.y) + 12), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x) + 23, int(self.y) + 12), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_head_rect(self):
        # The head area for hitting blocks from below
        return pygame.Rect(int(self.x), int(self.y), self.width, 8)

    def get_feet_rect(self):
        # The feet area for landing
        return pygame.Rect(int(self.x), int(self.y) + self.height - 4, self.width, 4)


class Block:
    def __init__(self, x, y, block_type="brick"):
        self.x = x
        self.y = y
        self.width = BLOCK_SIZE
        self.height = BLOCK_SIZE
        self.block_type = block_type  # "brick" or "question"
        self.alive = True
        self.hit_animation = 0
        self.has_reward = True if block_type == "question" else False

    def hit(self):
        if self.block_type == "question" and self.has_reward:
            self.has_reward = False
            self.hit_animation = 10
            return "coin"
        elif self.block_type == "brick":
            self.alive = False
            return "smash"
        return None

    def update(self):
        if self.hit_animation > 0:
            self.hit_animation -= 1

    def draw(self, screen):
        if not self.alive:
            return

        if self.block_type == "question":
            color = QUESTION_BLOCK_HIT_COLOR if not self.has_reward else QUESTION_BLOCK_COLOR
            pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (int(self.x), int(self.y), self.width, self.height), 2)

            # Draw question mark if still has reward
            if self.has_reward:
                font = pygame.font.Font(None, 28)
                text = font.render("?", True, (255, 255, 255))
                screen.blit(text, (int(self.x) + 12, int(self.y) + 6))
        else:
            # Brick
            pygame.draw.rect(screen, BRICK_COLOR, (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (int(self.x), int(self.y), self.width, self.height), 2)
            # Brick lines
            pygame.draw.line(screen, (0, 0, 0), (int(self.x), int(self.y) + 20), (int(self.x) + self.width, int(self.y) + 20), 1)
            pygame.draw.line(screen, (0, 0, 0), (int(self.x) + 20, int(self.y)), (int(self.x) + 20, int(self.y) + 20), 1)

        # Bounce animation
        if self.hit_animation > 0:
            offset = (10 - self.hit_animation) // 2
            pygame.draw.rect(screen, (255, 255, 255), (int(self.x), int(self.y) - offset, self.width, self.height), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = -8
        self.life = 30
        self.radius = 12

    def update(self):
        self.vel_y += GRAVITY * 0.5
        self.y += self.vel_y
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        alpha = min(255, self.life * 10)
        coin_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(coin_surface, (255, 215, 0, alpha), (self.radius, self.radius), self.radius)
        pygame.draw.circle(coin_surface, (255, 255, 0, alpha), (self.radius - 3, self.radius - 3), 4)
        screen.blit(coin_surface, (int(self.x) - self.radius, int(self.y) - self.radius))
