import random
import pygame
from config import *

class MathProblem:
    def __init__(self, max_number=MAX_NUMBER_BASE):
        self.max_number = max_number
        self.generate_problem()

    def generate_problem(self):
        self.operation = random.choice(['+', '-'])
        if self.operation == '+':
            self.num1 = random.randint(1, self.max_number)
            self.num2 = random.randint(1, self.max_number)
            self.answer = self.num1 + self.num2
        else:
            self.num1 = random.randint(2, self.max_number)
            self.num2 = random.randint(1, self.num1)
            self.answer = self.num1 - self.num2

    def __str__(self):
        return f"{self.num1} {self.operation} {self.num2} = ?"

    def increase_difficulty(self):
        self.max_number += MAX_NUMBER_INCREMENT
        self.generate_problem()

class LilyPad:
    def __init__(self, x, row, speed, value, is_correct=False):
        self.x = float(x)
        self.row = row
        self.speed = speed
        self.value = value
        self.is_correct = is_correct
        self.radius = GRID_SIZE // 2 - 5

    def update(self):
        self.x += self.speed
        if self.speed > 0:
            if self.x > SCREEN_WIDTH + GRID_SIZE:
                self.x = -GRID_SIZE
        else:
            if self.x < -GRID_SIZE:
                self.x = SCREEN_WIDTH + GRID_SIZE

    def get_rect(self):
        y = self.row * GRID_SIZE
        return (int(self.x), int(y), GRID_SIZE - 10, GRID_SIZE - 10)

    def draw(self, surface, font):
        x, y, w, h = self.get_rect()
        center_x = x + w // 2
        center_y = y + h // 2

        color = (80, 220, 100) if self.is_correct else COLOR_LILY_PAD
        pygame.draw.circle(surface, color, (center_x, center_y), self.radius)
        pygame.draw.circle(surface, (30, 120, 50), (center_x, center_y), self.radius, 3)

        # Draw number
        text = font.render(str(self.value), True, COLOR_TEXT_DARK)
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)

class Frog:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid_x = GRID_COLS // 2
        self.grid_y = GRID_ROWS - 1
        self.on_lily_pad = None
        self.alive = True
        self.sinking = False
        self.sink_timer = 0

    def move(self, dx, dy):
        if not self.alive:
            return False

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
            self.grid_x = new_x
            self.grid_y = new_y
            return True
        return False

    def get_pos(self):
        if self.on_lily_pad:
            return self.on_lily_pad.x + GRID_SIZE // 2, self.grid_y * GRID_SIZE + GRID_SIZE // 2
        return self.grid_x * GRID_SIZE + GRID_SIZE // 2, self.grid_y * GRID_SIZE + GRID_SIZE // 2

    def sink(self):
        self.sinking = True
        self.alive = False

    def draw(self, surface):
        x, y = self.get_pos()
        size = GRID_SIZE // 2 - 5

        if self.sinking:
            self.sink_timer += 1
            y += self.sink_timer * 2

        body = pygame.Rect(x - size, y - size // 2, size * 2, size)
        pygame.draw.ellipse(surface, COLOR_FROG, body)
        pygame.draw.ellipse(surface, COLOR_FROG_OUTLINE, body, 2)

        head_size = size // 1.5
        head = pygame.Rect(x - head_size // 2, y - size // 2 - head_size // 2, head_size, head_size)
        pygame.draw.circle(surface, COLOR_FROG, (int(x), int(y - size // 2 - head_size // 4)), int(head_size // 2))
        pygame.draw.circle(surface, COLOR_FROG_OUTLINE, (int(x), int(y - size // 2 - head_size // 4)), int(head_size // 2), 2)

        eye_offset = head_size // 4
        eye_size = head_size // 5
        pygame.draw.circle(surface, COLOR_TEXT_DARK, (int(x - eye_offset), int(y - size // 2 - head_size // 4 - eye_offset // 2)), eye_size)
        pygame.draw.circle(surface, COLOR_TEXT_DARK, (int(x + eye_offset), int(y - size // 2 - head_size // 4 - eye_offset // 2)), eye_size)
