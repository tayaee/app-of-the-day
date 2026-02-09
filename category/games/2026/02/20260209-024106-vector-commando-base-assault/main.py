"""Vector Commando: Base Assault - A top-down tactical shooter game."""

import pygame
import random
import math
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 10
SCROLL_SPEED = 1

# Colors
COLOR_BG = (34, 139, 34)  # Forest green
COLOR_PLAYER = (50, 50, 200)
COLOR_ENEMY_INFANTRY = (180, 50, 50)
COLOR_ENEMY_TURRET = (150, 100, 50)
COLOR_BULLET = (255, 255, 0)
COLOR_ENEMY_BULLET = (255, 100, 0)
COLOR_RIVER = (50, 150, 200)
COLOR_SANDBAG = (194, 178, 128)
COLOR_FLAG = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)


class Direction(Enum):
    """8-direction movement vectors."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)


class Entity:
    """Base class for all game entities."""

    def __init__(self, x: float, y: float, width: int, height: int, color: tuple):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.alive = True

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface):
        """Draw the entity."""
        if self.alive:
            pygame.draw.rect(surface, self.color, self.get_rect())

    def collides_with(self, other: 'Entity') -> bool:
        """Check collision with another entity."""
        return self.get_rect().colliderect(other.get_rect())


class Player(Entity):
    """Player character controlled by keyboard."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 20, 20, COLOR_PLAYER)
        self.lives = 3
        self.score = 0
        self.shoot_cooldown = 0
        self.grenade_cooldown = 0
        self.invincible_frames = 0
        self.facing = Direction.UP

    def update(self, keys, obstacles):
        """Update player state based on input."""
        if not self.alive:
            return

        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.grenade_cooldown > 0:
            self.grenade_cooldown -= 1
        if self.invincible_frames > 0:
            self.invincible_frames -= 1

        # Movement input
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Update facing direction
        if dy < 0:
            self.facing = Direction.UP
        elif dy > 0:
            self.facing = Direction.DOWN
        elif dx < 0:
            self.facing = Direction.LEFT
        elif dx > 0:
            self.facing = Direction.RIGHT

        # Calculate new position
        new_x = self.x + dx * PLAYER_SPEED
        new_y = self.y + dy * PLAYER_SPEED

        # Boundary checks
        new_x = max(0, min(SCREEN_WIDTH - self.width, new_x))
        new_y = max(0, min(SCREEN_HEIGHT - self.height, new_y))

        # Check collision with obstacles
        temp_rect = pygame.Rect(int(new_x), int(new_y), self.width, self.height)
        blocked = False
        for obstacle in obstacles:
            if obstacle.blocking and temp_rect.colliderect(obstacle.get_rect()):
                blocked = True
                break

        if not blocked:
            self.x = new_x
            self.y = new_y

    def can_shoot(self) -> bool:
        """Check if player can shoot."""
        return self.shoot_cooldown == 0

    def can_throw_grenade(self) -> bool:
        """Check if player can throw grenade."""
        return self.grenade_cooldown == 0

    def shoot(self) -> 'Bullet':
        """Fire a bullet in facing direction."""
        self.shoot_cooldown = 15
        dx, dy = self.facing.value
        return Bullet(
            self.x + self.width / 2 + dx * 15,
            self.y + self.height / 2 + dy * 15,
            dx * BULLET_SPEED,
            dy * BULLET_SPEED,
            COLOR_BULLET,
            is_player_bullet=True
        )

    def throw_grenade(self) -> 'Grenade':
        """Throw a grenade in facing direction."""
        self.grenade_cooldown = 60
        dx, dy = self.facing.value
        return Grenade(
            self.x + self.width / 2 + dx * 15,
            self.y + self.height / 2 + dy * 15,
            dx * BULLET_SPEED * 0.8,
            dy * BULLET_SPEED * 0.8
        )

    def take_damage(self):
        """Handle taking damage."""
        if self.invincible_frames == 0:
            self.lives -= 1
            self.invincible_frames = 120
            if self.lives <= 0:
                self.alive = False

    def draw(self, surface: pygame.Surface):
        """Draw player with invincibility flashing."""
        if not self.alive:
            return
        if self.invincible_frames > 0 and (self.invincible_frames // 4) % 2 == 0:
            return
        super().draw(surface)
        # Draw direction indicator
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        dx, dy = self.facing.value
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (center_x, center_y),
            (center_x + dx * 12, center_y + dy * 12),
            2
        )


