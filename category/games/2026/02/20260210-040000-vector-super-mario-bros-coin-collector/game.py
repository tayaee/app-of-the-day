"""Main game loop and rendering logic."""

import pygame
import config
from entities import GameState, Player, Platform, Coin


class Game:
    """Main game class handling loop, rendering, and input."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.display.set_caption("Vector Super Mario Bros Coin Collector")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.state = config.STATE_MENU
        self.game_state = GameState()
        self.game_state.reset()

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == config.KEY_EXIT:
                        running = False
                    elif self.state == config.STATE_MENU:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._start_game()
                    elif self.state == config.STATE_GAMEOVER:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._start_game()
                    elif self.state == config.STATE_PLAYING:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self.game_state.player.jump()

            # State-specific updates
            if self.state == config.STATE_PLAYING:
                self._update()

            # Rendering
            self._render()
            self.clock.tick(config.FPS)

        pygame.quit()

    def _start_game(self) -> None:
        """Start a new game."""
        self.state = config.STATE_PLAYING
        self.game_state.reset()

    def _update(self) -> None:
        """Update game logic."""
        if self.game_state.game_over:
            self.state = config.STATE_GAMEOVER
            return

        state = self.game_state
        state.frames_survived += 1

        # Add survival points every second (60 frames)
        if state.frames_survived % 60 == 0:
            state.score += config.POINTS_PER_SECOND
            state.total_reward += config.SURVIVAL_REWARD

        # Handle continuous key input for horizontal movement
        keys = pygame.key.get_pressed()
        if keys[config.KEY_LEFT]:
            state.player.move_left()
        elif keys[config.KEY_RIGHT]:
            state.player.move_right()
        else:
            state.player.stop_horizontal()

        # Update player
        state.player.update()

        # Check platform collisions
        player_rect = pygame.Rect(state.player.get_rect())
        player_bottom = state.player.y + config.PLAYER_SIZE

        for platform in state.platforms:
            plat_rect = pygame.Rect(platform.get_rect())

            # Only land if falling and above platform
            if (state.player.vy > 0 and
                not state.player.on_ground and
                player_bottom <= platform.y + config.PLATFORM_HEIGHT + state.player.vy + 5):

                if player_rect.colliderect(plat_rect):
                    state.player.y = platform.y - config.PLAYER_SIZE
                    state.player.vy = 0
                    state.player.on_ground = True

        # Update coins
        for coin in state.coins[:]:
            coin.update()
            coin_rect = pygame.Rect(coin.get_rect())

            # Check collision with player
            if player_rect.colliderect(coin_rect):
                state.coins.remove(coin)
                state.coins_collected += 1
                state.score += config.POINTS_PER_COIN
                state.total_reward += config.COIN_REWARD
                continue

            # Remove coins that fall off screen
            if coin.y > config.SCREEN_HEIGHT + config.COIN_SIZE:
                state.coins.remove(coin)

        # Spawn new coins
        state.update_coin_spawn()

        # Check death (fall below screen or off sides)
        if (state.player.y > config.SCREEN_HEIGHT or
            state.player.y < -config.PLAYER_SIZE * 2):
            state.game_over = True
            state.total_reward += config.DEATH_PENALTY

    def _render(self) -> None:
        """Render the current frame."""
        self.screen.fill(config.COLOR_BG)

        if self.state == config.STATE_MENU:
            self._render_menu()
        elif self.state == config.STATE_PLAYING or self.state == config.STATE_GAMEOVER:
            self._render_game()

        pygame.display.flip()

    def _render_menu(self) -> None:
        """Render the menu screen."""
        # Title
        title = self.font.render("MARIO COIN COLLECTOR", True, config.COLOR_PLAYER)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 180))
        self.screen.blit(title, title_rect)

        # Instructions
        lines = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "LEFT/RIGHT - Move",
            "SPACE - Jump",
            "",
            "Collect falling coins!",
            "Don't fall off the platforms!"
        ]

        for i, line in enumerate(lines):
            color = config.COLOR_TEXT if i == 0 else config.COLOR_UI
            text = self.small_font.render(line, True, color)
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, 260 + i * 28))
            self.screen.blit(text, text_rect)

    def _render_game(self) -> None:
        """Render the game world."""
        state = self.game_state

        # Draw platforms
        for platform in state.platforms:
            pygame.draw.rect(self.screen, config.COLOR_PLATFORM,
                           (platform.x, platform.y, platform.width, config.PLATFORM_HEIGHT),
                           border_radius=4)
            # Add highlight
            pygame.draw.rect(self.screen, (100, 210, 140),
                           (platform.x + 2, platform.y + 2, platform.width - 4, 4),
                           border_radius=2)

        # Draw coins
        for coin in state.coins:
            # Draw coin as ellipse (simulating rotation)
            scale_x = abs(0.3 + 0.7 * (0.5 + 0.5 * 0.5))
            coin_width = int(config.COIN_SIZE * scale_x)
            coin_rect = pygame.Rect(0, 0, coin_width, config.COIN_SIZE)
            coin_rect.center = (int(coin.x), int(coin.y))
            pygame.draw.ellipse(self.screen, config.COLOR_COIN, coin_rect)
            # Add shine
            shine_rect = pygame.Rect(0, 0, coin_width // 3, config.COIN_SIZE // 3)
            shine_rect.center = (int(coin.x) - 2, int(coin.y) - 2)
            pygame.draw.ellipse(self.screen, (255, 230, 150), shine_rect)

        # Draw player
        pygame.draw.rect(self.screen, config.COLOR_PLAYER,
                        (state.player.x, state.player.y,
                         config.PLAYER_SIZE, config.PLAYER_SIZE),
                        border_radius=4)

        # Draw eyes on player
        eye_y = state.player.y + 8
        eye_offset = 6 if state.player.vx >= 0 else -6
        pygame.draw.circle(self.screen, (255, 255, 255),
                         (int(state.player.x + config.PLAYER_SIZE // 2 + eye_offset), int(eye_y)), 4)
        pygame.draw.circle(self.screen, (0, 0, 0),
                         (int(state.player.x + config.PLAYER_SIZE // 2 + eye_offset), int(eye_y)), 2)

        # Draw HUD
        score_text = self.font.render(f"Score: {state.score}", True, config.COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        coins_text = self.small_font.render(f"Coins: {state.coins_collected}", True, config.COLOR_COIN)
        self.screen.blit(coins_text, (10, 50))

        # Game over overlay
        if self.state == config.STATE_GAMEOVER:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, config.COLOR_GAMEOVER)
            game_over_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
            self.screen.blit(game_over_text, game_over_rect)

            final_score = self.small_font.render(f"Final Score: {state.score}", True, config.COLOR_TEXT)
            score_rect = final_score.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
            self.screen.blit(final_score, score_rect)

            coins_final = self.small_font.render(f"Coins Collected: {state.coins_collected}",
                                               True, config.COLOR_COIN)
            coins_rect = coins_final.get_rect(center=(config.SCREEN_WIDTH // 2, 330))
            self.screen.blit(coins_final, coins_rect)

            restart_text = self.small_font.render("Press SPACE to Restart", True, config.COLOR_UI)
            restart_rect = restart_text.get_rect(center=(config.SCREEN_WIDTH // 2, 390))
            self.screen.blit(restart_text, restart_rect)

    def get_state(self) -> GameState:
        """Get current game state for external access."""
        return self.game_state
