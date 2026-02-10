"""
Vector Frogger: Lilypad Hop
A grid-based river crossing game where a frog navigates moving lilypads.
"""

import pygame
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class Lilypad:
    row: int
    col: float
    width: int
    speed: float


class GameConfig:
    WIDTH = 400
    HEIGHT = 600
    GRID_SIZE = 40
    FPS = 60

    # Colors
    COLOR_WATER = (30, 100, 180)
    COLOR_BANK = (50, 150, 50)
    COLOR_LILYPAD = (34, 139, 34)
    COLOR_FROG = (50, 205, 50)
    COLOR_FROG_OUTLINE = (20, 100, 20)
    COLOR_TEXT = (255, 255, 255)

    # Game settings
    BANK_HEIGHT = 2  # rows
    RIVER_ROWS = 10
    LILYPAD_MIN_WIDTH = 2
    LILYPAD_MAX_WIDTH = 4


class GameState:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.game_over = False
        self.won = False
        self.high_score = 0

    def reset(self):
        self.score = 0
        self.level = 1
        self.game_over = False
        self.won = False


class Frog:
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.world_x = grid_x * GameConfig.GRID_SIZE
        self.reset(grid_x, grid_y)

    def reset(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.world_x = grid_x * GameConfig.GRID_SIZE

    def move(self, direction: Direction, max_x: int, max_y: int):
        dx, dy = direction.value
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if 0 <= new_x < max_x and 0 <= new_y < max_y:
            self.grid_x = new_x
            self.grid_y = new_y
            self.world_x = self.grid_x * GameConfig.GRID_SIZE
            return True
        return False

    def update_world_x(self, speed: float):
        self.world_x += speed


class LilypadRow:
    def __init__(self, row: int, speed: float, pad_count: int, direction: int):
        self.row = row
        self.speed = speed * direction
        self.pads: List[Lilypad] = []
        self._generate_pads(pad_count)

    def _generate_pads(self, count: int):
        import random
        self.pads = []
        spacing = GameConfig.WIDTH // count

        for i in range(count):
            width = random.randint(
                GameConfig.LILYPAD_MIN_WIDTH,
                GameConfig.LILYPAD_MAX_WIDTH
            )
            offset = random.randint(0, spacing // 2)
            col = (i * spacing + offset) / GameConfig.GRID_SIZE
            self.pads.append(Lilypad(self.row, col, width, self.speed))

    def update(self):
        for pad in self.pads:
            pad.col += pad.speed / GameConfig.GRID_SIZE

            # Wrap around
            if self.speed > 0:
                if pad.col * GameConfig.GRID_SIZE > GameConfig.WIDTH:
                    pad.col = -pad.width
            else:
                if (pad.col + pad.width) * GameConfig.GRID_SIZE < 0:
                    pad.col = GameConfig.WIDTH / GameConfig.GRID_SIZE

    def get_pad_at(self, world_x: float) -> Optional[Lilypad]:
        grid_x = world_x / GameConfig.GRID_SIZE
        for pad in self.pads:
            if pad.col <= grid_x < pad.col + pad.width:
                return pad
        return None


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption("Vector Frogger: Lilypad Hop")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.grid_cols = GameConfig.WIDTH // GameConfig.GRID_SIZE
        self.grid_rows = GameConfig.HEIGHT // GameConfig.GRID_SIZE

        self.state = GameState()
        self.frog = Frog(self.grid_cols // 2, self.grid_rows - GameConfig.BANK_HEIGHT)
        self.rows: List[LilypadRow] = []

        self._init_level()

    def _init_level(self):
        import random

        self.rows = []
        river_start = GameConfig.BANK_HEIGHT
        river_end = river_start + GameConfig.RIVER_ROWS

        for row in range(river_start, river_end):
            speed_mult = 1.0 + (self.state.level - 1) * 0.2
            speed = random.uniform(1.0, 2.0) * speed_mult
            direction = 1 if random.random() > 0.5 else -1
            pad_count = max(2, 4 - self.state.level // 2)

            self.rows.append(LilypadRow(row, speed, pad_count, direction))

    def reset(self):
        self.state.reset()
        self.frog.reset(self.grid_cols // 2, self.grid_rows - GameConfig.BANK_HEIGHT)
        self._init_level()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state.game_over or self.state.won:
                    if event.key == pygame.K_SPACE:
                        self.reset()
                    continue

                moved = False
                if event.key == pygame.K_UP:
                    moved = self.frog.move(Direction.UP, self.grid_cols, self.grid_rows)
                elif event.key == pygame.K_DOWN:
                    moved = self.frog.move(Direction.DOWN, self.grid_cols, self.grid_rows)
                elif event.key == pygame.K_LEFT:
                    moved = self.frog.move(Direction.LEFT, self.grid_cols, self.grid_rows)
                elif event.key == pygame.K_RIGHT:
                    moved = self.frog.move(Direction.RIGHT, self.grid_cols, self.grid_rows)

                if moved:
                    if event.key == pygame.K_UP:
                        self.state.score += 10

        return True

    def update(self):
        if self.state.game_over or self.state.won:
            return

        # Update lilypad rows
        for row in self.rows:
            row.update()

        # Check if frog is on a lilypad
        frog_in_river = GameConfig.BANK_HEIGHT <= self.frog.grid_y < GameConfig.BANK_HEIGHT + GameConfig.RIVER_ROWS

        if frog_in_river:
            row_idx = self.frog.grid_y - GameConfig.BANK_HEIGHT
            row = self.rows[row_idx]
            pad = row.get_pad_at(self.frog.world_x)

            if pad:
                # Frog rides the lilypad
                self.frog.update_world_x(row.speed)

                # Check if frog went off screen
                if (self.frog.world_x < -GameConfig.GRID_SIZE or
                    self.frog.world_x > GameConfig.WIDTH):
                    self.state.game_over = True
            else:
                # Frog is in water
                self.state.game_over = True

        # Check win condition
        if self.frog.grid_y < GameConfig.BANK_HEIGHT:
            self.state.won = True
            self.state.score += 100
            if self.state.score > self.state.high_score:
                self.state.high_score = self.state.score

    def draw(self):
        # Draw water
        self.screen.fill(GameConfig.COLOR_WATER)

        # Draw banks
        bank_rect_bottom = pygame.Rect(
            0, GameConfig.HEIGHT - GameConfig.BANK_HEIGHT * GameConfig.GRID_SIZE,
            GameConfig.WIDTH, GameConfig.BANK_HEIGHT * GameConfig.GRID_SIZE
        )
        pygame.draw.rect(self.screen, GameConfig.COLOR_BANK, bank_rect_bottom)

        bank_rect_top = pygame.Rect(
            0, 0,
            GameConfig.WIDTH, GameConfig.BANK_HEIGHT * GameConfig.GRID_SIZE
        )
        pygame.draw.rect(self.screen, GameConfig.COLOR_BANK, bank_rect_top)

        # Draw lilypads
        for row in self.rows:
            for pad in row.pads:
                rect = pygame.Rect(
                    pad.col * GameConfig.GRID_SIZE,
                    row.row * GameConfig.GRID_SIZE,
                    pad.width * GameConfig.GRID_SIZE,
                    GameConfig.GRID_SIZE
                )
                pygame.draw.ellipse(self.screen, GameConfig.COLOR_LILYPAD, rect)

        # Draw frog
        frog_screen_y = self.frog.grid_y * GameConfig.GRID_SIZE
        frog_size = GameConfig.GRID_SIZE - 4
        frog_rect = pygame.Rect(
            self.frog.world_x + 2,
            frog_screen_y + 2,
            frog_size,
            frog_size
        )
        pygame.draw.ellipse(self.screen, GameConfig.COLOR_FROG, frog_rect)
        pygame.draw.ellipse(self.screen, GameConfig.COLOR_FROG_OUTLINE, frog_rect, 2)

        # Draw eyes
        eye_size = 6
        eye_y = frog_screen_y + 8
        left_eye_x = self.frog.world_x + 10
        right_eye_x = self.frog.world_x + GameConfig.GRID_SIZE - 16
        pygame.draw.circle(self.screen, (255, 255, 255), (int(left_eye_x), eye_y), eye_size)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(right_eye_x), eye_y), eye_size)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(left_eye_x), eye_y), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(right_eye_x), eye_y), 3)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.state.score}", True, GameConfig.COLOR_TEXT)
        level_text = self.font.render(f"Level: {self.state.level}", True, GameConfig.COLOR_TEXT)

        # Draw text background
        bg_rect = pygame.Rect(5, 5, 200, 60)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))

        # Draw game over / win message
        if self.state.game_over:
            msg = self.font.render("GAME OVER - Press SPACE", True, GameConfig.COLOR_TEXT)
            text_rect = msg.get_rect(center=(GameConfig.WIDTH // 2, GameConfig.HEIGHT // 2))
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 20))
            self.screen.blit(msg, text_rect)
        elif self.state.won:
            msg = self.font.render(f"WON! Score: {self.state.score} - SPACE", True, GameConfig.COLOR_TEXT)
            text_rect = msg.get_rect(center=(GameConfig.WIDTH // 2, GameConfig.HEIGHT // 2))
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 20))
            self.screen.blit(msg, text_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(GameConfig.FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
