import pygame
import random
from config import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.alive = True

    def move(self, dx):
        new_x = self.x + dx
        if 0 <= new_x <= SCREEN_WIDTH - self.width:
            self.x = new_x

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.polygon(screen, PLAYER_COLOR, [
            (self.x + 5, self.y),
            (self.x + self.width // 2, self.y - 10),
            (self.x + self.width - 5, self.y)
        ])

    def get_rect(self):
        return pygame.Rect(self.x, self.y - 10, self.width, self.height + 10)

class Bullet:
    def __init__(self, x, y, speed, color=BULLET_COLOR):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = speed
        self.color = color
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Alien:
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        self.width = ALIEN_WIDTH
        self.height = ALIEN_HEIGHT
        self.row = row
        self.color = ALIEN_COLORS[min(row // 2, 2)]
        self.alive = True
        self.frame = 0

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        eye_color = (0, 0, 0)
        pygame.draw.rect(screen, eye_color, (self.x + 8, self.y + 8, 4, 4))
        pygame.draw.rect(screen, eye_color, (self.x + self.width - 12, self.y + 8, 4, 4))
        pygame.draw.rect(screen, eye_color, (self.x + 10, self.y + 16, 10, 3))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_points(self):
        if self.row < 1:
            return POINTS_TOP_ROW
        elif self.row < 3:
            return POINTS_MID_ROW
        return POINTS_BOTTOM_ROW

class Bunker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BUNKER_WIDTH
        self.height = BUNKER_HEIGHT
        self.health = 4

    def draw(self, screen):
        alpha = int(255 * (self.health / 4))
        color = (*BUNKER_COLOR,)
        size = int(self.width * (self.health / 4))
        offset = (self.width - size) // 2
        pygame.draw.rect(screen, color, (self.x + offset, self.y, size, self.height))

    def get_rect(self):
        size = int(self.width * (self.health / 4))
        offset = (self.width - size) // 2
        return pygame.Rect(self.x + offset, self.y, size, self.height)

    def hit(self):
        self.health -= 1
        return self.health <= 0

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = (random.random() - 0.5) * 6
        self.vy = (random.random() - 0.5) * 6
        self.life = 30
        self.color = color
        self.size = 3

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / 30))
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))
