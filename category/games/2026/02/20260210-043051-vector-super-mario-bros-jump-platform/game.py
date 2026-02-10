"""Main game loop and rendering."""

import pygame
import sys
from config import *
from entities import *


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros - Jump Platform")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.state = GameState()

    def run(self) -> None:
        """Main game loop."""
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self) -> None:
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.state.handle_jump()
                elif event.key == pygame.K_r and (self.state.game_over or self.state.victory):
                    self.state.reset()

    def _update(self) -> None:
        """Update game state."""
        keys = pygame.key.get_pressed()
        input_keys = (keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_SPACE])
        self.state.update(input_keys)

    def _draw(self) -> None:
        """Draw everything."""
        self.screen.fill(COLOR_BG)

        # Draw ground pattern
        self._draw_background()

        # Draw platforms
        for platform in self.state.platforms:
            platform.draw(self.screen, self.state.camera.offset_x)

        # Draw flagpole
        self.state.flagpole.draw(self.screen, self.state.camera.offset_x)

        # Draw player
        self.state.player.draw(self.screen, self.state.camera.offset_x)

        # Draw UI
        self._draw_ui()

        pygame.display.flip()

    def _draw_background(self) -> None:
        """Draw background elements."""
        # Ground line
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        pygame.draw.line(self.screen, (60, 50, 40), (0, ground_y), (SCREEN_WIDTH, ground_y), 3)

        # Distance markers
        for x in range(0, LEVEL_WIDTH, 200):
            screen_x = int(x - self.state.camera.offset_x)
            if -50 < screen_x < SCREEN_WIDTH + 50:
                pygame.draw.line(self.screen, (40, 40, 60), (screen_x, ground_y), (screen_x, SCREEN_HEIGHT), 1)
                label = self.small_font.render(f"{x // 10}m", True, (80, 80, 100))
                self.screen.blit(label, (screen_x + 5, ground_y + 10))

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # HUD
        time_color = (255, 100, 100) if self.state.time_left < 30 else COLOR_TEXT
        time_text = self.font.render(f"Time: {int(self.state.time_left)}", True, time_color)
        dist_text = self.font.render(f"Distance: {int(self.state.player.max_distance // 10)}m", True, COLOR_TEXT)

        self.screen.blit(time_text, (SCREEN_WIDTH - 180, 10))
        self.screen.blit(dist_text, (10, 10))

        # Progress bar
        bar_width = 200
        bar_height = 10
        progress = min(self.state.player.max_distance / LEVEL_WIDTH, 1.0)
        pygame.draw.rect(self.screen, (60, 60, 80), (10, 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, (100, 200, 100), (10, 50, int(bar_width * progress), bar_height))

        # Start screen
        if self.state.waiting_start:
            self._draw_overlay("VECTOR PLATFORM JUMPER", "Press SPACE to start", "LEFT/RIGHT: Move | SPACE: Jump")

        # Game over
        elif self.state.game_over:
            self._draw_overlay("GAME OVER", "You fell!", "Press R to retry")

        # Victory
        elif self.state.victory:
            self._draw_overlay("VICTORY!", f"Score: {self.state.score}", f"Time Bonus: {int(self.state.time_left * 5)} | Press R to replay")

    def _draw_overlay(self, title: str, subtitle: str, info: str) -> None:
        """Draw overlay screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font.render(title, True, COLOR_FLAG if self.state.victory else (255, 100, 100))
        subtitle_surf = self.font.render(subtitle, True, COLOR_TEXT)
        info_surf = self.small_font.render(info, True, (180, 180, 180))

        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(info_surf, (SCREEN_WIDTH // 2 - info_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
