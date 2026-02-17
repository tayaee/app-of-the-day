"""Vector Ball Physics - Physics-based ball navigation game."""

import pygame
import math
from typing import List, Tuple, Optional

# Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics constants
GRAVITY = 0.15
FRICTION = 0.995
RESTITUTION = 0.75
IMPULSE_FORCE = 0.8
MAX_VELOCITY = 15.0

# Colors
COLOR_BG = (20, 20, 25)
COLOR_BALL = (100, 200, 255)
COLOR_BALL_OUTLINE = (150, 220, 255)
COLOR_EXIT = (50, 200, 80)
COLOR_EXIT_OUTLINE = (80, 255, 100)
COLOR_OBSTACLE = (200, 60, 60)
COLOR_OBSTACLE_OUTLINE = (255, 100, 100)
COLOR_COLLECTIBLE = (255, 220, 50)
COLOR_COLLECTIBLE_OUTLINE = (255, 240, 100)
COLOR_TEXT = (220, 220, 220)


class Vector2:
    """Simple 2D vector class for physics calculations."""

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> 'Vector2':
        l = self.length()
        if l > 0:
            return Vector2(self.x / l, self.y / l)
        return Vector2()

    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


class Ball:
    """Player ball with physics-based movement."""

    def __init__(self, x: float, y: float, radius: float = 15):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.radius = radius
        self.start_pos = Vector2(x, y)

    def apply_force(self, fx: float, fy: float):
        """Apply force to the ball."""
        self.acc.x += fx
        self.acc.y += fy

    def update(self):
        """Update physics using Euler integration."""
        # Apply gravity
        self.acc.y += GRAVITY

        # Update velocity
        self.vel += self.acc

        # Apply friction
        self.vel *= FRICTION

        # Limit velocity
        speed = self.vel.length()
        if speed > MAX_VELOCITY:
            self.vel = self.vel.normalize() * MAX_VELOCITY

        # Update position
        self.pos += self.vel

        # Reset acceleration
        self.acc = Vector2()

        # Screen boundary collision
        self.handle_wall_collision()

    def handle_wall_collision(self):
        """Handle collision with screen boundaries."""
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.vel.x *= -RESTITUTION
        elif self.pos.x + self.radius > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH - self.radius
            self.vel.x *= -RESTITUTION

        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.vel.y *= -RESTITUTION
        elif self.pos.y + self.radius > SCREEN_HEIGHT:
            self.pos.y = SCREEN_HEIGHT - self.radius
            self.vel.y *= -RESTITUTION

    def reset(self):
        """Reset ball to starting position."""
        self.pos = Vector2(self.start_pos.x, self.start_pos.y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

    def draw(self, surface):
        """Draw the ball."""
        pygame.draw.circle(surface, COLOR_BALL, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, COLOR_BALL_OUTLINE, (int(self.pos.x), int(self.pos.y)), self.radius, 2)


class Obstacle:
    """Static rectangular obstacle."""

    def __init__(self, x: float, y: float, width: float, height: float):
        self.rect = pygame.Rect(x, y, width, height)
        self.hazard = False

    def check_collision(self, ball: Ball) -> bool:
        """Check and handle collision with ball."""
        closest_x = max(self.rect.left, min(ball.pos.x, self.rect.right))
        closest_y = max(self.rect.top, min(ball.pos.y, self.rect.bottom))

        dist_x = ball.pos.x - closest_x
        dist_y = ball.pos.y - closest_y
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)

        if distance < ball.radius:
            # Collision detected - resolve it
            if distance == 0:
                overlap = ball.radius
                normal = Vector2(1, 0)
            else:
                overlap = ball.radius - distance
                normal = Vector2(dist_x / distance, dist_y / distance)

            # Push ball out
            ball.pos += normal * overlap

            # Reflect velocity
            if abs(normal.x) > abs(normal.y):
                ball.vel.x *= -RESTITUTION
            else:
                ball.vel.y *= -RESTITUTION

            return True
        return False

    def draw(self, surface):
        """Draw the obstacle."""
        color = COLOR_OBSTACLE if self.hazard else (100, 100, 120)
        outline = COLOR_OBSTACLE_OUTLINE if self.hazard else (140, 140, 160)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, outline, self.rect, 2)


