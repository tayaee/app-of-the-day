"""
Vector Space Invaders - Simple Swarm
A vector-style arcade shooter where you defend Earth from descending alien swarms.
"""

import pygame
import sys
import random
from typing import List, Tuple, Optional

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Vector style - neon on dark background)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Game Rules
PLAYER_SPEED = 5
BULLET_SPEED = 7
ALIEN_HORIZONTAL_SPEED = 2
ALIEN_VERTICAL_DROP = 20
ALIEN_FIRE_RATE = 0.01
GRID_ROWS = 5
GRID_COLS = 8
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
ALIEN_PADDING = 15

# Scoring
SCORE_BOTTOM_ROW = 10
SCORE_MIDDLE_ROW = 20
SCORE_TOP_ROW = 30


class Vector:
    """Simple 2D vector class for position and velocity calculations."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def to_tuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))


class Player:
    """Player-controlled tank at the bottom of the screen."""

    def __init__(self, screen_width: int, screen_height: int):
        self.width = 50
        self.height = 30
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 60
        self.speed = PLAYER_SPEED
        self.screen_width = screen_width
        self.can_shoot = True

    def move(self, direction: int) -> None:
        """Move player left (-1) or right (1)."""
        self.x += direction * self.speed
        self.x = max(0, min(self.screen_width - self.width, self.x))

    def get_center(self) -> Tuple[int, int]:
        """Return center point of player for bullet spawn."""
        return (self.x + self.width // 2, self.y)

    def get_rect(self) -> pygame.Rect:
        """Return collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw player tank in vector style."""
        # Tank body
        points = [
            (self.x, self.y + self.height),
            (self.x, self.y + 10),
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + 10),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.lines(surface, GREEN, False, points, 2)
        pygame.draw.line(surface, GREEN, (self.x + 5, self.y + self.height),
                        (self.x + self.width - 5, self.y + self.height), 2)


class Bullet:
    """Projectile fired by player or aliens."""

    def __init__(self, x: int, y: int, speed: int, is_player: bool = True):
        self.pos = Vector(x, y)
        self.speed = speed
        self.is_player = is_player
        self.width = 4
        self.height = 12
        self.active = True

    def update(self) -> None:
        """Update bullet position."""
        if self.is_player:
            self.pos.y -= self.speed
        else:
            self.pos.y += self.speed

        # Deactivate if off screen
        if self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT:
            self.active = False

    def get_rect(self) -> pygame.Rect:
        """Return collision rectangle."""
        return pygame.Rect(
            int(self.pos.x - self.width // 2),
            int(self.pos.y),
            self.width,
            self.height
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw bullet in vector style."""
        color = CYAN if self.is_player else RED
        rect = self.get_rect()
        pygame.draw.rect(surface, color, rect)


