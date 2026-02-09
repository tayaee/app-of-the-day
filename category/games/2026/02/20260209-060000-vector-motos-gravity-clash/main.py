import pygame
import math
import random
from typing import List, Tuple, Optional

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics Constants
FRICTION = 0.98
PLAYER_ACCEL = 0.8
PLAYER_MAX_SPEED = 8.0
BOUNCE_DAMPING = 0.7

# Colors
COLOR_BG = (20, 20, 30)
COLOR_ARENA = (40, 40, 50)
COLOR_ARENA_BORDER = (60, 60, 80)
COLOR_PLAYER = (0, 200, 255)
COLOR_ENEMY_NORMAL = (255, 100, 100)
COLOR_ENEMY_HEAVY = (255, 150, 50)
COLOR_ENEMY_FAST = (255, 100, 255)
COLOR_TEXT = (220, 220, 220)
COLOR_PARTICLE = (255, 255, 150)


class Vector:
    """Simple 2D vector class for physics calculations."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0)
        return self / mag

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Particle:
    """Visual particle effect."""

    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*COLOR_PARTICLE, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class Unit:
    """Base class for all game units."""

    def __init__(self, x: float, y: float, radius: float, mass: float, color: Tuple[int, int, int]):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.radius = radius
        self.mass = mass
        self.color = color
        self.is_off_screen = False
        self.trail = []
        self.trail_timer = 0

    def update(self):
        self.pos = self.pos + self.vel
        self.vel = self.vel * FRICTION

        # Update trail
        self.trail_timer += 1
        if self.trail_timer >= 5:
            self.trail_timer = 0
            self.trail.append((self.pos.x, self.pos.y))
            if len(self.trail) > 10:
                self.trail.pop(0)

        # Check if off screen
        margin = 50
        self.is_off_screen = (
            self.pos.x < -margin or
            self.pos.x > SCREEN_WIDTH + margin or
            self.pos.y < -margin or
            self.pos.y > SCREEN_HEIGHT + margin
        )

    def apply_force(self, fx: float, fy: float):
        self.vel.x += fx / self.mass
        self.vel.y += fy / self.mass

    def draw(self, surface):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            radius = int(self.radius * 0.5 * (i / len(self.trail)))
            if radius > 0:
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
                surface.blit(s, (int(tx) - radius, int(ty) - radius))

        # Draw unit body
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))

        # Draw highlight
        highlight_offset = int(self.radius * 0.3)
        highlight_radius = int(self.radius * 0.3)
        if highlight_radius > 0:
            pygame.draw.circle(
                surface,
                (min(self.color[0] + 60, 255), min(self.color[1] + 60, 255), min(self.color[2] + 60, 255)),
                (int(self.pos.x) - highlight_offset, int(self.pos.y) - highlight_offset),
                highlight_radius
            )


class Player(Unit):
    """Player controlled unit."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, radius=20, mass=2.0, color=COLOR_PLAYER)
        self.input_dir = Vector(0, 0)

    def handle_input(self, keys):
        self.input_dir = Vector(0, 0)
        if keys[pygame.K_LEFT]:
            self.input_dir.x = -1
        if keys[pygame.K_RIGHT]:
            self.input_dir.x = 1
        if keys[pygame.K_UP]:
            self.input_dir.y = -1
        if keys[pygame.K_DOWN]:
            self.input_dir.y = 1

        if self.input_dir.magnitude() > 0:
            self.input_dir = self.input_dir.normalize()

    def update(self):
        # Apply input force
        if self.input_dir.magnitude() > 0:
            force = self.input_dir * PLAYER_ACCEL * self.mass
            self.apply_force(force.x, force.y)

        # Clamp speed
        speed = self.vel.magnitude()
        if speed > PLAYER_MAX_SPEED:
            self.vel = self.vel.normalize() * PLAYER_MAX_SPEED

        super().update()