class Bullet(Entity):
    """Projectile that travels in a straight line."""

    def __init__(self, x: float, y: float, dx: float, dy: float, color: tuple, is_player_bullet: bool = True):
        super().__init__(x - 3, y - 3, 6, 6, color)
        self.dx = dx
        self.dy = dy
        self.is_player_bullet = is_player_bullet

    def update(self):
        """Update bullet position."""
        self.x += self.dx
        self.y += self.dy

        # Remove if off screen
        if (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
                self.y < -50 or self.y > SCREEN_HEIGHT + 50):
            self.alive = False

    def draw(self, surface: pygame.Surface):
        """Draw bullet as circle."""
        if self.alive:
            pygame.draw.circle(surface, self.color, (int(self.x + 3), int(self.y + 3)), 3)


class Grenade(Entity):
    """Thrown explosive that travels over obstacles."""

    def __init__(self, x: float, y: float, dx: float, dy: float):
        super().__init__(x - 5, y - 5, 10, 10, (100, 100, 100))
        self.dx = dx
        self.dy = dy
        self.timer = 60  # Frames until explosion
        self.exploded = False

    def update(self):
        """Update grenade position and timer."""
        if not self.exploded:
            self.x += self.dx
            self.y += self.dy
            self.dx *= 0.98  # Friction
            self.dy *= 0.98
            self.timer -= 1

            if self.timer <= 0:
                self.exploded = True
                self.alive = False

    def get_explosion_rect(self) -> pygame.Rect:
        """Get the explosion area."""
        return pygame.Rect(int(self.x - 40), int(self.y - 40), 80, 80)

    def draw(self, surface: pygame.Surface):
        """Draw grenade."""
        if not self.exploded:
            pygame.draw.circle(surface, self.color, (int(self.x + 5), int(self.y + 5)), 5)
            # Draw timer indicator
            pulse = int((self.timer / 60) * 255)
            pygame.draw.circle(
                surface,
                (255, pulse, 0),
                (int(self.x + 5), int(self.y + 5)),
                5 + (60 - self.timer) // 10,
                1
            )


class Enemy(Entity):
    """Base enemy class."""

    def __init__(self, x: float, y: float, width: int, height: int, color: tuple):
        super().__init__(x, y, width, height, color)
        self.shoot_timer = random.randint(60, 180)

    def update(self, player: Player):
        """Update enemy behavior."""
        self.shoot_timer -= 1

    def can_shoot(self) -> bool:
        """Check if enemy can shoot."""
        return self.shoot_timer <= 0

    def shoot_at(self, player: Player) -> Bullet:
        """Fire at player."""
        self.shoot_timer = random.randint(90, 200)
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2

        dx = player_center_x - center_x
        dy = player_center_y - center_y
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        return Bullet(
            center_x + dx * 15,
            center_y + dy * 15,
            dx * BULLET_SPEED * 0.6,
            dy * BULLET_SPEED * 0.6,
            COLOR_ENEMY_BULLET,
            is_player_bullet=False
        )


class Infantry(Enemy):
    """Mobile enemy that moves toward player."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 18, 18, COLOR_ENEMY_INFANTRY)
        self.speed = 1.5

    def update(self, player: Player):
        """Move toward player."""
        super().update(player)

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2

        dx = player_center_x - center_x
        dy = player_center_y - center_y
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            self.x += (dx / length) * self.speed
            self.y += (dy / length) * self.speed


class Turret(Enemy):
    """Stationary enemy that shoots at player."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 24, COLOR_ENEMY_TURRET)
        self.shoot_timer = random.randint(30, 90)


class Obstacle(Entity):
    """Static obstacle on the battlefield."""

    def __init__(self, x: float, y: float, width: int, height: int, color: tuple, blocking: bool):
        super().__init__(x, y, width, height, color)
        self.blocking = blocking


