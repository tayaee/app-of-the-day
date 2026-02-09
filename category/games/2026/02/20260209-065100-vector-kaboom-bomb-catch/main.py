"""
Vector Kaboom: Bomb Catch
A high-speed reaction game where you catch falling bombs from the Mad Bomber.
"""

import pygame
import random
import math
from typing import List, Tuple


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 50, 50)
COLOR_CYAN = (0, 255, 255)
COLOR_YELLOW = (255, 255, 0)

# Game settings
BUCKET_WIDTH = 80
BUCKET_HEIGHT = 25
BUCKET_COUNT = 3
BUCKET_SPACING = 30
BUCKET_START_Y = SCREEN_HEIGHT - 50

BOMBER_WIDTH = 50
BOMBER_HEIGHT = 30
BOMBER_Y = 50
BOMB_RADIUS = 12
BOMB_SPEED_BASE = 2
BOMB_SPEED_MAX = 8

PLAYER_SPEED = 8
PLAYER_WIDTH = BUCKET_WIDTH
PLAYER_HEIGHT = BUCKET_COUNT * (BUCKET_HEIGHT + BUCKET_SPACING) - BUCKET_SPACING

# Scoring
SCORE_CATCH = 10
SCORE_SURVIVE = 1
PENALTY_MISS = -50


class Bomb:
    """A falling bomb dropped by the Mad Bomber."""

    def __init__(self, x: float, y: float, speed: float):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = BOMB_RADIUS
        self.active = True
        self.wobble_phase = random.uniform(0, math.pi * 2)

    def update(self) -> None:
        """Update bomb position."""
        self.y += self.speed
        # Add slight horizontal wobble for visual interest
        self.x += math.sin(self.wobble_phase) * 0.5
        self.wobble_phase += 0.1

        # Remove if off screen
        if self.y > SCREEN_HEIGHT + self.radius:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bomb as a red circle with a fuse."""
        # Bomb body
        pygame.draw.circle(surface, COLOR_RED, (int(self.x), int(self.y)), self.radius)
        # Inner highlight
        pygame.draw.circle(surface, (255, 150, 150), (int(self.x - 3), int(self.y - 3)), 4)
        # Fuse
        fuse_end_x = self.x + math.cos(self.wobble_phase) * 8
        fuse_end_y = self.y - 8 + math.sin(self.wobble_phase) * 2
        pygame.draw.line(surface, COLOR_YELLOW, (self.x, self.y - self.radius),
                         (fuse_end_x, fuse_end_y), 2)

    def get_rect(self) -> pygame.Rect:
        """Get collision rect for the bomb."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)


class Bucket:
    """A single bucket that can catch one bomb."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = BUCKET_WIDTH
        self.height = BUCKET_HEIGHT
        self.active = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bucket as a cyan trapezoid."""
        if not self.active:
            return

        # Trapezoid shape
        top_left = (self.x, self.y)
        top_right = (self.x + self.width, self.y)
        bottom_left = (self.x + 10, self.y + self.height)
        bottom_right = (self.x + self.width - 10, self.y + self.height)

        points = [top_left, top_right, bottom_right, bottom_left]
        pygame.draw.polygon(surface, COLOR_CYAN, points)
        pygame.draw.polygon(surface, COLOR_WHITE, points, 2)

    def get_rect(self) -> pygame.Rect:
        """Get collision rect for the bucket."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Player:
    """The player controlling three stacked buckets."""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - BUCKET_WIDTH // 2
        self.y = BUCKET_START_Y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.buckets: List[Bucket] = []

        # Create stacked buckets
        for i in range(BUCKET_COUNT):
            bucket_y = self.y - i * (BUCKET_HEIGHT + BUCKET_SPACING)
            self.buckets.append(Bucket(self.x, bucket_y))

    def move(self, dx: float) -> None:
        """Move player horizontally, keeping within bounds."""
        self.x += dx
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

        # Update bucket positions
        for bucket in self.buckets:
            bucket.x = self.x

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all active buckets."""
        for bucket in self.buckets:
            bucket.draw(surface)

    def get_catch_rects(self) -> List[pygame.Rect]:
        """Get collision rects for all active buckets."""
        return [bucket.get_rect() for bucket in self.buckets if bucket.active]

    def lose_bucket(self) -> bool:
        """Lose one bucket. Returns False if all buckets are gone."""
        for bucket in reversed(self.buckets):
            if bucket.active:
                bucket.active = False
                return True
        return False

    def get_active_count(self) -> int:
        """Get number of active buckets remaining."""
        return sum(1 for b in self.buckets if b.active)


