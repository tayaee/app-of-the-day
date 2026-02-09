"""Renderer for Vector Tapper Root Beer Dash."""

import pygame


class Renderer:
    """Handles all rendering for the game."""

    def __init__(self, game_state):
        self.state = game_state
        self.width = game_state.SCREEN_WIDTH
        self.height = game_state.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vector Tapper Root Beer Dash")

        # Colors
        self.bg_color = (25, 20, 35)
        self.bar_color = (70, 55, 45)
        self.bar_outline = (110, 90, 70)
        self.tap_color = (100, 100, 120)
        self.tap_highlight = (150, 150, 170)
        self.bartender_color = (60, 160, 210)
        self.customer_color = (210, 90, 90)
        self.beer_color = (210, 150, 60)
        self.beer_foam_color = (250, 240, 230)
        self.mug_color = (160, 160, 160)
        self.mug_outline = (100, 100, 100)
        self.text_color = (230, 230, 230)
        self.score_color = (255, 220, 80)

        # Fonts
        self.title_font = pygame.font.Font(None, 52)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def clear(self) -> None:
        """Clear the screen."""
        self.screen.fill(self.bg_color)

    def draw_bar(self, bar_index: int) -> None:
        """Draw a single bar."""
        y = self.state.get_bar_y(bar_index)
        x = 60
        width = self.state.BAR_WIDTH
        height = self.state.BAR_HEIGHT

        # Bar surface
        bar_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.bar_color, bar_rect)
        pygame.draw.rect(self.screen, self.bar_outline, bar_rect, 3)

        # Wood grain lines
        for i in range(3):
            grain_y = y + 15 + i * 25
            pygame.draw.line(
                self.screen,
                (55, 45, 38),
                (x + 10, grain_y),
                (x + width - 10, grain_y),
                1
            )

        # Tap/root beer keg at left end
        tap_rect = pygame.Rect(15, y + 15, 45, 50)
        pygame.draw.rect(self.screen, self.tap_color, tap_rect)
        pygame.draw.rect(self.screen, self.tap_highlight, tap_rect, 2)

        # Tap nozzle
        nozzle_rect = pygame.Rect(55, y + 32, 15, 16)
        pygame.draw.rect(self.screen, (80, 80, 100), nozzle_rect)

        # Root beer label
        label_rect = pygame.Rect(20, y + 25, 35, 30)
        pygame.draw.rect(self.screen, (180, 100, 50), label_rect)
        label_text = self.small_font.render("RB", True, (255, 255, 255))
        self.screen.blit(label_text, (28, y + 32))

    def draw_bartender(self) -> None:
        """Draw the bartender at current bar."""
        y = self.state.get_bar_y(self.state.bartender_bar) + 10
        x = 30

        # Body
        body_rect = pygame.Rect(x - 15, y, 30, 55)
        pygame.draw.rect(self.screen, self.bartender_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 2)

        # Head
        head_rect = pygame.Rect(x - 12, y - 18, 24, 22)
        pygame.draw.rect(self.screen, self.bartender_color, head_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), head_rect, 2)

        # Eyes
        pygame.draw.rect(self.screen, (255, 255, 255), (x - 6, y - 12, 5, 5))
        pygame.draw.rect(self.screen, (255, 255, 255), (x + 1, y - 12, 5, 5))

        # Apron
        apron_rect = pygame.Rect(x - 13, y + 12, 26, 38)
        pygame.draw.rect(self.screen, (250, 250, 250), apron_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), apron_rect, 1)

        # Arm holding tray
        arm_rect = pygame.Rect(x + 5, y + 25, 20, 8)
        pygame.draw.rect(self.screen, self.bartender_color, arm_rect)
        tray_rect = pygame.Rect(x + 22, y + 22, 12, 14)
        pygame.draw.rect(self.screen, (180, 180, 180), tray_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), tray_rect, 1)

    def draw_customer(self, customer) -> None:
        """Draw a customer."""
        y = self.state.get_bar_y(customer.bar_index) + 20
        x = int(customer.x)

        # Body
        body_rect = pygame.Rect(x, y, 28, 42)
        pygame.draw.rect(self.screen, self.customer_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 2)

        # Head
        head_rect = pygame.Rect(x + 3, y - 15, 22, 20)
        pygame.draw.rect(self.screen, self.customer_color, head_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), head_rect, 2)

        # Eyes (looking toward drinks)
        eye_x = x + 8
        pygame.draw.rect(self.screen, (255, 255, 255), (eye_x, y - 10, 4, 4))
        pygame.draw.rect(self.screen, (255, 255, 255), (eye_x + 7, y - 10, 4, 4))

        # Thirsty mouth
        mouth_rect = pygame.Rect(x + 8, y - 2, 12, 4)
        pygame.draw.rect(self.screen, (100, 50, 50), mouth_rect)

    def draw_mug(self, mug) -> None:
        """Draw a mug (full or empty)."""
        y = self.state.get_bar_y(mug.bar_index) + 32
        x = int(mug.x)

        if mug.is_full:
            # Full mug with root beer
            # Glass body
            glass_rect = pygame.Rect(x, y, 22, 28)
            pygame.draw.rect(self.screen, (200, 200, 220), glass_rect, 2)

            # Root beer liquid
            liquid_rect = pygame.Rect(x + 2, y + 8, 18, 18)
            pygame.draw.rect(self.screen, self.beer_color, liquid_rect)

            # Foam on top
            foam_rect = pygame.Rect(x + 1, y + 4, 20, 6)
            pygame.draw.rect(self.screen, self.beer_foam_color, foam_rect)

            # Foam bubbles
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 5, y + 5), 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 11, y + 3), 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 17, y + 5), 2)
        else:
            # Empty mug
            mug_rect = pygame.Rect(x, y, 22, 20)
            pygame.draw.rect(self.screen, self.mug_color, mug_rect)
            pygame.draw.rect(self.screen, self.mug_outline, mug_rect, 2)

            # Handle
            handle_rect = pygame.Rect(x - 6, y + 2, 7, 16)
            pygame.draw.rect(self.screen, self.mug_outline, handle_rect, 2)

            # Empty interior
            inner_rect = pygame.Rect(x + 3, y + 3, 16, 14)
            pygame.draw.rect(self.screen, (80, 80, 80), inner_rect)

    def draw_ui(self) -> None:
        """Draw UI elements."""
        # Score
        score_text = self.font.render(f"Score: {self.state.score}", True, self.score_color)
        self.screen.blit(score_text, (15, 15))

        # Current bar indicator
        bar_text = self.small_font.render(
            f"Bar: {self.state.bartender_bar + 1}/{self.state.NUM_BARS}",
            True, self.text_color
        )
        self.screen.blit(bar_text, (15, 50))

        # Instructions on start
        if self.state.score == 0 and not self.state.game_over:
            inst_y = self.height - 100
            instructions = [
                "UP/DOWN: Move between bars",
                "SPACE: Pour and slide root beer",
                "ESC: Quit"
            ]
            for i, inst in enumerate(instructions):
                inst_text = self.small_font.render(inst, True, (140, 140, 160))
                self.screen.blit(
                    inst_text,
                    (self.width // 2 - inst_text.get_width() // 2, inst_y + i * 22)
                )

    def draw_game_over(self) -> None:
        """Draw game over screen."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        go_text = self.title_font.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(go_text, (self.width // 2 - go_text.get_width() // 2, 200))

        # Reason
        reason_text = self.font.render(self.state.game_over_reason, True, self.text_color)
        self.screen.blit(reason_text, (self.width // 2 - reason_text.get_width() // 2, 270))

        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, self.score_color)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 320))

        # Restart instruction
        restart_text = self.small_font.render(
            "Press R to restart or ESC to quit",
            True, (170, 170, 170)
        )
        self.screen.blit(
            restart_text,
            (self.width // 2 - restart_text.get_width() // 2, 380)
        )

    def render(self) -> None:
        """Render the complete game."""
        self.clear()

        # Draw all bars
        for i in range(self.state.NUM_BARS):
            self.draw_bar(i)

        # Draw customers
        for customer in self.state.customers:
            self.draw_customer(customer)

        # Draw mugs
        for mug in self.state.mugs:
            if mug.active:
                self.draw_mug(mug)

        # Draw bartender
        self.draw_bartender()

        # Draw UI
        self.draw_ui()

        # Draw game over if needed
        if self.state.game_over:
            self.draw_game_over()

        pygame.display.flip()
