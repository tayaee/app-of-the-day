import pygame
import sys
import random
from enum import Enum
from typing import List, Optional

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Layout
LANE_COUNT = 4
LANE_HEIGHT = 100
LANE_START_Y = 100
CHEF_WIDTH = 60
CHEF_HEIGHT = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)

# Sushi colors (3 types)
SUSHI_COLORS = [
    (255, 100, 100),  # Red - Salmon
    (100, 255, 100),  # Green - Cucumber
    (100, 100, 255),  # Blue - Tuna
]

SUSHI_NAMES = ["SALMON", "CUCUMBER", "TUNA"]

# Game settings
INITIAL_CUSTOMER_SPEED = 1.5
SPEED_INCREMENT = 0.1
SPAWN_INTERVAL_MIN = 120  # frames
SPAWN_INTERVAL_MAX = 240  # frames

# Scoring
POINTS_CORRECT = 100
POINTS_WRONG = -50
STARTING_LIVES = 3


class SushiType(Enum):
    SALMON = 0
    CUCUMBER = 1
    TUNA = 2


class Customer:
    def __init__(self, lane: int):
        self.lane = lane
        self.x = SCREEN_WIDTH - 80
        self.y = LANE_START_Y + lane * LANE_HEIGHT + LANE_HEIGHT // 2
        self.sushi_type = random.choice(list(SushiType))
        self.radius = 25
        self.speed = INITIAL_CUSTOMER_SPEED

    def update(self, speed_multiplier: float = 1.0):
        self.x -= self.speed * speed_multiplier

    def draw(self, surface: pygame.Surface):
        # Draw customer body
        color = SUSHI_COLORS[self.sushi_type.value]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

        # Draw sushi indicator text
        font = pygame.font.Font(None, 24)
        text = font.render(str(self.sushi_type.value + 1), True, BLACK)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text, text_rect)

    def is_off_screen(self) -> bool:
        return self.x < -self.radius

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class ProjectileSushi:
    def __init__(self, lane: int, sushi_type: SushiType):
        self.lane = lane
        self.x = CHEF_WIDTH + 20
        self.y = LANE_START_Y + lane * LANE_HEIGHT + LANE_HEIGHT // 2
        self.sushi_type = sushi_type
        self.radius = 15
        self.speed = 8

    def update(self):
        self.x += self.speed

    def draw(self, surface: pygame.Surface):
        color = SUSHI_COLORS[self.sushi_type.value]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

        # Draw number
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.sushi_type.value + 1), True, BLACK)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text, text_rect)

    def is_off_screen(self) -> bool:
        return self.x > SCREEN_WIDTH + self.radius

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Tapper: Sushi Conveyor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.customers: List[Customer] = []
        self.projectiles: List[ProjectileSushi] = []
        self.current_lane = 0
        self.lives = STARTING_LIVES
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
        self.speed_multiplier = 1.0
        self.missed_display_timer = 0
        self.missed_display_pos = None

    def spawn_customer(self):
        # Find lanes with no customers nearby
        available_lanes = []
        for lane in range(LANE_COUNT):
            can_spawn = True
            for customer in self.customers:
                if customer.lane == lane and customer.x > SCREEN_WIDTH - 200:
                    can_spawn = False
                    break
            if can_spawn:
                available_lanes.append(lane)

        if available_lanes:
            lane = random.choice(available_lanes)
            customer = Customer(lane)
            customer.speed = INITIAL_CUSTOMER_SPEED * self.speed_multiplier
            self.customers.append(customer)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_UP:
                        self.current_lane = max(0, self.current_lane - 1)
                    elif event.key == pygame.K_DOWN:
                        self.current_lane = min(LANE_COUNT - 1, self.current_lane + 1)
                    elif event.key == pygame.K_1:
                        self.throw_sushi(SushiType.SALMON)
                    elif event.key == pygame.K_2:
                        self.throw_sushi(SushiType.CUCUMBER)
                    elif event.key == pygame.K_3:
                        self.throw_sushi(SushiType.TUNA)
        return True

    def throw_sushi(self, sushi_type: SushiType):
        projectile = ProjectileSushi(self.current_lane, sushi_type)
        self.projectiles.append(projectile)

    def update(self):
        if self.game_over:
            return

        # Update spawn timer
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_interval = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
            self.spawn_customer()

        # Update customers
        for customer in self.customers[:]:
            customer.update()
            if customer.is_off_screen():
                self.customers.remove(customer)
                self.lives -= 1
                self.missed_display_timer = 60
                self.missed_display_pos = (50, customer.y)
                if self.lives <= 0:
                    self.game_over = True

        # Update projectiles and check collisions
        for projectile in self.projectiles[:]:
            projectile.update()
            hit = False
            for customer in self.customers[:]:
                if customer.lane == projectile.lane:
                    if projectile.get_rect().colliderect(customer.get_rect()):
                        # Check if correct sushi type
                        if projectile.sushi_type == customer.sushi_type:
                            self.score += POINTS_CORRECT
                            # Increase speed every 500 points
                            if self.score % 500 == 0:
                                self.speed_multiplier += SPEED_INCREMENT
                        else:
                            self.score += POINTS_WRONG
                            self.lives -= 1
                            if self.lives <= 0:
                                self.game_over = True
                        self.customers.remove(customer)
                        hit = True
                        break
            if hit or projectile.is_off_screen():
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)

        # Update missed display timer
        if self.missed_display_timer > 0:
            self.missed_display_timer -= 1

    def draw(self):
        self.screen.fill(BLACK)

        # Draw lanes
        for i in range(LANE_COUNT):
            y = LANE_START_Y + i * LANE_HEIGHT
            color = DARK_GRAY if i == self.current_lane else GRAY
            pygame.draw.rect(self.screen, color, (0, y, SCREEN_WIDTH, LANE_HEIGHT - 2))
            pygame.draw.rect(self.screen, WHITE, (0, y, SCREEN_WIDTH, LANE_HEIGHT - 2), 1)

            # Draw lane number
            lane_text = self.small_font.render(f"LANE {i + 1}", True, WHITE)
            self.screen.blit(lane_text, (SCREEN_WIDTH - 80, y + 5))

        # Draw conveyor belt direction arrows
        for i in range(LANE_COUNT):
            y = LANE_START_Y + i * LANE_HEIGHT + LANE_HEIGHT // 2
            for x in range(200, SCREEN_WIDTH, 150):
                pygame.draw.polygon(self.screen, (70, 70, 70), [
                    (x, y - 10),
                    (x - 15, y),
                    (x, y + 10)
                ])

        # Draw chef area
        chef_y = LANE_START_Y + self.current_lane * LANE_HEIGHT
        pygame.draw.rect(self.screen, (150, 100, 50), (0, chef_y, CHEF_WIDTH, LANE_HEIGHT - 2))
        pygame.draw.rect(self.screen, WHITE, (0, chef_y, CHEF_WIDTH, LANE_HEIGHT - 2), 2)

        # Draw chef
        chef_center_y = chef_y + LANE_HEIGHT // 2
        pygame.draw.circle(self.screen, (255, 200, 150), (CHEF_WIDTH // 2, int(chef_center_y)), 20)
        # Chef hat
        pygame.draw.rect(self.screen, WHITE, (CHEF_WIDTH // 2 - 15, int(chef_center_y) - 35, 30, 20))

        # Draw customers
        for customer in self.customers:
            customer.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw missed indicator
        if self.missed_display_timer > 0 and self.missed_display_pos:
            alpha = min(255, self.missed_display_timer * 5)
            miss_text = self.font.render("MISSED!", True, (255, 0, 0))
            miss_text.set_alpha(alpha)
            self.screen.blit(miss_text, self.missed_display_pos)

        # Draw header
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, LANE_START_Y))

        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 30))

        # Draw lives
        lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 30))

        # Draw sushi key legend
        legend_y = 30
        for i, color in enumerate(SUSHI_COLORS):
            key_text = self.small_font.render(f"{i + 1}: {SUSHI_NAMES[i]}", True, color)
            self.screen.blit(key_text, (200 + i * 130, legend_y))

        # Draw controls help
        controls_text = self.small_font.render("UP/DOWN: Change Lane | 1-3: Throw Sushi", True, (200, 200, 200))
        self.screen.blit(controls_text, (20, 70))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart or ESC to Quit", True, (200, 200, 200))

            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(final_score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)

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


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