class Bomber:
    """The Mad Bomber who moves and drops bombs."""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = BOMBER_Y
        self.width = BOMBER_WIDTH
        self.height = BOMBER_HEIGHT
        self.speed = 2
        self.direction = 1
        self.drop_timer = 0
        self.drop_interval = 120  # Frames between drops
        self.move_pause_timer = 0
        self.is_paused = False

    def update(self, difficulty_multiplier: float) -> Tuple[float, float]:
        """Update bomber position. Returns (x, y) if bomb dropped, else (None, None)."""
        # Adjust speed based on difficulty
        actual_speed = self.speed * difficulty_multiplier

        if self.is_paused:
            self.move_pause_timer -= 1
            if self.move_pause_timer <= 0:
                self.is_paused = False
            return None, None

        # Move horizontally
        self.x += actual_speed * self.direction

        # Reverse direction at edges
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction *= -1
            self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

        # Random pause for dropping bomb
        if random.random() < 0.02:
            self.is_paused = True
            self.move_pause_timer = random.randint(20, 40)

        # Drop bomb timer
        self.drop_timer += 1
        adjusted_interval = max(30, int(self.drop_interval / difficulty_multiplier))

        if self.drop_timer >= adjusted_interval and self.is_paused:
            self.drop_timer = 0
            return self.x + self.width // 2, self.y + self.height

        return None, None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bomber as a white figure."""
        # Body (rectangle)
        body_rect = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLOR_WHITE, body_rect)
        pygame.draw.rect(surface, COLOR_WHITE, body_rect, 2)

        # Eyes
        eye_y = self.y + 10
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + 15), eye_y), 4)
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.x + 35), eye_y), 4)

        # Angry eyebrows
        pygame.draw.line(surface, COLOR_BLACK, (self.x + 10, eye_y - 8),
                        (self.x + 20, eye_y - 4), 2)
        pygame.draw.line(surface, COLOR_BLACK, (self.x + 30, eye_y - 4),
                        (self.x + 40, eye_y - 8), 2)

    def get_center_x(self) -> float:
        """Get bomber center X position."""
        return self.x + self.width // 2


class Game:
    """Main game class managing all game state."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Kaboom: Bomb Catch")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.player = Player()
        self.bomber = Bomber()
        self.bombs: List[Bomb] = []
        self.score = 0
        self.difficulty = 1.0
        self.game_over = False
        self.survival_frames = 0

    def handle_input(self) -> None:
        """Handle keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
            elif event.type == pygame.MOUSEMOTION and not self.game_over:
                # Mouse control - center player on mouse
                mouse_x = event.pos[0]
                self.player.x = mouse_x - self.player.width // 2
                self.player.x = max(0, min(SCREEN_WIDTH - self.player.width, self.player.x))
                for bucket in self.player.buckets:
                    bucket.x = self.player.x

        # Keyboard control
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move(-PLAYER_SPEED)
            if keys[pygame.K_RIGHT]:
                self.player.move(PLAYER_SPEED)

    def update(self) -> None:
        """Update game state."""
        if self.game_over:
            return

        self.survival_frames += 1

        # Increase difficulty over time
        self.difficulty = 1.0 + (self.score / 200) + (self.survival_frames / 10000)

        # Update bomber
        bomb_x, bomb_y = self.bomber.update(self.difficulty)
        if bomb_x is not None:
            bomb_speed = min(BOMB_SPEED_MAX, BOMB_SPEED_BASE + self.difficulty * 0.5)
            self.bombs.append(Bomb(bomb_x, bomb_y, bomb_speed))

        # Update bombs
        for bomb in self.bombs[:]:
            bomb.update()

            # Check collision with buckets
            caught = False
            for i, bucket in enumerate(self.player.buckets):
                if bucket.active and bomb.get_rect().colliderect(bucket.get_rect()):
                    # Bomb caught by this bucket
                    self.score += SCORE_CATCH
                    self.bombs.remove(bomb)
                    caught = True
                    break

            if caught:
                continue

            # Check if bomb hit ground
            if not bomb.active:
                self.bombs.remove(bomb)
                if not self.player.lose_bucket():
                    self.game_over = True

        # Survival points
        if self.survival_frames % 60 == 0:
            self.score += SCORE_SURVIVE

    def draw(self) -> None:
        """Draw all game elements."""
        self.screen.fill(COLOR_BLACK)

        if not self.game_over:
            # Draw game elements
            self.bomber.draw(self.screen)
            self.player.draw(self.screen)
            for bomb in self.bombs:
                bomb.draw(self.screen)

            # Draw ground line
            pygame.draw.line(self.screen, COLOR_WHITE, (0, SCREEN_HEIGHT - 1),
                           (SCREEN_WIDTH, SCREEN_HEIGHT - 1), 2)

        # Draw UI
        score_text = self.font_small.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw remaining buckets indicator
        bucket_text = self.font_small.render(f"BUCKETS: {self.player.get_active_count()}",
                                           True, COLOR_CYAN)
        self.screen.blit(bucket_text, (10, 45))

        if self.game_over:
            # Game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(COLOR_BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, COLOR_RED)
            score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_WHITE)
            restart_text = self.font_small.render("Press R to Restart or ESC to Quit",
                                                True, COLOR_YELLOW)

            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