class MovingObstacle(Obstacle):
    """Moving rectangular obstacle that acts as a hazard."""

    def __init__(self, x: float, y: float, width: float, height: float,
                 axis: str = 'horizontal', speed: float = 2.0, range_val: float = 100):
        super().__init__(x, y, width, height)
        self.axis = axis
        self.speed = speed
        self.range = range_val
        self.start_pos = Vector2(x, y)
        self.time_offset = 0.0
        self.hazard = True

    def update(self, dt: float):
        """Update position based on oscillation."""
        self.time_offset += dt * 0.002
        offset = math.sin(self.time_offset * self.speed) * self.range

        if self.axis == 'horizontal':
            self.rect.x = self.start_pos.x + offset
        else:
            self.rect.y = self.start_pos.y + offset


class Collectible:
    """Collectible dot for bonus points."""

    def __init__(self, x: float, y: float, radius: float = 8):
        self.pos = Vector2(x, y)
        self.radius = radius
        self.collected = False
        self.pulse_offset = 0.0

    def update(self, dt: float):
        """Update pulse animation."""
        self.pulse_offset += dt * 0.005

    def check_collision(self, ball: Ball) -> bool:
        """Check if ball collects this dot."""
        if self.collected:
            return False

        distance = (ball.pos - self.pos).length()
        if distance < ball.radius + self.radius:
            self.collected = True
            return True
        return False

    def draw(self, surface):
        """Draw the collectible."""
        if self.collected:
            return

        pulse = math.sin(self.pulse_offset) * 2
        r = self.radius + pulse
        pygame.draw.circle(surface, COLOR_COLLECTIBLE, (int(self.pos.x), int(self.pos.y)), int(r))
        pygame.draw.circle(surface, COLOR_COLLECTIBLE_OUTLINE, (int(self.pos.x), int(self.pos.y)), int(r), 2)


class ExitPortal:
    """Goal portal to reach."""

    def __init__(self, x: float, y: float, radius: float = 25):
        self.pos = Vector2(x, y)
        self.radius = radius
        self.pulse_offset = 0.0

    def update(self, dt: float):
        """Update pulse animation."""
        self.pulse_offset += dt * 0.003

    def check_reach(self, ball: Ball) -> bool:
        """Check if ball reaches the exit."""
        distance = (ball.pos - self.pos).length()
        return distance < self.radius + ball.radius * 0.5

    def draw(self, surface):
        """Draw the exit portal."""
        pulse = math.sin(self.pulse_offset) * 3
        r = self.radius + pulse

        # Outer ring
        pygame.draw.circle(surface, COLOR_EXIT, (int(self.pos.x), int(self.pos.y)), int(r))
        pygame.draw.circle(surface, COLOR_EXIT_OUTLINE, (int(self.pos.x), int(self.pos.y)), int(r), 3)

        # Inner ring
        inner_r = r * 0.5
        pygame.draw.circle(surface, COLOR_EXIT_OUTLINE, (int(self.pos.x), int(self.pos.y)), int(inner_r))


