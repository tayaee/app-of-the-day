"""
Vector Balloon Fight - Gravity
A 2D side-scroller where you flap to gain altitude and pop enemy balloons.
"""

import pygame
import random
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (30, 30, 50)
COLOR_PLAYER = (50, 200, 255)
COLOR_BALLOON = (255, 100, 100)
COLOR_ENEMY = (255, 150, 50)
COLOR_PLATFORM = (100, 150, 200)
COLOR_TEXT = (255, 255, 255)

# Physics
GRAVITY = 0.3
FLAP_FORCE = -6.0
MAX_FALL_SPEED = 10.0
BALLOON_LIFT = 0.15

# Game settings
PLAYER_LIVES = 3
ENEMIES_PER_WAVE = 5
WAVE_BONUS = 500
ENEMY_SCORE = 100


class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2(0, 0)


class Entity:
    def __init__(self, x, y, width, height):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.width = width
        self.height = height
        self.active = True

    def get_rect(self):
        return pygame.Rect(
            int(self.pos.x - self.width // 2),
            int(self.pos.y - self.height // 2),
            self.width,
            self.height
        )

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class Platform(Entity):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_PLATFORM, rect, border_radius=4)
        pygame.draw.rect(surface, (150, 200, 255), rect, 2, border_radius=4)


class Balloon:
    def __init__(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.radius = 12
        self.popped = False

    def draw(self, surface, owner_x, owner_y):
        if not self.popped:
            x = int(owner_x + self.offset_x)
            y = int(owner_y + self.offset_y)
            pygame.draw.circle(surface, COLOR_BALLOON, (x, y), self.radius)
            pygame.draw.circle(surface, (255, 150, 150), (x - 3, y - 3), 4)


class Character(Entity):
    def __init__(self, x, y, width=30, height=30):
        super().__init__(x, y, width, height)
        self.balloons = [
            Balloon(-10, -20),
            Balloon(10, -20)
        ]
        self.on_ground = False

    def update(self, dt, platforms):
        # Apply gravity
        self.vel.y += GRAVITY * dt

        # Apply balloon lift
        active_balloons = sum(1 for b in self.balloons if not b.popped)
        if active_balloons > 0:
            self.vel.y -= BALLOON_LIFT * active_balloons * dt

        # Clamp fall speed
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED

        # Update position
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt

        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.collides_with_platform(platform):
                self.resolve_platform_collision(platform)

    def collides_with_platform(self, platform):
        rect = self.get_rect()
        plat_rect = platform.get_rect()
        return rect.colliderect(plat_rect)

    def resolve_platform_collision(self, platform):
        rect = self.get_rect()
        plat_rect = platform.get_rect()

        # Determine collision side
        overlap_left = (rect.right - plat_rect.left)
        overlap_right = (plat_rect.right - rect.left)
        overlap_top = (rect.bottom - plat_rect.top)
        overlap_bottom = (plat_rect.bottom - rect.top)

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_top and self.vel.y > 0:
            self.pos.y = plat_rect.top - self.height // 2
            self.vel.y = 0
            self.on_ground = True
        elif min_overlap == overlap_bottom and self.vel.y < 0:
            self.pos.y = plat_rect.bottom + self.height // 2
            self.vel.y = 0
        elif min_overlap == overlap_left and self.vel.x > 0:
            self.pos.x = plat_rect.left - self.width // 2
            self.vel.x = -self.vel.x * 0.5
        elif min_overlap == overlap_right and self.vel.x < 0:
            self.pos.x = plat_rect.right + self.width // 2
            self.vel.x = -self.vel.x * 0.5

    def flap(self):
        if any(not b.popped for b in self.balloons):
            self.vel.y = FLAP_FORCE

    def pop_balloon(self):
        for balloon in self.balloons:
            if not balloon.popped:
                balloon.popped = True
                return True
        return False

    def has_balloons(self):
        return any(not b.popped for b in self.balloons)

    def draw(self, surface):
        # Draw balloons first
        for balloon in self.balloons:
            balloon.draw(surface, self.pos.x, self.pos.y)

        # Draw character body
        rect = self.get_rect()
        if self.has_balloons():
            color = COLOR_PLAYER
        else:
            color = (150, 150, 150)

        pygame.draw.ellipse(surface, color, rect)

        # Draw eyes
        eye_offset_x = 4 if self.vel.x >= 0 else -4
        pygame.draw.circle(surface, (255, 255, 255), (int(rect.centerx + eye_offset_x - 4), int(rect.centery - 4)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(rect.centerx + eye_offset_x + 4), int(rect.centery - 4)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(rect.centerx + eye_offset_x - 4), int(rect.centery - 4)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(rect.centerx + eye_offset_x + 4), int(rect.centery - 4)), 2)


class Enemy(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.target_x = x
        self.target_y = y
        self.change_target_timer = 0
        self.speed = 2.0

    def update(self, dt, platforms):
        super().update(dt, platforms)

        # AI behavior - move toward target
        to_target = Vector2(self.target_x - self.pos.x, self.target_y - self.pos.y)
        dist = to_target.magnitude()

        if dist < 50 or self.change_target_timer <= 0:
            self.change_target_timer = random.randint(60, 180)
            self.target_x = random.randint(50, SCREEN_WIDTH - 50)
            self.target_y = random.randint(50, SCREEN_HEIGHT // 2)

        if dist > 0:
            direction = to_target.normalize()
            self.vel.x = direction.x * self.speed

        # Occasional flap
        if random.random() < 0.02 and self.pos.y > 100:
            self.flap()

        # Screen wrap horizontal
        if self.pos.x < -20:
            self.pos.x = SCREEN_WIDTH + 20
        elif self.pos.x > SCREEN_WIDTH + 20:
            self.pos.x = -20

        self.change_target_timer -= dt

    def draw(self, surface):
        # Draw balloons
        for balloon in self.balloons:
            balloon.draw(surface, self.pos.x, self.pos.y)

        # Draw enemy body
        rect = self.get_rect()
        color = COLOR_ENEMY if self.has_balloons() else (150, 100, 50)

        pygame.draw.ellipse(surface, color, rect)

        # Draw angry eyes
        pygame.draw.circle(surface, (255, 255, 255), (int(rect.centerx - 6), int(rect.centery - 4)), 5)
        pygame.draw.circle(surface, (255, 255, 255), (int(rect.centerx + 6), int(rect.centery - 4)), 5)
        pygame.draw.circle(surface, (0, 0, 0), (int(rect.centerx - 6), int(rect.centery - 4)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(rect.centerx + 6), int(rect.centery - 4)), 2)


class Player(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 4.0

    def update(self, dt, platforms):
        super().update(dt, platforms)

        # Horizontal movement
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        if keys[pygame.K_LEFT]:
            self.vel.x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel.x = self.speed

        # Screen bounds
        self.pos.x = max(20, min(SCREEN_WIDTH - 20, self.pos.x))

    def draw(self, surface):
        super().draw(surface)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Balloon Fight - Gravity")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.platforms = self.create_platforms()
        self.score = 0
        self.lives = PLAYER_LIVES
        self.wave = 1
        self.spawn_wave()
        self.game_over = False
        self.falling_penalty = 0

    def create_platforms(self):
        platforms = [
            Platform(150, 450, 200, 20),
            Platform(450, 350, 200, 20),
            Platform(100, 250, 150, 20),
            Platform(550, 200, 150, 20),
            Platform(300, 150, 200, 20),
        ]
        return platforms

    def spawn_wave(self):
        self.enemies = []
        for _ in range(ENEMIES_PER_WAVE + self.wave - 1):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, 200)
            self.enemies.append(Enemy(x, y))

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies[:]:
            if not enemy.active:
                continue

            enemy_rect = enemy.get_rect()

            # Check collision
            if player_rect.colliderect(enemy_rect):
                # Player landing on enemy from above
                if self.player.vel.y > 0 and self.player.pos.y < enemy.pos.y:
                    if enemy.pop_balloon():
                        self.score += ENEMY_SCORE
                        if not enemy.has_balloons():
                            enemy.active = False
                            self.score += ENEMY_SCORE
                # Enemy touching player
                else:
                    if self.player.pop_balloon():
                        if not self.player.has_balloons():
                            self.lives -= 1
                            self.player.pos = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                            self.player.vel = Vector2(0, 0)
                            for b in self.player.balloons:
                                b.popped = False

                            if self.lives <= 0:
                                self.game_over = True

    def update(self):
        if self.game_over:
            return

        dt = 1.0

        # Update player
        self.player.update(dt, self.platforms)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.platforms)

        # Check collisions
        self.check_collisions()

        # Remove inactive enemies
        self.enemies = [e for e in self.enemies if e.active]

        # Check for wave completion
        if len(self.enemies) == 0:
            self.score += WAVE_BONUS
            self.wave += 1
            self.spawn_wave()

        # Penalty for falling below screen
        if self.player.pos.y > SCREEN_HEIGHT + 50:
            self.falling_penalty += 1
            if self.falling_penalty % 10 == 0:
                self.score -= 10
                if not self.player.has_balloons():
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    self.player.pos = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    self.player.vel = Vector2(0, 0)
                    for b in self.player.balloons:
                        b.popped = False
        else:
            self.falling_penalty = 0

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        wave_text = self.font.render(f"Wave: {self.wave}", True, COLOR_TEXT)
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_TEXT)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(wave_text, (10, 50))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 100, 100))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart_text = self.font.render("Press SPACE to restart", True, COLOR_TEXT)

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if self.game_over:
                            self.reset_game()
                        else:
                            self.player.flap()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