class Flag(Entity):
    """Capture objective at end of level."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 30, 40, COLOR_FLAG)
        self.captured = False
        self.wave_offset = 0

    def update(self):
        """Animate flag."""
        self.wave_offset = (self.wave_offset + 0.1) % (math.pi * 2)

    def draw(self, surface: pygame.Surface):
        """Draw flag with waving animation."""
        if self.captured:
            return

        # Pole
        pygame.draw.line(
            surface,
            (100, 100, 100),
            (self.x + 5, self.y),
            (self.x + 5, self.y + self.height),
            3
        )

        # Flag
        wave = int(math.sin(self.wave_offset) * 3)
        points = [
            (self.x + 5, self.y + wave),
            (self.x + 30, self.y + 5 + wave),
            (self.x + 30, self.y + 20 + wave),
            (self.x + 5, self.y + 15 + wave)
        ]
        pygame.draw.polygon(surface, self.color, points)


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Commando: Base Assault")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset all game state."""
        self.player = Player(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 100)
        self.bullets = []
        self.grenades = []
        self.enemies = []
        self.obstacles = []
        self.flags = []
        self.scroll_offset = 0
        self.level_length = 3000
        self.game_over = False
        self.victory = False
        self.wave = 1

        self.generate_level()

    def generate_level(self):
        """Procedurally generate the level."""
        # Generate obstacles
        for y in range(200, self.level_length, 150):
            # Random rivers
            if random.random() < 0.3:
                river_width = random.randint(100, 200)
                river_x = random.randint(50, SCREEN_WIDTH - 50 - river_width)
                self.obstacles.append(
                    Obstacle(river_x, y, river_width, 40, COLOR_RIVER, blocking=True)
                )

            # Random sandbag walls
            if random.random() < 0.4:
                for i in range(random.randint(2, 4)):
                    bag_x = random.randint(50, SCREEN_WIDTH - 100)
                    bag_y = y + random.randint(-30, 30)
                    self.obstacles.append(
                        Obstacle(bag_x, bag_y, 60, 15, COLOR_SANDBAG, blocking=False)
                    )

        # Generate enemy waves
        for y in range(300, self.level_length - 200, 200):
            # Infantry group
            for _ in range(random.randint(2, 4)):
                ex = random.randint(50, SCREEN_WIDTH - 70)
                self.enemies.append(Infantry(ex, y))

            # Turrets
            if random.random() < 0.5:
                tx = random.choice([100, SCREEN_WIDTH - 150])
                self.enemies.append(Turret(tx, y + 50))

        # Place flag at end
        self.flags.append(Flag(SCREEN_WIDTH // 2 - 15, self.level_length - 100))

    def spawn_enemies(self):
        """Spawn new enemies as player progresses."""
        if len(self.enemies) < 5 + self.wave:
            spawn_y = self.scroll_offset + SCREEN_HEIGHT + random.randint(0, 100)
            if spawn_y < self.level_length - 200:
                enemy_type = random.choice([Infantry, Turret])
                ex = random.randint(50, SCREEN_WIDTH - 70)
                self.enemies.append(enemy_type(ex, spawn_y))

    def handle_input(self):
        """Process keyboard input."""
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over or self.victory:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_z and self.player.can_shoot():
                        self.bullets.append(self.player.shoot())
                    elif event.key == pygame.K_x and self.player.can_throw_grenade():
                        self.grenades.append(self.player.throw_grenade())

        if not self.game_over and not self.victory:
            self.player.update(keys, self.get_visible_obstacles())

        return True

    def get_visible_obstacles(self):
        """Get obstacles currently on screen."""
        visible = []
        for obs in self.obstacles:
            screen_y = obs.y - self.scroll_offset
            if -100 < screen_y < SCREEN_HEIGHT + 100:
                visible.append(obs)
        return visible

    def update(self):
        """Update all game objects."""
        if self.game_over or self.victory:
            return

        # Scroll battlefield
        if self.player.y < SCREEN_HEIGHT // 2:
            scroll_amount = (SCREEN_HEIGHT // 2 - self.player.y) * SCROLL_SPEED
            self.scroll_offset += scroll_amount
            self.player.y = SCREEN_HEIGHT // 2

        # Spawn enemies
        self.spawn_enemies()

        # Update bullets
        for bullet in self.bullets:
            bullet.update()

        # Update grenades
        for grenade in self.grenades:
            grenade.update()

        # Update enemies (only those on screen)
        visible_enemies = []
        for enemy in self.enemies:
            screen_y = enemy.y - self.scroll_offset
            if -100 < screen_y < SCREEN_HEIGHT + 100:
                enemy.update(self.player)
                visible_enemies.append(enemy)
            elif screen_y >= SCREEN_HEIGHT + 100:
                visible_enemies.append(enemy)  # Keep off-screen but ahead

        # Enemy shooting
        for enemy in visible_enemies:
            screen_y = enemy.y - self.scroll_offset
            if 0 < screen_y < SCREEN_HEIGHT and enemy.can_shoot():
                self.bullets.append(enemy.shoot_at(self.player))

        # Update flags
        for flag in self.flags:
            flag.update()

        # Check collisions
        self.check_collisions()

        # Remove dead entities
        self.bullets = [b for b in self.bullets if b.alive]
        self.grenades = [g for g in self.grenades if g.alive]
        self.enemies = [e for e in self.enemies if e.alive]

        # Check game state
        if not self.player.alive:
            self.game_over = True

        # Check victory
        for flag in self.flags:
            if not flag.captured:
                screen_y = flag.y - self.scroll_offset
                if screen_y < SCREEN_HEIGHT and self.player.collides_with(flag):
                    flag.captured = True
                    self.player.score += 500

        if all(flag.captured for flag in self.flags):
            self.victory = True

    def check_collisions(self):
        """Handle all collision detection."""
        # Player bullets vs enemies
        for bullet in self.bullets:
            if not bullet.is_player_bullet:
                continue

            for enemy in self.enemies:
                if enemy.alive and bullet.collides_with(enemy):
                    enemy.alive = False
                    bullet.alive = False
                    self.player.score += 100
                    break

        # Enemy bullets vs player
        for bullet in self.bullets:
            if bullet.is_player_bullet:
                continue

            screen_y = bullet.y - self.scroll_offset
            if 0 < screen_y < SCREEN_HEIGHT and bullet.collides_with(self.player):
                bullet.alive = False
                self.player.take_damage()

        # Grenades vs enemies
        for grenade in self.grenades:
            if grenade.exploded:
                explosion_rect = grenade.get_explosion_rect()
                for enemy in self.enemies:
                    enemy_screen_rect = enemy.get_rect()
                    enemy_screen_rect.y -= self.scroll_offset
                    if explosion_rect.colliderect(enemy_screen_rect):
                        enemy.alive = False
                        self.player.score += 100

        # Player vs enemies (contact damage)
        for enemy in self.enemies:
            screen_y = enemy.y - self.scroll_offset
            if 0 < screen_y < SCREEN_HEIGHT and enemy.collides_with(self.player):
                self.player.take_damage()

    def draw(self):
        """Render all game objects."""
        self.screen.fill(COLOR_BG)

        # Draw obstacles
        for obs in self.obstacles:
            screen_y = obs.y - self.scroll_offset
            if -100 < screen_y < SCREEN_HEIGHT + 100:
                draw_rect = obs.get_rect()
                draw_rect.y = screen_y
                pygame.draw.rect(self.screen, obs.color, draw_rect)

        # Draw flags
        for flag in self.flags:
            screen_y = flag.y - self.scroll_offset
            if -100 < screen_y < SCREEN_HEIGHT + 100:
                draw_y = screen_y
                pygame.draw.line(
                    self.screen,
                    (100, 100, 100),
                    (flag.x + 5, draw_y),
                    (flag.x + 5, draw_y + flag.height),
                    3
                )
                if not flag.captured:
                    wave = int(math.sin(flag.wave_offset) * 3)
                    points = [
                        (flag.x + 5, draw_y + wave),
                        (flag.x + 30, draw_y + 5 + wave),
                        (flag.x + 30, draw_y + 20 + wave),
                        (flag.x + 5, draw_y + 15 + wave)
                    ]
                    pygame.draw.polygon(self.screen, flag.color, points)

        # Draw enemies
        for enemy in self.enemies:
            screen_y = enemy.y - self.scroll_offset
            if -50 < screen_y < SCREEN_HEIGHT + 50:
                draw_rect = enemy.get_rect()
                draw_rect.y = screen_y
                pygame.draw.rect(self.screen, enemy.color, draw_rect)

        # Draw player
        self.player.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            screen_y = bullet.y - self.scroll_offset
            if -50 < screen_y < SCREEN_HEIGHT + 50:
                pygame.draw.circle(
                    self.screen,
                    bullet.color,
                    (int(bullet.x), int(screen_y)),
                    3
                )

        # Draw grenades
        for grenade in self.grenades:
            screen_y = grenade.y - self.scroll_offset
            if grenade.exploded:
                # Draw explosion
                explosion_rect = pygame.Rect(
                    int(grenade.x - 40),
                    int(screen_y - 40),
                    80, 80
                )
                pygame.draw.circle(self.screen, (255, 150, 0), explosion_rect.center, 40)
            elif -50 < screen_y < SCREEN_HEIGHT + 50:
                pygame.draw.circle(
                    self.screen,
                    grenade.color,
                    (int(grenade.x + 5), int(screen_y + 5)),
                    5
                )

        # Draw HUD
        self.draw_hud()

        # Draw game over / victory screen
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display."""
        # Score
        score_text = self.font.render(f"SCORE: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.font.render(f"LIVES: {self.player.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (10, 50))

        # Progress
        progress = min(100, int(self.scroll_offset / self.level_length * 100))
        progress_text = self.small_font.render(f"PROGRESS: {progress}%", True, COLOR_TEXT)
        self.screen.blit(progress_text, (10, 90))

        # Controls
        controls = "ARROWS: Move | Z: Shoot | X: Grenade"
        controls_text = self.small_font.render(controls, True, (200, 200, 200))
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 10, 10))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        score_text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        restart_text = self.small_font.render("Press R to restart or Q to quit", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def draw_victory(self):
        """Draw victory screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        victory_text = self.font.render("VICTORY!", True, (50, 255, 50))
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, text_rect)

        score_text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        restart_text = self.small_font.render("Press R to play again or Q to quit", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
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
