"""
Vector Adventure Island Jump
A minimalist side-scrolling platformer inspired by the classic Adventure Island.
Navigate a prehistoric landscape, jump over obstacles, and collect fruit to maintain stamina.
"""

import pygame
import sys
import random
from pathlib import Path

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
COLOR_BG = (135, 206, 235)  # Sky blue
COLOR_GROUND = (139, 90, 43)  # Brown
COLOR_GRASS = (34, 139, 34)  # Forest green
COLOR_PLAYER = (255, 100, 100)  # Light red
COLOR_PLAYER_DUCK = (200, 80, 80)  # Darker red when ducking
COLOR_ROCK = (128, 128, 128)  # Gray
COLOR_SNAIL = (128, 0, 128)  # Purple
COLOR_FRUIT = (255, 165, 0)  # Orange
COLOR_STAMINA_FULL = (0, 255, 0)  # Green
COLOR_STAMINA_LOW = (255, 0, 0)  # Red
COLOR_STAMINA_BG = (50, 50, 50)  # Dark gray
COLOR_TEXT = (0, 0, 0)
COLOR_CLOUD = (255, 255, 255)

# Physics
GRAVITY = 0.6
JUMP_FORCE = -13
DOUBLE_JUMP_FORCE = -11

# Game settings
GROUND_Y = SCREEN_HEIGHT - 60
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40
PLAYER_DUCK_HEIGHT = 20
BASE_SCROLL_SPEED = 4
STAMINA_MAX = 100
STAMINA_DEPLETION_RATE = 0.05
STAMINA_FRUIT_BONUS = 30
SPEED_INCREASE_INTERVAL = 100


