"""Vector Joust: Gravity Combat

A simplified gravity-defying aerial duel where height and timing determine the victor.
"""

import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Physics
GRAVITY = 0.4
FLAP_STRENGTH = -8
MOVE_SPEED = 5
MAX_FALL_SPEED = 12
MAX_HORIZONTAL_SPEED = 8
FRICTION = 0.92

# Colors
COLOR_BG = (20, 20, 40)
COLOR_PLAYER = (50, 200, 255)
COLOR_ENEMY = (255, 80, 80)
COLOR_PLATFORM = (100, 100, 120)
COLOR_TEXT = (255, 255, 255)

# Game
PLAYER_LIVES = 3
ENEMY_LIVES = 3
COLLISION_COOLDOWN = 60


class VectorEntity:
    """Base class for all moving entities in the game."""

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.cooldown = 0

    def apply_physics(self):
        """Apply gravity and friction to the entity."""
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        self.vx *= FRICTION

        self.x += self.vx
        self.y += self.vy

        # Wrap around screen
        if self.x > SCREEN_WIDTH:
            self.x = -self.width
        elif self.x < -self.width:
            self.x = SCREEN_WIDTH

        # Ground collision
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.cooldown > 0:
            self.cooldown -= 1

    def get_rect(self):
        """Return the collision rect for this entity."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        """Draw the entity as a vector shape."""
        # Draw a knight-like triangular shape
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height * 0.7),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(surface, self.color, points)

        # Draw eye
        eye_x = self.x + self.width // 2 + (1 if self.vx >= 0 else -1) * 8
        eye_y = self.y + self.height * 0.3
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(eye_y)), 3)


class Player(VectorEntity):
    """Player-controlled entity."""

    def __init__(self):
        super().__init__(100, SCREEN_HEIGHT // 2, 30, 40, COLOR_PLAYER)
        self.score = 0
        self.lives = PLAYER_LIVES

    def handle_input(self, keys):
        """Handle keyboard input."""
        if keys[pygame.K_UP]:
            self.vy = FLAP_STRENGTH

        if keys[pygame.K_LEFT]:
            self.vx -= MOVE_SPEED * 0.2
        if keys[pygame.K_RIGHT]:
            self.vx += MOVE_SPEED * 0.2

        # Clamp horizontal speed
        self.vx = max(-MAX_HORIZONTAL_SPEED, min(MAX_HORIZONTAL_SPEED, self.vx))


class Enemy(VectorEntity):
    """AI-controlled opponent."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, 30, 40, COLOR_ENEMY)
        self.score = 0
        self.lives = ENEMY_LIVES
        self.decision_timer = 0
        self.target_y = SCREEN_HEIGHT // 2

    def update_ai(self, player):
        """Simple AI behavior."""
        self.decision_timer += 1

        if self.decision_timer > 15:
            self.decision_timer = 0

            # Decide whether to go higher or attack
            if self.y > player.y + 50:
                # Below player - try to go higher
                self.target_y = max(50, player.y - 30)
            elif self.y < player.y - 100:
                # Too high - maybe attack or stay level
                self.target_y = player.y
            else:
                # Similar height - decide randomly
                if random.random() < 0.3:
                    self.target_y = max(50, self.y - 50)

        # Flap to reach target height
        if self.y > self.target_y + 20:
            self.vy = FLAP_STRENGTH

        # Horizontal movement
        dx = player.x - self.x

        # Account for wrap-around
        if abs(dx) > SCREEN_WIDTH / 2:
            dx = -dx

        if abs(dx) > 100:
            if dx > 0:
                self.vx += MOVE_SPEED * 0.15
            else:
                self.vx -= MOVE_SPEED * 0.15

        self.vx = max(-MAX_HORIZONTAL_SPEED * 0.7, min(MAX_HORIZONTAL_SPEED * 0.7, self.vx))


