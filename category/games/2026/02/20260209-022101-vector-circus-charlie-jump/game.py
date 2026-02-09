"""Main game logic."""

import pygame
import sys

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_GROUND, COLOR_TEXT,
    STAGE_LENGTH
)
from player import Player
from obstacles import ObstacleManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Circus Charlie Jump")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset()

    def reset(self):
        self.player = Player(100, 350)
        self.obstacle_manager = ObstacleManager()
        self.distance = 0
        self.score = 0
        self.game_over = False
        self.victory = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if self.game_over or self.victory:
                        self.reset()
                    else:
                        self.player.jump()

    def update(self):
        if self.game_over or self.victory:
            return

        self.player.update()
        self.distance += 4

        self.obstacle_manager.update(4, self.distance)

        player_rect = self.player.get_rect()

        if self.obstacle_manager.check_collisions(player_rect):
            self.game_over = True

        self.score += self.obstacle_manager.check_passes(player_rect)
        self.score += self.obstacle_manager.check_bonus(player_rect)

        if self.distance >= STAGE_LENGTH:
            self.victory = True

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw ground
        pygame.draw.rect(self.screen, COLOR_GROUND, (0, 350, SCREEN_WIDTH, 50))

        # Draw progress bar at top
        progress = min(1.0, self.distance / STAGE_LENGTH)
        pygame.draw.rect(self.screen, (50, 50, 50), (50, 10, SCREEN_WIDTH - 100, 10))
        pygame.draw.rect(self.screen, (0, 200, 100), (50, 10, (SCREEN_WIDTH - 100) * progress, 10))

        # Draw finish line if near
        if STAGE_LENGTH - self.distance < SCREEN_WIDTH:
            finish_x = STAGE_LENGTH - self.distance
            pygame.draw.line(self.screen, (255, 255, 255), (finish_x, 50), (finish_x, 350), 3)

        self.obstacle_manager.draw(self.screen)
        self.player.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 30))

        # Draw game over or victory message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press SPACE to restart", True, (255, 50, 50))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        elif self.victory:
            victory_text = self.font.render(f"VICTORY! Score: {self.score} - Press SPACE", True, (50, 255, 50))
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(victory_text, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