class Enemy(Unit):
    """Enemy unit with AI behavior."""

    def __init__(self, x: float, y: float, enemy_type: str):
        self.enemy_type = enemy_type

        if enemy_type == "normal":
            mass = 1.5
            radius = 18
            color = COLOR_ENEMY_NORMAL
            self.speed = 0.3
        elif enemy_type == "heavy":
            mass = 4.0
            radius = 25
            color = COLOR_ENEMY_HEAVY
            self.speed = 0.15
        else:  # fast
            mass = 1.0
            radius = 15
            color = COLOR_ENEMY_FAST
            self.speed = 0.5

        super().__init__(x, y, radius, mass, color)
        self.ai_timer = random.randint(0, 60)
        self.ai_dir = Vector(0, 0)

    def update_ai(self, player_pos: Vector):
        self.ai_timer += 1

        if self.ai_timer >= 60:
            self.ai_timer = 0
            # Decide new direction - occasionally move towards player
            if random.random() < 0.4:
                direction = (player_pos - self.pos).normalize()
                self.ai_dir = direction * random.uniform(0.5, 1.0)
            else:
                angle = random.uniform(0, math.pi * 2)
                self.ai_dir = Vector(math.cos(angle), math.sin(angle))

        # Apply AI movement
        self.apply_force(self.ai_dir.x * self.speed * self.mass, self.ai_dir.y * self.speed * self.mass)

        super().update()