class Platform:
    """Static platform for bouncing."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PLATFORM, self.rect, border_radius=4)


class Particle:
    """Visual effect for collisions."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 30
        self.color = color
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.95

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            color = (*self.color, alpha)
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Joust: Gravity Combat")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        """Reset the game state."""
        self.player = Player()
        self.enemy = Enemy()
        self.platforms = [
            Platform(200, 450, 150, 20),
            Platform(450, 350, 150, 20),
            Platform(100, 250, 120, 20),
            Platform(580, 250, 120, 20)
        ]
        self.particles = []
        self.game_over = False
        self.winner = None
        self.message = ""
        self.message_timer = 0

    def spawn_particles(self, x, y, color, count=10):
        """Create particle explosion."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def check_collision(self):
        """Check and handle player-enemy collision."""
        if self.player.cooldown > 0 or self.enemy.cooldown > 0:
            return

        player_rect = self.player.get_rect()
        enemy_rect = self.enemy.get_rect()

        if player_rect.colliderect(enemy_rect):
            # Check who is higher
            player_above = self.player.y < self.enemy.y

            if player_above:
                # Player wins
                self.player.score += 100
                self.enemy.lives -= 1
                self.enemy.cooldown = COLLISION_COOLDOWN
                self.message = "+100 HEIGHT DOMINANCE!"
                self.spawn_particles(self.enemy.x + 15, self.enemy.y + 20, COLOR_ENEMY, 20)
            else:
                # Enemy wins
                self.enemy.score += 100
                self.player.lives -= 1
                self.player.cooldown = COLLISION_COOLDOWN
                self.message = "-50 HIT FROM ABOVE!"
                self.spawn_particles(self.player.x + 15, self.player.y + 20, COLOR_PLAYER, 20)

            self.message_timer = 60

            # Check game over
            if self.player.lives <= 0:
                self.game_over = True
                self.winner = "ENEMY"
            elif self.enemy.lives <= 0:
                self.game_over = True
                self.winner = "PLAYER"

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Handle input
        self.player.handle_input(keys)

        # Update AI
        self.enemy.update_ai(self.player)

        # Apply physics
        self.player.apply_physics()
        self.enemy.apply_physics()

        # Platform collision
        for platform in self.platforms:
            player_rect = self.player.get_rect()
            enemy_rect = self.enemy.get_rect()

            if player_rect.colliderect(platform.rect) and self.player.vy > 0:
                self.player.y = platform.rect.top - self.player.height
                self.player.vy = -self.player.vy * 0.5

            if enemy_rect.colliderect(platform.rect) and self.enemy.vy > 0:
                self.enemy.y = platform.rect.top - self.enemy.height
                self.enemy.vy = -self.enemy.vy * 0.5

        # Check player-enemy collision
        self.check_collision()

        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw entities
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

        # Draw particles
        for p in self.particles:
            p.draw(self.screen)

        # Draw HUD
        player_score = self.font.render(f"P1: {self.player.score}", True, COLOR_PLAYER)
        enemy_score = self.font.render(f"CPU: {self.enemy.score}", True, COLOR_ENEMY)

        self.screen.blit(player_score, (20, 20))
        self.screen.blit(enemy_score, (SCREEN_WIDTH - 150, 20))

        # Draw lives
        for i in range(self.player.lives):
            pygame.draw.circle(self.screen, COLOR_PLAYER, (30 + i * 25, 60), 8)
        for i in range(self.enemy.lives):
            pygame.draw.circle(self.screen, COLOR_ENEMY, (SCREEN_WIDTH - 130 + i * 25, 60), 8)

        # Draw message
        if self.message_timer > 0:
            msg = self.font.render(self.message, True, COLOR_TEXT)
            rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(msg, rect)

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.winner == "PLAYER":
                text = "VICTORY!"
                color = COLOR_PLAYER
            else:
                text = "DEFEAT!"
                color = COLOR_ENEMY

            title = self.big_font.render(text, True, color)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(title, title_rect)

            score_text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(score_text, score_rect)

            restart = self.font.render("Press SPACE to restart", True, COLOR_TEXT)
            restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(restart, restart_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()

            # Update
            self.update()

            # Draw
            self.draw()

            # Cap FPS
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the application."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
