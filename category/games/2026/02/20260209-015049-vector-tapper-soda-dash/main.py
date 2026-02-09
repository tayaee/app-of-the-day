"""Vector Tapper Soda Dash - A fast-paced arcade game."""

import pygame
import sys
from entities import GameState


class Renderer:
    """Handles all rendering for the game."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Vector Tapper Soda Dash")

        # Colors
        self.bg_color = (20, 20, 30)
        self.bar_color = (60, 50, 40)
        self.bar_outline = (100, 80, 60)
        self.bartender_color = (50, 150, 200)
        self.customer_color = (200, 80, 80)
        self.drink_color = (255, 200, 50)
        self.mug_color = (150, 150, 150)
        self.text_color = (220, 220, 220)

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

    def clear(self) -> None:
        """Clear the screen."""
        self.screen.fill(self.bg_color)

    def draw_bar(self, state: GameState, bar_index: int) -> None:
        """Draw a single bar."""
        y = state.get_bar_y(bar_index)
        bar_rect = pygame.Rect(60, y, state.bar_width, state.bar_height)

        # Draw bar surface
        pygame.draw.rect(self.screen, self.bar_color, bar_rect)
        pygame.draw.rect(self.screen, self.bar_outline, bar_rect, 3)

        # Draw tap at left end
        tap_rect = pygame.Rect(20, y + 20, 40, 40)
        pygame.draw.rect(self.screen, (100, 100, 120), tap_rect)
        pygame.draw.rect(self.screen, (150, 150, 170), tap_rect, 2)

    def draw_bartender(self, state: GameState) -> None:
        """Draw the bartender."""
        y = state.get_bar_y(state.bartender_bar) + 10
        x = int(state.bartender_x)

        # Body
        body_rect = pygame.Rect(x - 15, y, 30, 50)
        pygame.draw.rect(self.screen, self.bartender_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 2)

        # Head
        head_rect = pygame.Rect(x - 10, y - 15, 20, 20)
        pygame.draw.rect(self.screen, self.bartender_color, head_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), head_rect, 2)

        # Apron
        apron_rect = pygame.Rect(x - 12, y + 10, 24, 35)
        pygame.draw.rect(self.screen, (240, 240, 240), apron_rect)

    def draw_customer(self, state: GameState, customer) -> None:
        """Draw a customer."""
        y = state.get_bar_y(customer.bar_index) + 15
        x = int(customer.x)

        # Body
        body_rect = pygame.Rect(x, y, 25, 40)
        pygame.draw.rect(self.screen, self.customer_color, body_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 2)

        # Head
        head_rect = pygame.Rect(x + 2, y - 12, 20, 18)
        pygame.draw.rect(self.screen, self.customer_color, head_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), head_rect, 2)

        # Thirst indicator
        thirst_width = int(20 * (customer.patience / 100.0))
        thirst_rect = pygame.Rect(x + 2, y + 45, thirst_width, 5)
        pygame.draw.rect(self.screen, (255, 100, 100), thirst_rect)

    def draw_drink(self, state: GameState, drink) -> None:
        """Draw a drink."""
        y = state.get_bar_y(drink.bar_index) + 25
        x = int(drink.x)

        # Glass
        glass_rect = pygame.Rect(x, y, 20, 25)
        pygame.draw.rect(self.screen, (200, 200, 255), glass_rect, 2)

        # Liquid
        liquid_rect = pygame.Rect(x + 2, y + 10, 16, 13)
        pygame.draw.rect(self.screen, self.drink_color, liquid_rect)

        # Foam
        foam_rect = pygame.Rect(x + 1, y + 5, 18, 6)
        pygame.draw.rect(self.screen, (255, 255, 255), foam_rect)

    def draw_empty_mug(self, state: GameState, mug) -> None:
        """Draw an empty mug."""
        y = state.get_bar_y(mug.bar_index) + 30
        x = int(mug.x)

        # Mug body
        mug_rect = pygame.Rect(x, y, 20, 18)
        pygame.draw.rect(self.screen, self.mug_color, mug_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), mug_rect, 2)

        # Handle
        handle_rect = pygame.Rect(x - 5, y + 2, 6, 14)
        pygame.draw.rect(self.screen, self.mug_color, handle_rect, 2)

    def draw_ui(self, state: GameState) -> None:
        """Draw UI elements."""
        # Score
        score_text = self.font.render(f"Score: {state.score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))

        # Current bar indicator
        bar_text = self.small_font.render(f"Bar: {state.bartender_bar + 1}/{state.num_bars}", True, self.text_color)
        self.screen.blit(bar_text, (10, 45))

        # Instructions
        if state.score == 0 and not state.game_over:
            inst_y = self.height - 80
            instructions = [
                "UP/DOWN: Change bar",
                "LEFT/RIGHT: Move along bar",
                "SPACE: Pour & throw drink",
                "ESC: Quit"
            ]
            for i, inst in enumerate(instructions):
                inst_text = self.small_font.render(inst, True, (150, 150, 170))
                self.screen.blit(inst_text, (self.width // 2 - inst_text.get_width() // 2, inst_y + i * 20))

    def draw_game_over(self, state: GameState) -> None:
        """Draw game over screen."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        go_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
        self.screen.blit(go_text, (self.width // 2 - go_text.get_width() // 2, 200))

        # Reason
        reason_text = self.font.render(state.game_over_reason, True, self.text_color)
        self.screen.blit(reason_text, (self.width // 2 - reason_text.get_width() // 2, 260))

        # Final score
        score_text = self.font.render(f"Final Score: {state.score}", True, self.drink_color)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 310))

        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, (180, 180, 180))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, 360))

    def render(self, state: GameState) -> None:
        """Render the complete game."""
        self.clear()

        # Draw all bars
        for i in range(state.num_bars):
            self.draw_bar(state, i)

        # Draw customers
        for customer in state.customers:
            self.draw_customer(state, customer)

        # Draw drinks
        for drink in state.drinks:
            if drink.active:
                self.draw_drink(state, drink)

        # Draw empty mugs
        for mug in state.empty_mugs:
            if mug.active:
                self.draw_empty_mug(state, mug)

        # Draw bartender
        self.draw_bartender(state)

        # Draw UI
        self.draw_ui(state)

        # Draw game over if needed
        if state.game_over:
            self.draw_game_over(state)

        pygame.display.flip()


def main():
    """Main game loop."""
    pygame.init()

    renderer = Renderer()
    state = GameState()
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif not state.game_over:
                    if event.key == pygame.K_UP:
                        state.move_bartender_up()
                    elif event.key == pygame.K_DOWN:
                        state.move_bartender_down()
                    elif event.key == pygame.K_SPACE:
                        state.throw_drink()
                    elif event.key == pygame.K_LEFT:
                        state.start_move_left()
                    elif event.key == pygame.K_RIGHT:
                        state.start_move_right()

                else:  # Game over
                    if event.key == pygame.K_r:
                        state.reset()

            elif event.type == pygame.KEYUP:
                if not state.game_over:
                    if event.key == pygame.K_LEFT:
                        state.stop_move_left()
                    elif event.key == pygame.K_RIGHT:
                        state.stop_move_right()

        # Update
        state.update(dt)

        # Render
        renderer.render(state)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