class Arena:
    """Game arena with configurable bounds."""

    def __init__(self, level: int):
        self.level = level
        # Shrink arena slightly as levels progress
        shrink_amount = min(level * 20, 100)
        self.margin = 50 + shrink_amount
        self.bounds = pygame.Rect(
            self.margin,
            self.margin,
            SCREEN_WIDTH - self.margin * 2,
            SCREEN_HEIGHT - self.margin * 2
        )
        self.pulse_phase = 0

    def update(self):
        self.pulse_phase += 0.05

    def draw(self, surface, has_particles: bool = False):
        # Draw arena background
        bg_color = list(COLOR_ARENA)
        if has_particles:
            pulse = int(10 * math.sin(self.pulse_phase))
            bg_color = (bg_color[0] + pulse, bg_color[1], bg_color[2])

        pygame.draw.rect(surface, bg_color, self.bounds)

        # Draw border with glow effect
        border_rect = self.bounds.inflate(4, 4)
        pygame.draw.rect(surface, COLOR_ARENA_BORDER, border_rect, 2)

        # Draw corner markers
        corner_size = 20
        corners = [
            (self.bounds.left, self.bounds.top),
            (self.bounds.right, self.bounds.top),
            (self.bounds.left, self.bounds.bottom),
            (self.bounds.right, self.bounds.bottom),
        ]
        for x, y in corners:
            pygame.draw.line(surface, COLOR_ARENA_BORDER,
                           (x - corner_size, y), (x + corner_size, y), 3)
            pygame.draw.line(surface, COLOR_ARENA_BORDER,
                           (x, y - corner_size), (x, y + corner_size), 3)

    def is_out_of_bounds(self, unit: Unit) -> bool:
        return (
            unit.pos.x < self.bounds.left - unit.radius or
            unit.pos.x > self.bounds.right + unit.radius or
            unit.pos.y < self.bounds.top - unit.radius or
            unit.pos.y > self.bounds.bottom + unit.radius
        )


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Motos: Gravity Clash")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.state = "title"  # title, playing, game_over, victory
        self.score = 0
        self.level = 1
        self.lives = 3
        self.time_bonus = 1000
        self.particles: List[Particle] = []
        self.setup_level()

    def setup_level(self):
        self.arena = Arena(self.level)

        # Center player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Spawn enemies based on level
        self.enemies: List[Enemy] = []
        enemy_count = 2 + self.level

        for _ in range(enemy_count):
            # Determine enemy type
            if self.level >= 3 and random.random() < 0.2:
                enemy_type = "heavy"
            elif self.level >= 2 and random.random() < 0.3:
                enemy_type = "fast"
            else:
                enemy_type = "normal"

            # Spawn at random edge position
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x = random.uniform(self.arena.bounds.left + 30, self.arena.bounds.right - 30)
                y = self.arena.bounds.top + 30
            elif side == 'bottom':
                x = random.uniform(self.arena.bounds.left + 30, self.arena.bounds.right - 30)
                y = self.arena.bounds.bottom - 30
            elif side == 'left':
                x = self.arena.bounds.left + 30
                y = random.uniform(self.arena.bounds.top + 30, self.arena.bounds.bottom - 30)
            else:
                x = self.arena.bounds.right - 30
                y = random.uniform(self.arena.bounds.top + 30, self.arena.bounds.bottom - 30)

            self.enemies.append(Enemy(x, y, enemy_type))

        self.time_bonus = 1000 + self.level * 200
        self.start_ticks = pygame.time.get_ticks()

    def handle_collisions(self):
        all_units = [self.player] + self.enemies

        for i, a in enumerate(all_units):
            for b in all_units[i + 1:]:
                dist = a.pos.distance_to(b.pos)
                min_dist = a.radius + b.radius

                if dist < min_dist and dist > 0:
                    # Collision detected - elastic collision response
                    normal = (b.pos - a.pos).normalize()

                    # Relative velocity
                    rel_vel = a.vel - b.vel
                    vel_along_normal = rel_vel.dot(normal)

                    # Don't resolve if velocities are separating
                    if vel_along_normal > 0:
                        continue

                    # Impulse scalar
                    j = -(1 + BOUNCE_DAMPING) * vel_along_normal
                    j /= (1 / a.mass + 1 / b.mass)

                    # Apply impulse
                    impulse = normal * j
                    a.vel = a.vel - impulse * (1 / a.mass)
                    b.vel = b.vel + impulse * (1 / b.mass)

                    # Separate overlapping units
                    overlap = min_dist - dist
                    correction = normal * (overlap / 2)
                    a.pos = a.pos - correction
                    b.pos = b.pos + correction

                    # Create collision particles
                    collision_point = a.pos + (b.pos - a.pos) * 0.5
                    self.create_particles(collision_point.x, collision_point.y, 5)

    def create_particles(self, x: float, y: float, count: int):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, vx, vy, lifetime))

    def update(self):
        if self.state != "playing":
            return

        # Update arena
        self.arena.update()

        # Handle input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()

        # Update enemies
        for enemy in self.enemies:
            enemy.update_ai(self.player.pos)

        # Handle collisions
        self.handle_collisions()

        # Check if player fell off
        if self.arena.is_out_of_bounds(self.player):
            self.lives -= 1
            if self.lives <= 0:
                self.state = "game_over"
            else:
                # Reset player position
                self.player.pos = Vector(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.player.vel = Vector(0, 0)
                self.player.trail.clear()
                self.create_particles(self.player.pos.x, self.player.pos.y, 20)

        # Check enemies
        enemies_to_remove = []
        for enemy in self.enemies:
            enemy.update()
            if self.arena.is_out_of_bounds(enemy):
                enemies_to_remove.append(enemy)
                self.score += 100
                self.create_particles(enemy.pos.x, enemy.pos.y, 15)

        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

        # Update particles
        self.particles = [p for p in self.particles if p.update()]

        # Update time bonus
        self.time_bonus -= 1
        if self.time_bonus <= 0:
            self.time_bonus = 0

        # Check victory
        if len(self.enemies) == 0:
            self.score += self.time_bonus
            self.level += 1
            self.setup_level()

    def draw(self):
        self.screen.fill(COLOR_BG)

        if self.state == "title":
            self.draw_title()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "victory":
            self.draw_victory()

        pygame.display.flip()

    def draw_title(self):
        # Title
        title = self.font_large.render("MOTOS GRAVITY CLASH", True, COLOR_PLAYER)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_small.render("Push enemies off the edge!", True, COLOR_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # Instructions
        instructions = [
            "ARROW KEYS - Move",
            "Push all enemies off the arena",
            "Don't fall off yourself!",
            "",
            "Press SPACE to Start",
            "Press ESC to Quit"
        ]

        y = 280
        for line in instructions:
            text = self.font_small.render(line, True, COLOR_TEXT)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 35

    def draw_game(self):
        # Draw arena
        self.arena.draw(self.screen, len(self.particles) > 0)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

    def draw_hud(self):
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        # Level
        level_text = self.font_medium.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (20, 55))

        # Lives
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (20, 90))

        # Enemies remaining
        enemies_text = self.font_medium.render(f"Enemies: {len(self.enemies)}", True, COLOR_TEXT)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 150, 20))

        # Time bonus
        time_text = self.font_small.render(f"Bonus: {self.time_bonus}", True, COLOR_TEXT)
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 55))

    def draw_game_over(self):
        # Draw game in background dimmed
        self.arena.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over = self.font_large.render("GAME OVER", True, (255, 100, 100))
        rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(game_over, rect)

        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(score_text, score_rect)

        # Level reached
        level_text = self.font_medium.render(f"Level Reached: {self.level}", True, COLOR_TEXT)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(level_text, level_rect)

        # Instructions
        restart = self.font_small.render("Press R to Restart or ESC to Quit", True, COLOR_TEXT)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(restart, restart_rect)

    def draw_victory(self):
        self.screen.fill(COLOR_BG)

        victory = self.font_large.render("VICTORY!", True, (100, 255, 100))
        rect = victory.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(victory, rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if self.state == "title":
                        if event.key == pygame.K_SPACE:
                            self.state = "playing"

                    elif self.state == "game_over":
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.state = "playing"

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