class Level:
    """Game level with obstacles, collectibles, and exit."""

    def __init__(self, start_pos: Tuple[float, float],
                 exit_pos: Tuple[float, float],
                 obstacles: List[Obstacle],
                 collectibles: List[Collectible]):
        self.start_pos = start_pos
        self.exit_pos = exit_pos
        self.obstacles = obstacles
        self.collectibles = collectibles
        self.exit = ExitPortal(exit_pos[0], exit_pos[1])


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Ball Physics")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.running = True
        self.game_over = False
        self.level_complete = False
        self.score = 0
        self.current_level = 0
        self.frames_elapsed = 0

        self.levels = self._create_levels()
        self._load_level(0)

    def _create_levels(self) -> List[Level]:
        """Create game levels."""
        levels = []

        # Level 1: Simple navigation
        levels.append(Level(
            start_pos=(100, 500),
            exit_pos=(700, 100),
            obstacles=[
                Obstacle(350, 200, 100, 20),
                Obstacle(200, 350, 20, 150),
                Obstacle(580, 350, 20, 150),
            ],
            collectibles=[
                Collectible(400, 400),
                Collectible(300, 250),
                Collectible(500, 250),
            ]
        ))

        # Level 2: More obstacles
        levels.append(Level(
            start_pos=(50, 300),
            exit_pos=(750, 300),
            obstacles=[
                Obstacle(150, 100, 20, 400),
                Obstacle(300, 100, 20, 200),
                Obstacle(300, 350, 20, 150),
                Obstacle(450, 200, 20, 400),
                Obstacle(600, 100, 20, 200),
                Obstacle(600, 350, 20, 150),
                Obstacle(200, 200, 80, 20),
                Obstacle(500, 350, 80, 20),
            ],
            collectibles=[
                Collectible(220, 280),
                Collectible(520, 430),
                Collectible(375, 100),
                Collectible(670, 280),
            ]
        ))

        # Level 3: Hazards
        levels.append(Level(
            start_pos=(100, 550),
            exit_pos=(700, 50),
            obstacles=[
                Obstacle(250, 150, 20, 300),
                Obstacle(400, 100, 20, 200),
                Obstacle(400, 350, 20, 150),
                Obstacle(550, 150, 20, 300),
                MovingObstacle(275, 300, 50, 20, 'vertical', 3, 150),
                MovingObstacle(525, 250, 50, 20, 'vertical', 3, 150),
            ],
            collectibles=[
                Collectible(320, 400),
                Collectible(480, 400),
                Collectible(400, 200),
            ]
        ))

        # Level 4: Complex
        levels.append(Level(
            start_pos=(50, 50),
            exit_pos=(750, 550),
            obstacles=[
                Obstacle(100, 100, 600, 20),
                Obstacle(100, 150, 20, 350),
                Obstacle(300, 200, 400, 20),
                Obstacle(300, 250, 20, 200),
                Obstacle(500, 300, 250, 20),
                Obstacle(500, 350, 20, 200),
                Obstacle(700, 400, 20, 150),
                MovingObstacle(150, 350, 30, 30, 'horizontal', 2, 80),
                MovingObstacle(350, 450, 30, 30, 'horizontal', 2, 80),
            ],
            collectibles=[
                Collectible(200, 350),
                Collectible(400, 450),
                Collectible(600, 350),
                Collectible(700, 250),
            ]
        ))

        return levels

    def _load_level(self, level_idx: int):
        """Load a level."""
        if level_idx >= len(self.levels):
            self.game_over = True
            self.level_complete = True
            return

        self.current_level = level_idx
        level = self.levels[level_idx]
        self.ball = Ball(level.start_pos[0], level.start_pos[1])
        self.level = level
        self.frames_elapsed = 0

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.score = 0
                        self.game_over = False
                        self.level_complete = False
                        self._load_level(0)

        # Continuous input for force application
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ball.apply_force(-IMPULSE_FORCE * 0.3, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ball.apply_force(IMPULSE_FORCE * 0.3, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.ball.apply_force(0, -IMPULSE_FORCE * 0.5)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.ball.apply_force(0, IMPULSE_FORCE * 0.3)

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        self.frames_elapsed += 1
        dt = self.clock.get_time()

        # Update ball
        self.ball.update()

        # Update exit
        self.level.exit.update(dt)

        # Update collectibles
        for collectible in self.level.collectibles:
            collectible.update(dt)
            if collectible.check_collision(self.ball):
                self.score += 10

        # Update obstacles and check collisions
        for obstacle in self.level.obstacles:
            if isinstance(obstacle, MovingObstacle):
                obstacle.update(dt)

            if obstacle.check_collision(self.ball):
                if obstacle.hazard:
                    self.score -= 50
                    self.ball.reset()

        # Check if reached exit
        if self.level.exit.check_reach(self.ball):
            # Score based on time (fewer frames = better)
            time_bonus = max(0, 100 - self.frames_elapsed // 10)
            self.score += 100 + time_bonus

            # Next level
            self._load_level(self.current_level + 1)

    def draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BG)

        # Draw obstacles
        for obstacle in self.level.obstacles:
            obstacle.draw(self.screen)

        # Draw collectibles
        for collectible in self.level.collectibles:
            collectible.draw(self.screen)

        # Draw exit
        self.level.exit.draw(self.screen)

        # Draw ball
        self.ball.draw(self.screen)

        # Draw UI
        self._draw_ui()

        pygame.display.flip()

    def _draw_ui(self):
        """Draw user interface."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.font.render(f"Level: {self.current_level + 1}", True, COLOR_TEXT)
        self.screen.blit(level_text, (10, 50))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            if self.level_complete:
                title = self.font.render("All Levels Complete!", True, COLOR_EXIT)
            else:
                title = self.font.render("Game Over", True, COLOR_EXIT)

            final_score = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart = self.small_font.render("Press SPACE to restart", True, COLOR_TEXT)

            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

            self.screen.blit(title, title_rect)
            self.screen.blit(final_score, score_rect)
            self.screen.blit(restart, restart_rect)

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
