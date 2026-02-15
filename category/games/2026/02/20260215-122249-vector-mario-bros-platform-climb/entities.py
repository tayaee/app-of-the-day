import pygame
from config import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.climbing = False
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.tier_reached = set()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.get_rect())
        pygame.draw.rect(screen, (200, 50, 50), (self.x + 4, self.y + 4, self.width - 8, 4))
        pygame.draw.rect(screen, (200, 50, 50), (self.x + 4, self.y + 10, 4, 4))

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, PLATFORM_COLOR, self.get_rect())
        pygame.draw.rect(screen, (100, 50, 10), (self.x, self.y, self.width, 4))

class Ladder:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, LADDER_COLOR, self.get_rect())
        for i in range(0, self.height, 12):
            pygame.draw.line(screen, (80, 80, 80),
                           (self.x, self.y + i),
                           (self.x + self.width, self.y + i), 2)

class Obstacle:
    def __init__(self, x, y, tier, speed):
        self.x = x
        self.y = y
        self.tier = tier
        self.speed = speed
        self.radius = OBSTACLE_RADIUS

    def update(self):
        self.x += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

    def is_off_screen(self, screen_width):
        return (self.speed > 0 and self.x > screen_width + self.radius) or \
               (self.speed < 0 and self.x < -self.radius)

    def draw(self, screen):
        pygame.draw.circle(screen, OBSTACLE_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 200, 100), (int(self.x - 2), int(self.y - 2)), self.radius // 2)

class Elevator:
    def __init__(self, x, y_start, y_end, width, height):
        self.x = x
        self.y = y_start
        self.y_start = y_start
        self.y_end = y_end
        self.width = width
        self.height = height
        self.speed = 1.5
        self.moving_up = True

    def update(self):
        if self.moving_up:
            self.y -= self.speed
            if self.y <= self.y_end:
                self.moving_up = False
        else:
            self.y += self.speed
            if self.y >= self.y_start:
                self.moving_up = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 150), self.get_rect())
        pygame.draw.rect(screen, (80, 80, 120), (self.x + 4, self.y + 4, self.width - 8, 4))
