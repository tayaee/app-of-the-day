import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Game settings
PLAYER_SPEED = 6
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 30
LASER_SPEED = 10
LASER_WIDTH = 3
LASER_HEIGHT = 15
BARRIER_BASE_SPEED = 3
BARRIER_SPEED_INCREMENT = 0.001
BARRIER_WIDTH_MIN = 50
BARRIER_WIDTH_MAX = 200
BARRIER_HEIGHT = 20
BARRIER_SPAWN_INTERVAL = 1200
CORE_NODE_RADIUS = 12


class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 60
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED

    def move(self, direction):
        if direction == "left" and self.x > self.width // 2:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width // 2:
            self.x += self.speed

    def draw(self, surface):
        # Draw vector-style starfighter
        points = [
            (self.x, self.y - self.height // 2),  # Nose
            (self.x - self.width // 2, self.y + self.height // 2),  # Bottom left
            (self.x, self.y + self.height // 4),  # Center notch
            (self.x + self.width // 2, self.y + self.height // 2),  # Bottom right
        ]
        pygame.draw.lines(surface, WHITE, True, points, 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = LASER_WIDTH
        self.height = LASER_HEIGHT
        self.active = True

    def update(self):
        self.y -= LASER_SPEED
        if self.y < 0:
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            GREEN,
            (self.x - self.width // 2, self.y, self.width, self.height)
        )

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y,
            self.width,
            self.height
        )


class Barrier:
    def __init__(self, speed):
        self.width = random.randint(BARRIER_WIDTH_MIN, BARRIER_WIDTH_MAX)
        self.x = random.randint(
            self.width // 2 + 50,
            SCREEN_WIDTH - self.width // 2 - 50
        )
        self.y = -BARRIER_HEIGHT
        self.height = BARRIER_HEIGHT
        self.speed = speed
        self.active = True
        self.has_core = random.random() < 0.4  # 40% chance of core node
        self.core_destroyed = False

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface):
        # Draw barrier
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, WHITE, rect, 2)

        # Draw core node if present
        if self.has_core and not self.core_destroyed:
            pygame.draw.circle(
                surface,
                GREEN,
                (self.x, self.y + self.height // 2),
                CORE_NODE_RADIUS,
                2
            )
            # Inner core
            pygame.draw.circle(
                surface,
                GREEN,
                (self.x, self.y + self.height // 2),
                CORE_NODE_RADIUS // 2
            )

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y,
            self.width,
            self.height
        )

    def get_core_rect(self):
        if not self.has_core or self.core_destroyed:
            return None
        return pygame.Rect(
            self.x - CORE_NODE_RADIUS,
            self.y + self.height // 2 - CORE_NODE_RADIUS,
            CORE_NODE_RADIUS * 2,
            CORE_NODE_RADIUS * 2
        )

    def destroy_core(self):
        self.core_destroyed = True


class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2.0)
        self.size = random.randint(1, 2)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, (100, 100, 100), (self.x, self.y), self.size)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Trench Run: Pursuit")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.lasers = []
        self.barriers = []
        self.stars = [Star() for _ in range(50)]
        self.barrier_speed = BARRIER_BASE_SPEED
        self.last_barrier_spawn = pygame.time.get_ticks()
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.game_over = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left")
        if keys[pygame.K_RIGHT]:
            self.player.move("right")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.lasers.append(Laser(self.player.x, self.player.y))
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()

        return True

    def update(self):
        if self.game_over:
            return

        # Update stars
        for star in self.stars:
            star.update()

        # Update score based on survival time
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time) // 1000
        self.score = elapsed_seconds * 10

        # Spawn barriers
        current_time = pygame.time.get_ticks()
        if current_time - self.last_barrier_spawn > BARRIER_SPAWN_INTERVAL:
            self.barriers.append(Barrier(self.barrier_speed))
            self.last_barrier_spawn = current_time
            # Gradually increase speed
            self.barrier_speed += BARRIER_SPEED_INCREMENT

        # Update lasers
        for laser in self.lasers[:]:
            laser.update()
            if not laser.active:
                self.lasers.remove(laser)

        # Update barriers
        for barrier in self.barriers[:]:
            barrier.update()
            if not barrier.active:
                self.barriers.remove(barrier)

        # Collision detection: lasers vs core nodes
        player_rect = self.player.get_rect()

        for laser in self.lasers[:]:
            for barrier in self.barriers:
                core_rect = barrier.get_core_rect()
                if core_rect and laser.get_rect().colliderect(core_rect):
                    barrier.destroy_core()
                    laser.active = False
                    self.score += 50
                    break

        # Remove inactive lasers
        self.lasers = [l for l in self.lasers if l.active]

        # Collision detection: player vs barriers
        for barrier in self.barriers:
            if not barrier.core_destroyed:
                barrier_rect = barrier.get_rect()
                # Check collision with the actual barrier (excluding core section)
                if player_rect.colliderect(barrier_rect):
                    self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw stars
        for star in self.stars:
            star.draw(self.screen)

        # Draw barriers
        for barrier in self.barriers:
            barrier.draw(self.screen)

        # Draw lasers
        for laser in self.lasers:
            laser.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.large_font.render("GAME OVER", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)

            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
            self.screen.blit(final_score_text, score_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