class Alien:
    """Single alien invader."""

    def __init__(self, x: int, y: int, row: int):
        self.x = x
        self.y = y
        self.width = ALIEN_WIDTH
        self.height = ALIEN_HEIGHT
        self.row = row
        self.active = True

        # Score based on row (top rows worth more)
        if row < 2:
            self.score = SCORE_TOP_ROW
        elif row < 4:
            self.score = SCORE_MIDDLE_ROW
        else:
            self.score = SCORE_BOTTOM_ROW

    def move(self, dx: int, dy: int) -> None:
        """Move alien by given offset."""
        self.x += dx
        self.y += dy

    def get_rect(self) -> pygame.Rect:
        """Return collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw alien in vector style - different shapes per row."""
        color = WHITE
        points = []

        if self.row == 0:
            # Top row: squid shape
            points = [
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height // 2),
                (self.x + self.width - 5, self.y + self.height),
                (self.x + 5, self.y + self.height),
                (self.x, self.y + self.height // 2)
            ]
        elif self.row == 1:
            # Second row: octopus shape
            points = [
                (self.x + 5, self.y),
                (self.x + self.width - 5, self.y),
                (self.x + self.width, self.y + self.height // 2),
                (self.x + self.width - 8, self.y + self.height),
                (self.x + 8, self.y + self.height),
                (self.x, self.y + self.height // 2)
            ]
        else:
            # Bottom rows: crab shape
            points = [
                (self.x + 10, self.y),
                (self.x + self.width - 10, self.y),
                (self.x + self.width, self.y + self.height - 5),
                (self.x + self.width - 5, self.y + self.height),
                (self.x + 5, self.y + self.height),
                (self.x, self.y + self.height - 5)
            ]

        pygame.draw.lines(surface, color, True, points, 2)
        # Eyes
        pygame.draw.circle(surface, color, (self.x + self.width // 3, self.y + self.height // 2), 3)
        pygame.draw.circle(surface, color, (self.x + 2 * self.width // 3, self.y + self.height // 2), 3)


class AlienSwarm:
    """Manages the grid of alien invaders."""

    def __init__(self, screen_width: int):
        self.screen_width = screen_width
        self.aliens: List[List[Optional[Alien]]] = []
        self.direction = 1  # 1 for right, -1 for left
        self.speed = ALIEN_HORIZONTAL_SPEED
        self.setup_grid()

    def setup_grid(self) -> None:
        """Create initial grid of aliens."""
        start_x = (self.screen_width - (GRID_COLS * (ALIEN_WIDTH + ALIEN_PADDING))) // 2
        start_y = 50

        for row in range(GRID_ROWS):
            alien_row = []
            for col in range(GRID_COLS):
                x = start_x + col * (ALIEN_WIDTH + ALIEN_PADDING)
                y = start_y + row * (ALIEN_HEIGHT + ALIEN_PADDING)
                alien_row.append(Alien(x, y, row))
            self.aliens.append(alien_row)

    def update(self) -> Tuple[int, bool]:
        """Update swarm position. Returns (y_drop, game_over)."""
        should_drop = False
        game_over = False
        min_y = float('inf')

        # Find boundaries and check positions
        leftmost = self.screen_width
        rightmost = 0
        active_count = 0

        for row in self.aliens:
            for alien in row:
                if alien:
                    leftmost = min(leftmost, alien.x)
                    rightmost = max(rightmost, alien.x + alien.width)
                    min_y = min(min_y, alien.y + alien.height)
                    active_count += 1

        # Check if aliens reached player level
        if min_y >= SCREEN_HEIGHT - 80:
            game_over = True

        # Check boundaries and move
        hit_boundary = False
        if rightmost >= self.screen_width - 10 and self.direction == 1:
            hit_boundary = True
        elif leftmost <= 10 and self.direction == -1:
            hit_boundary = True

        if hit_boundary:
            self.direction *= -1
            should_drop = True

        drop_amount = ALIEN_VERTICAL_DROP if should_drop else 0

        for row in self.aliens:
            for alien in row:
                if alien:
                    alien.move(self.direction * self.speed, drop_amount)

        return (drop_amount, game_over)

    def get_active_aliens(self) -> List[Alien]:
        """Return list of all active aliens."""
        return [alien for row in self.aliens for alien in row if alien]

    def get_random_shooter(self) -> Optional[Alien]:
        """Return a random alien that can shoot (bottom of each column)."""
        shooters = []
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS - 1, -1, -1):
                if self.aliens[row][col]:
                    shooters.append(self.aliens[row][col])
                    break
        return random.choice(shooters) if shooters else None

    def remove_alien(self, alien: Alien) -> None:
        """Remove alien from grid."""
        for row in self.aliens:
            for i, a in enumerate(row):
                if a == alien:
                    row[i] = None
                    return

    def is_cleared(self) -> bool:
        """Check if all aliens are destroyed."""
        return len(self.get_active_aliens()) == 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all active aliens."""
        for alien in self.get_active_aliens():
            alien.draw(surface)


class Star:
    """Background star for depth effect."""

    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.brightness = random.randint(50, 200)

    def update(self) -> None:
        """Move star downward."""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw star."""
        color = (self.brightness, self.brightness, self.brightness)
        surface.set_at((int(self.x), int(self.y)), color)


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vector Space Invaders")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.player = Player(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.swarm = AlienSwarm(SCREEN_WIDTH)
        self.player_bullets: List[Bullet] = []
        self.alien_bullets: List[Bullet] = []
        self.stars = [Star() for _ in range(50)]
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.wave = 1

    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.player.can_shoot and not self.game_over:
                    bullet_pos = self.player.get_center()
                    self.player_bullets.append(Bullet(bullet_pos[0], bullet_pos[1], BULLET_SPEED, True))
                    self.player.can_shoot = False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

        # Continuous key handling
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move(-1)
            if keys[pygame.K_RIGHT]:
                self.player.move(1)

        return True

    def update(self) -> None:
        """Update game state."""
        # Update stars
        for star in self.stars:
            star.update()

        if self.game_over:
            return

        # Update swarm
        _, swarm_game_over = self.swarm.update()
        if swarm_game_over:
            self.game_over = True

        # Check for wave clear
        if self.swarm.is_cleared():
            self.wave += 1
            self.swarm = AlienSwarm(SCREEN_WIDTH)

        # Alien shooting
        if random.random() < ALIEN_FIRE_RATE:
            shooter = self.swarm.get_random_shooter()
            if shooter:
                bullet_x = shooter.x + shooter.width // 2
                bullet_y = shooter.y + shooter.height
                self.alien_bullets.append(Bullet(bullet_x, bullet_y, BULLET_SPEED - 2, False))

        # Update bullets
        for bullet in self.player_bullets:
            bullet.update()
        for bullet in self.alien_bullets:
            bullet.update()

        # Remove inactive bullets
        self.player_bullets = [b for b in self.player_bullets if b.active]
        self.alien_bullets = [b for b in self.alien_bullets if b.active]

        # Check if player bullet left screen
        if not any(b.active and b.pos.y < 0 for b in self.player_bullets):
            self.player.can_shoot = True

        # Collision detection - player bullets vs aliens
        player_rect = self.player.get_rect()
        for bullet in self.player_bullets:
            if not bullet.active:
                continue
            bullet_rect = bullet.get_rect()

            for alien in self.swarm.get_active_aliens():
                if bullet_rect.colliderect(alien.get_rect()):
                    self.score += alien.score
                    self.swarm.remove_alien(alien)
                    bullet.active = False
                    self.player.can_shoot = True
                    break

        # Collision detection - alien bullets vs player
        for bullet in self.alien_bullets:
            if not bullet.active:
                continue
            if bullet.get_rect().colliderect(player_rect):
                bullet.active = False
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True

        # Collision detection - aliens vs player
        for alien in self.swarm.get_active_aliens():
            if alien.get_rect().colliderect(player_rect):
                self.lives = 0
                self.game_over = True
                break

    def draw(self) -> None:
        """Render game."""
        self.screen.fill(BLACK)

        # Draw stars
        for star in self.stars:
            star.draw(self.screen)

        # Draw game objects
        self.player.draw(self.screen)
        self.swarm.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)
        for bullet in self.alien_bullets:
            bullet.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
        wave_text = self.font.render(f"WAVE: {self.wave}", True, YELLOW)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH // 2 - 50, 10))
        self.screen.blit(wave_text, (SCREEN_WIDTH - 150, 10))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, YELLOW)

            self.screen.blit(game_over_text,
                           (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(final_score_text,
                           (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text,
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main() -> None:
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
