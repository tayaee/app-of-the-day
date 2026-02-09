"""Renderer for Vector Super Mario World Physics."""

import pygame
from game import GameState, Vec2


class Renderer:
    def __init__(self, state: GameState):
        self.state = state
        self.screen = pygame.display.set_mode((state.width, state.height))
        pygame.display.set_caption("Vector Super Mario World Physics")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.bg_color = (20, 20, 40)
        self.platform_color = (100, 80, 60)
        self.platform_top_color = (140, 120, 100)
        self.player_color = (255, 100, 100)
        self.enemy_color = (150, 100, 50)
        self.coin_color = (255, 215, 0)
        self.flag_color = (50, 200, 50)
        self.flag_pole_color = (150, 150, 150)
        self.text_color = (255, 255, 255)

    def render(self):
        self.screen.fill(self.bg_color)

        # Draw platforms
        for plat in self.state.platforms:
            rect = (plat['x'], plat['y'], plat['w'], plat['h'])
            pygame.draw.rect(self.screen, self.platform_color, rect)
            # Platform top highlight
            top_rect = (plat['x'], plat['y'], plat['w'], 4)
            pygame.draw.rect(self.screen, self.platform_top_color, top_rect)

        # Draw coins
        for coin in self.state.coins:
            if not coin.collected:
                pygame.draw.circle(self.screen, self.coin_color,
                                 (int(coin.pos.x), int(coin.pos.y)), coin.radius)
                pygame.draw.circle(self.screen, (255, 255, 200),
                                 (int(coin.pos.x), int(coin.pos.y)), coin.radius - 3)

        # Draw enemies
        for enemy in self.state.enemies:
            if enemy.alive:
                rect = (int(enemy.pos.x), int(enemy.pos.y), enemy.width, enemy.height)
                pygame.draw.rect(self.screen, self.enemy_color, rect)
                # Eyes
                eye_y = int(enemy.pos.y) + 8
                pygame.draw.circle(self.screen, (255, 255, 255), (int(enemy.pos.x) + 8, eye_y), 5)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(enemy.pos.x) + 20, eye_y), 5)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(enemy.pos.x) + 8, eye_y), 2)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(enemy.pos.x) + 20, eye_y), 2)

        # Draw flag
        pole_start = (int(self.state.flag_x), int(self.state.flag_y))
        pole_end = (int(self.state.flag_x), int(self.state.flag_y) + 200)
        pygame.draw.line(self.screen, self.flag_pole_color, pole_start, pole_end, 4)
        flag_points = [
            pole_start,
            (int(self.state.flag_x) + 40, int(self.state.flag_y) + 20),
            pole_start
        ]
        pygame.draw.polygon(self.screen, self.flag_color, flag_points)

        # Draw player
        if self.state.player.alive:
            px, py = int(self.state.player.pos.x), int(self.state.player.pos.y)
            pw, ph = self.state.player.width, self.state.player.height

            # Body
            pygame.draw.rect(self.screen, self.player_color, (px, py, pw, ph))

            # Face
            face_x = px + 6 if self.state.player.facing_right else px + 4
            eye_x = px + 16 if self.state.player.facing_right else px + 6
            pygame.draw.circle(self.screen, (255, 200, 180), (face_x, py + 10), 6)
            pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, py + 10), 2)

            # Hat
            pygame.draw.rect(self.screen, (200, 50, 50), (px + 2, py - 4, pw - 4, 8))

        # Draw HUD
        score_text = self.font.render(f"Score: {self.state.score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))

        # Game over / win message
        if self.state.game_over:
            if self.state.win:
                msg = "LEVEL COMPLETE! Press R to restart"
                color = (100, 255, 100)
            else:
                msg = "GAME OVER! Press R to restart"
                color = (255, 100, 100)

            text = self.font.render(msg, True, color)
            rect = text.get_rect(center=(self.state.width // 2, self.state.height // 2))
            self.screen.blit(text, rect)

        pygame.display.flip()
