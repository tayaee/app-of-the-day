"""Main game loop and rendering logic."""

import pygame
import config
from entities import GameState, Player, Platform, PowerUp


class Game:
    """Main game class handling loop, rendering, and input."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.display.set_caption("Vector Super Mario Jump")
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
        state.total_reward += config.SURVIVAL_REWARD

        # Handle continuous key input
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
        player_rect = pygame.Rect(state.player.rect)
        player_bottom = state.player.y + config.PLAYER_SIZE

        for platform in state.platforms:
            plat_rect = pygame.Rect(platform.rect)

            # Only land if falling and above platform
            if (state.player.vy > 0 and
                state.player.on_ground == False and
                player_bottom <= platform.y + config.PLATFORM_HEIGHT + state.player.vy + 5):

                if player_rect.colliderect(plat_rect):
                    state.player.y = platform.y - config.PLAYER_SIZE
                    state.player.vy = 0
                    state.player.on_ground = True

                    # Check if this is a new platform
                    platform_center = platform.x + platform.width / 2
                    player_center = state.player.x + config.PLAYER_SIZE / 2
                    if abs(player_center - platform_center) < platform.width / 2 + 20:
                        if platform not in [p for p in getattr(state, '_landed_platforms', [])]:
                            state.score += config.POINTS_PER_PLATFORM
                            state.platforms_landed += 1
                            state.total_reward += config.LANDING_REWARD
                            if not hasattr(state, '_landed_platforms'):
                                state._landed_platforms = []
                            state._landed_platforms.append(platform)

            # Update moving platforms
            platform.update()

        # Check powerup collisions
        for powerup in state.powerups[:]:
            powerup_rect = pygame.Rect(powerup.rect)
            if player_rect.colliderect(powerup_rect):
                state.player.super_jumps_remaining += config.POWERUP_DURATION
                state.powerups.remove(powerup)

        # Update camera (scroll up when player reaches upper portion)
        target_camera = config.SCREEN_HEIGHT * 0.4
        screen_y = state.player.y + state.camera_y
        if screen_y < target_camera:
            state.camera_y += target_camera - screen_y
            height_record = int(-state.camera_y)
            if height_record > state.max_height:
                state.max_height = height_record
                state.total_reward += config.NEW_HEIGHT_REWARD

        # Generate new platforms
        top_platform = min(state.platforms, key=lambda p: p.y)
        if top_platform.y + state.camera_y > 50:
            new_platform = state.generate_platform()
            state.platforms.append(new_platform)

        # Remove off-screen platforms
        state.platforms = [p for p in state.platforms
                          if p.y + state.camera_y < config.SCREEN_HEIGHT + 100]
        state.powerups = [p for p in state.powerups
                         if p.y + state.camera_y < config.SCREEN_HEIGHT + 100]

        # Check death (fall below screen)
        if state.player.y - state.camera_y > config.SCREEN_HEIGHT:
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
        title = self.font.render("VECTOR MARIO JUMP", True, config.COLOR_PLAYER)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Instructions
        lines = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "LEFT/RIGHT - Move",
            "SPACE/UP - Jump"
        ]

        for i, line in enumerate(lines):
            color = config.COLOR_TEXT if i == 0 else config.COLOR_UI
            text = self.small_font.render(line, True, color)
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, 300 + i * 30))
            self.screen.blit(text, text_rect)

    def _render_game(self) -> None:
        """Render the game world."""
        state = self.game_state

        # Draw platforms
        for platform in state.platforms:
            screen_y = platform.y + state.camera_y
            if -config.PLATFORM_HEIGHT <= screen_y <= config.SCREEN_HEIGHT:
                color = config.COLOR_PLATFORM_MOVING if platform.moving else config.COLOR_PLATFORM
                pygame.draw.rect(self.screen, color,
                               (platform.x, screen_y, platform.width, config.PLATFORM_HEIGHT),
                               border_radius=4)
                # Add highlight
                pygame.draw.rect(self.screen, (255, 255, 255),
                               (platform.x + 2, screen_y + 2, platform.width - 4, 3),
                               border_radius=2)

        # Draw powerups
        for powerup in state.powerups:
            screen_y = powerup.y + state.camera_y
            if -config.POWERUP_SIZE <= screen_y <= config.SCREEN_HEIGHT + config.POWERUP_SIZE:
                # Draw mushroom shape
                x, y = powerup.x, screen_y
                size = config.POWERUP_SIZE
                # Cap
                pygame.draw.ellipse(self.screen, config.COLOR_POWERUP,
                                  (x - size//2, y - size//2, size, size * 0.7))
                # Stem
                pygame.draw.rect(self.screen, (240, 230, 200),
                               (x - size//4, y, size//2, size//3))

        # Draw player
        player_screen_y = state.player.y + state.camera_y
        pygame.draw.rect(self.screen, config.COLOR_PLAYER,
                        (state.player.x, player_screen_y, config.PLAYER_SIZE, config.PLAYER_SIZE),
                        border_radius=4)

        # Draw eyes on player
        eye_y = player_screen_y + 6
        eye_offset = 4 if state.player.vx >= 0 else -4
        pygame.draw.circle(self.screen, (255, 255, 255),
                         (int(state.player.x + config.PLAYER_SIZE//2 + eye_offset), int(eye_y)), 3)
        pygame.draw.circle(self.screen, (0, 0, 0),
                         (int(state.player.x + config.PLAYER_SIZE//2 + eye_offset), int(eye_y)), 1)

        # Draw HUD
        score_text = self.font.render(f"Score: {state.score}", True, config.COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        height_text = self.small_font.render(f"Height: {state.max_height}m", True, config.COLOR_UI)
        self.screen.blit(height_text, (10, 50))

        # Super jump indicator
        if state.player.super_jumps_remaining > 0:
            jump_text = self.small_font.render(f"SUPER: {state.player.super_jumps_remaining}",
                                             True, config.COLOR_POWERUP)
            self.screen.blit(jump_text, (10, 75))

        # Game over overlay
        if self.state == config.STATE_GAMEOVER:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, config.COLOR_PLAYER)
            game_over_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
            self.screen.blit(game_over_text, game_over_rect)

            final_score = self.small_font.render(f"Final Score: {state.score}", True, config.COLOR_TEXT)
            score_rect = final_score.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
            self.screen.blit(final_score, score_rect)

            restart_text = self.small_font.render("Press SPACE to Restart", True, config.COLOR_UI)
            restart_rect = restart_text.get_rect(center=(config.SCREEN_WIDTH // 2, 350))
            self.screen.blit(restart_text, restart_rect)

    def get_state(self) -> GameState:
        """Get current game state for external access."""
        return self.game_state