class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = 100
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.on_ground = True
        self.is_jumping = False
        self.can_double_jump = False
        self.is_ducking = False
        self.stamina = STAMINA_MAX
        self.alive = True

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.is_jumping = True
            self.can_double_jump = True
        elif self.can_double_jump:
            self.vel_y = DOUBLE_JUMP_FORCE
            self.can_double_jump = False

    def duck(self, ducking):
        self.is_ducking = ducking
        if ducking:
            self.height = PLAYER_DUCK_HEIGHT
        else:
            self.height = PLAYER_HEIGHT
        if self.on_ground:
            self.y = GROUND_Y - self.height

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Ground collision
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
            self.is_jumping = False
            self.can_double_jump = False

        # Stamina depletion
        self.stamina -= STAMINA_DEPLETION_RATE
        if self.stamina <= 0:
            self.alive = False

    def draw(self, surface):
        color = COLOR_PLAYER_DUCK if self.is_ducking else COLOR_PLAYER
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))

        # Draw simple eyes
        eye_color = (0, 0, 0)
        eye_y = self.y + 8 if not self.is_ducking else self.y + 5
        pygame.draw.circle(surface, eye_color, (self.x + 20, eye_y), 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    def __init__(self, x, obstacle_type):
        self.x = x
        self.type = obstacle_type
        self.passed = False

        if self.type == "rock":
            self.width = 25
            self.height = 25
            self.y = GROUND_Y - self.height
            self.color = COLOR_ROCK
        elif self.type == "snail":
            self.width = 30
            self.height = 20
            self.y = GROUND_Y - self.height
            self.color = COLOR_SNAIL
            self.move_speed = 1.5

    def update(self, scroll_speed):
        self.x -= scroll_speed
        if self.type == "snail":
            # Snails move slowly left
            self.x -= self.move_speed

    def draw(self, surface):
        if self.type == "rock":
            # Draw triangle rock
            points = [
                (self.x, self.y + self.height),
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(surface, self.color, points)
        elif self.type == "snail":
            # Draw snail body (rectangle)
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            # Draw shell (circle)
            shell_x = self.x + self.width - 10
            shell_y = self.y + 5
            pygame.draw.circle(surface, (100, 50, 100), (shell_x, shell_y), 8)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_off_screen(self):
        return self.x + self.width < 0


class Fruit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.bob_offset = random.random() * 6.28
        self.time = 0

    def update(self, scroll_speed):
        self.x -= scroll_speed
        self.time += 0.1

    def draw(self, surface):
        if self.collected:
            return

        # Bobbing animation
        bob_y = self.y + int(5 * (self.time + self.bob_offset))

        # Draw fruit (circle)
        pygame.draw.circle(surface, COLOR_FRUIT, (self.x, bob_y), self.radius)
        # Draw highlight
        pygame.draw.circle(surface, (255, 200, 100), (self.x - 3, bob_y - 3), 4)

    def get_rect(self):
        bob_y = self.y + int(5 * (self.time + self.bob_offset))
        return pygame.Rect(self.x - self.radius, bob_y - self.radius,
                          self.radius * 2, self.radius * 2)

    def is_off_screen(self):
        return self.x + self.radius < 0


class Cloud:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 0.3 + random.random() * 0.3

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        # Draw simple cloud (3 overlapping circles)
        pygame.draw.circle(surface, COLOR_CLOUD, (self.x, self.y), self.size)
        pygame.draw.circle(surface, COLOR_CLOUD, (self.x + self.size, self.y - 5), int(self.size * 0.8))
        pygame.draw.circle(surface, COLOR_CLOUD, (self.x + self.size * 2, self.y), int(self.size * 0.9))

    def is_off_screen(self):
        return self.x + self.size * 3 < 0


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Adventure Island Jump")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.fruits = []
        self.clouds = []

        # Initialize clouds
        for i in range(5):
            self.clouds.append(Cloud(
                100 + i * 200,
                50 + random.randint(0, 50),
                20 + random.randint(0, 15)
            ))

        self.score = 0
        self.scroll_speed = BASE_SCROLL_SPEED
        self.frame_count = 0
        self.game_over = False
        self.next_obstacle_distance = 200

    def spawn_obstacle(self):
        if self.next_obstacle_distance <= 0:
            obstacle_type = random.choice(["rock", "rock", "snail"])
            self.obstacles.append(Obstacle(SCREEN_WIDTH + 50, obstacle_type))

            # Set distance to next obstacle
            min_distance = 250 if self.scroll_speed < 6 else 200
            self.next_obstacle_distance = min_distance + random.randint(0, 150)

            # Maybe spawn fruit with obstacle
            if random.random() < 0.5:
                fruit_y = GROUND_Y - 60 - random.randint(0, 40)
                self.fruits.append(Fruit(SCREEN_WIDTH + 100, fruit_y))

    def spawn_fruit(self):
        # Occasionally spawn floating fruit
        if random.random() < 0.01:
            fruit_y = GROUND_Y - 80 - random.randint(0, 60)
            self.fruits.append(Fruit(SCREEN_WIDTH, fruit_y))

    def update(self):
        if self.game_over:
            return

        self.frame_count += 1
        self.score += 1

        # Increase difficulty
        if self.score % SPEED_INCREASE_INTERVAL == 0 and self.scroll_speed < 10:
            self.scroll_speed += 0.2

        # Update player
        self.player.update()

        if not self.player.alive:
            self.game_over = True
            return

        # Update clouds
        for cloud in self.clouds[:]:
            cloud.update()
            if cloud.is_off_screen():
                self.clouds.remove(cloud)
                self.clouds.append(Cloud(
                    SCREEN_WIDTH + 50,
                    50 + random.randint(0, 50),
                    20 + random.randint(0, 15)
                ))

        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.scroll_speed)
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                if not obstacle.passed:
                    obstacle.passed = True

        # Update fruits
        for fruit in self.fruits[:]:
            fruit.update(self.scroll_speed)
            if fruit.is_off_screen():
                self.fruits.remove(fruit)

        # Spawn new obstacles and fruits
        self.next_obstacle_distance -= self.scroll_speed
        self.spawn_obstacle()
        self.spawn_fruit()

        # Check collisions
        self.check_collisions()

    def check_collisions(self):
        player_rect = self.player.get_rect()

        # Obstacle collision
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                # If ducking under rock, check if player is low enough
                if obstacle.type == "rock" and self.player.is_ducking:
                    # Rock hitbox is smaller when ducking
                    hitbox = obstacle.get_rect()
                    hitbox.height = 10
                    hitbox.y = obstacle.y + obstacle.height - 10
                    if not player_rect.colliderect(hitbox):
                        continue
                self.player.alive = False
                return

        # Fruit collection
        for fruit in self.fruits:
            if not fruit.collected and player_rect.colliderect(fruit.get_rect()):
                fruit.collected = True
                self.player.stamina = min(STAMINA_MAX, self.player.stamina + STAMINA_FRUIT_BONUS)
                self.score += 50

    def draw(self):
        # Draw background
        self.screen.fill(COLOR_BG)

        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)

        # Draw ground
        pygame.draw.rect(self.screen, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, 60))
        pygame.draw.rect(self.screen, COLOR_GRASS, (0, GROUND_Y, SCREEN_WIDTH, 10))

        # Draw fruits
        for fruit in self.fruits:
            fruit.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Stamina bar
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 40

        # Background
        pygame.draw.rect(self.screen, COLOR_STAMINA_BG, (bar_x, bar_y, bar_width, bar_height))

        # Stamina fill
        fill_width = int(bar_width * (self.player.stamina / STAMINA_MAX))
        stamina_color = COLOR_STAMINA_FULL if self.player.stamina > 30 else COLOR_STAMINA_LOW
        pygame.draw.rect(self.screen, stamina_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Stamina text
        stamina_text = self.small_font.render("Stamina", True, COLOR_TEXT)
        self.screen.blit(stamina_text, (bar_x + bar_width + 10, bar_y))

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(game_over_text, game_over_rect)

        # Score text
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # Restart text
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if not self.game_over:
                            self.player.jump()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.player.duck(False)

            # Handle continuous duck key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN] and not self.game_over:
                self.player.duck(True)

            # Update
            self.update()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
