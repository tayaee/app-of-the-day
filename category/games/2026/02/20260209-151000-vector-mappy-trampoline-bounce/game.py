"""Main game loop and rendering logic."""

import pygame
import config
from entities import GameState, Player, Floor, Enemy, Item, Trampoline


class Game:
    """Main game class handling loop, rendering, and input."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.display.set_caption("Vector Mappy Trampoline Bounce")
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
                    elif self.state == config.STATE_LEVEL_COMPLETE:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._next_level()

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

    def _next_level(self) -> None:
        """Advance to next level."""
        self.state = config.STATE_PLAYING
        self.game_state.next_level()

    def _update(self) -> None:
        """Update game logic."""
        if self.game_state.game_over:
            self.state = config.STATE_GAMEOVER
            return

        if self.game_state.level_complete:
            self.state = config.STATE_LEVEL_COMPLETE
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

        # Floor and trampoline collision
        player_rect = pygame.Rect(state.player.rect)
        player_bottom = state.player.y + config.PLAYER_SIZE

        state.player.on_floor = False
        state.player.on_trampoline = False

        for floor in state.floors:
            floor_rect = pygame.Rect(floor.rect)

            # Check if player is falling onto this floor
            if state.player.vy > 0 and player_bottom <= floor.y + config.FLOOR_HEIGHT + state.player.vy + 5:
                if player_rect.colliderect(floor_rect):
                    # Check if landing on trampoline
                    if floor.trampoline and not floor.trampoline.broken:
                        tramp_half_width = config.TRAMPOLINE_WIDTH / 2
                        if floor.trampoline.x - tramp_half_width <= state.player.x + config.PLAYER_SIZE / 2 <= floor.trampoline.x + tramp_half_width:
                            # Landed on trampoline
                            state.player.y = floor.y - config.PLAYER_SIZE
                            state.player.jump(is_trampoline=True)
                            state.player.on_trampoline = True
                            state.player.current_trampoline = floor.trampoline
                            state.player.consecutive_bounces += 1
                            floor.trampoline.bounce_count += 1

                            # Check if trampoline breaks
                            if floor.trampoline.bounce_count >= config.MAX_BOUNCES:
                                floor.trampoline.broken = True
                                state.total_reward += config.TRAMPOLINE_BREAK_PENALTY
                                state.player.consecutive_bounces = 0
                            continue

                    # Landed on regular floor
                    state.player.y = floor.y - config.PLAYER_SIZE
                    state.player.vy = 0
                    state.player.on_floor = True
                    state.player.consecutive_bounces = 0

        # Update enemies
        for enemy in state.enemies:
            enemy.update()

            # Reverse at screen edges
            if enemy.x <= 0 or enemy.x >= config.SCREEN_WIDTH:
                enemy.reverse()

            # Reverse at floor edges
            if 0 <= enemy.floor_index < len(state.floors):
                floor = state.floors[enemy.floor_index]
                if enemy.x <= floor.x or enemy.x >= floor.x + floor.width:
                    enemy.reverse()

            # Check collision with player (only on floors, not mid-air)
            if state.player.on_floor and not state.player.on_trampoline:
                enemy_rect = pygame.Rect(enemy.rect)
                player_rect = pygame.Rect(state.player.rect)
                if player_rect.colliderect(enemy_rect):
                    state.game_over = True
                    state.total_reward += config.DEATH_PENALTY

        # Check item collection
        for floor in state.floors:
            for item in floor.items[:]:
                if not item.collected:
                    item_rect = pygame.Rect(item.rect)
                    player_rect = pygame.Rect(state.player.rect)
                    if player_rect.colliderect(item_rect):
                        item.collected = True
                        floor.items.remove(item)
                        state.score += config.POINTS_PER_ITEM
                        state.items_collected += 1
                        state.total_reward += config.COLLECT_REWARD

        # Check level complete
        if state.items_collected >= state.total_items:
            state.level_complete = True
            state.score += config.POINTS_PER_LEVEL
            state.total_reward += config.LEVEL_COMPLETE_REWARD

        # Check death (fall below screen)
        if state.player.y > config.SCREEN_HEIGHT:
            state.game_over = True
            state.total_reward += config.DEATH_PENALTY

    def _render(self) -> None:
        """Render the current frame."""
        self.screen.fill(config.COLOR_BG)

        if self.state == config.STATE_MENU:
            self._render_menu()
        elif self.state == config.STATE_PLAYING:
            self._render_game()
        elif self.state == config.STATE_GAMEOVER:
            self._render_game()
            self._render_gameover()
        elif self.state == config.STATE_LEVEL_COMPLETE:
            self._render_game()
            self._render_level_complete()

        pygame.display.flip()

    def _render_menu(self) -> None:
        """Render the menu screen."""
        # Title
        title = self.font.render("MAPPY TRAMPOLINE", True, config.COLOR_PLAYER)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 180))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("Collect all items, avoid cats!", True, config.COLOR_UI)
        sub_rect = subtitle.get_rect(center=(config.SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, sub_rect)

        # Instructions
        lines = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "LEFT/RIGHT - Move",
            "Auto-bounce on trampolines",
            "",
            "Bounce >4x = Trampoline breaks!"
        ]

        for i, line in enumerate(lines):
            color = config.COLOR_TEXT if i == 0 else config.COLOR_UI
            text = self.small_font.render(line, True, color)
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, 280 + i * 30))
            self.screen.blit(text, text_rect)

    def _render_game(self) -> None:
        """Render the game world."""
        state = self.game_state

        # Draw floors
        for floor in state.floors:
            pygame.draw.rect(self.screen, config.COLOR_FLOOR,
                           (floor.x, floor.y, floor.width, config.FLOOR_HEIGHT),
                           border_radius=3)
            # Floor highlight
            pygame.draw.rect(self.screen, (120, 130, 150),
                           (floor.x + 2, floor.y + 2, floor.width - 4, 3),
                           border_radius=2)

        # Draw trampolines
        for floor in state.floors:
            if floor.trampoline:
                tramp = floor.trampoline
                if not tramp.broken:
                    color = tramp.get_color()
                    half_width = config.TRAMPOLINE_WIDTH / 2
                    pygame.draw.rect(self.screen, color,
                                   (tramp.x - half_width, tramp.y - config.TRAMPOLINE_HEIGHT,
                                    config.TRAMPOLINE_WIDTH, config.TRAMPOLINE_HEIGHT),
                                   border_radius=4)
                    # Trampoline bounce indicator
                    bounces_left = config.MAX_BOUNCES - tramp.bounce_count
                    for i in range(bounces_left):
                        offset_x = (i - 1.5) * 8
                        pygame.draw.circle(self.screen, (255, 255, 255),
                                         (int(tramp.x + offset_x), int(tramp.y - 4)), 2)

        # Draw items
        for floor in state.floors:
            for item in floor.items:
                # Draw diamond shape
                x, y = item.x, item.y
                size = config.ITEM_SIZE // 2
                points = [
                    (x, y - size),
                    (x + size, y),
                    (x, y + size),
                    (x - size, y)
                ]
                pygame.draw.polygon(self.screen, config.COLOR_ITEM, points)
                pygame.draw.polygon(self.screen, (200, 255, 220), points, 2)

        # Draw enemies
        for enemy in state.enemies:
            # Draw cat shape (simplified)
            x, y = enemy.x, enemy.y
            size = config.ENEMY_SIZE
            # Body
            pygame.draw.ellipse(self.screen, config.COLOR_ENEMY,
                              (x - size//2, y - size//2, size, size * 0.8))
            # Ears
            pygame.draw.polygon(self.screen, config.COLOR_ENEMY,
                              [(x - size//3, y - size//3), (x - size//2, y - size//1.5), (x - size//6, y - size//2)])
            pygame.draw.polygon(self.screen, config.COLOR_ENEMY,
                              [(x + size//3, y - size//3), (x + size//2, y - size//1.5), (x + size//6, y - size//2)])
            # Eyes
            pygame.draw.circle(self.screen, (255, 255, 255), (int(x - 4), int(y - 2)), 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(x + 4), int(y - 2)), 3)
            pygame.draw.circle(self.screen, (0, 0, 0), (int(x - 4), int(y - 2)), 1)
            pygame.draw.circle(self.screen, (0, 0, 0), (int(x + 4), int(y - 2)), 1)

        # Draw player (mouse)
        pygame.draw.ellipse(self.screen, config.COLOR_PLAYER,
                          (state.player.x, state.player.y,
                           config.PLAYER_SIZE, config.PLAYER_SIZE * 0.85))
        # Ears
        pygame.draw.circle(self.screen, config.COLOR_PLAYER,
                          (int(state.player.x + 4), int(state.player.y)), 5)
        pygame.draw.circle(self.screen, config.COLOR_PLAYER,
                          (int(state.player.x + config.PLAYER_SIZE - 4), int(state.player.y)), 5)
        # Inner ears
        pygame.draw.circle(self.screen, (200, 230, 255),
                          (int(state.player.x + 4), int(state.player.y)), 2)
        pygame.draw.circle(self.screen, (200, 230, 255),
                          (int(state.player.x + config.PLAYER_SIZE - 4), int(state.player.y)), 2)
        # Eyes
        eye_offset = 3 if state.player.vx >= 0 else -3
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (int(state.player.x + config.PLAYER_SIZE//2 + eye_offset), int(state.player.y + 8)), 4)
        pygame.draw.circle(self.screen, (0, 0, 0),
                          (int(state.player.x + config.PLAYER_SIZE//2 + eye_offset), int(state.player.y + 8)), 2)

        # Draw HUD
        score_text = self.font.render(f"Score: {state.score}", True, config.COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        level_text = self.small_font.render(f"Level: {state.level}", True, config.COLOR_UI)
        self.screen.blit(level_text, (10, 50))

        items_text = self.small_font.render(f"Items: {state.items_collected}/{state.total_items}",
                                          True, config.COLOR_ITEM)
        self.screen.blit(items_text, (10, 75))

        # Bounce warning
        if state.player.consecutive_bounces >= config.MAX_BOUNCES - 1:
            warn_text = self.small_font.render("BREAKING!", True, config.COLOR_TRAMPOLINE_DANGER)
            self.screen.blit(warn_text, (10, 100))

    def _render_gameover(self) -> None:
        """Render game over overlay."""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, config.COLOR_ENEMY)
        game_over_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
        self.screen.blit(game_over_text, game_over_rect)

        final_score = self.small_font.render(f"Final Score: {self.game_state.score}",
                                           True, config.COLOR_TEXT)
        score_rect = final_score.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
        self.screen.blit(final_score, score_rect)

        restart_text = self.small_font.render("Press SPACE to Restart", True, config.COLOR_UI)
        restart_rect = restart_text.get_rect(center=(config.SCREEN_WIDTH // 2, 350))
        self.screen.blit(restart_text, restart_rect)

    def _render_level_complete(self) -> None:
        """Render level complete overlay."""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        level_text = self.font.render("LEVEL COMPLETE!", True, config.COLOR_ITEM)
        level_rect = level_text.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
        self.screen.blit(level_text, level_rect)

        bonus_text = self.small_font.render(f"+{config.POINTS_PER_LEVEL} Bonus!",
                                          True, config.COLOR_TEXT)
        bonus_rect = bonus_text.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
        self.screen.blit(bonus_text, bonus_rect)

        continue_text = self.small_font.render("Press SPACE for Next Level", True, config.COLOR_UI)
        continue_rect = continue_text.get_rect(center=(config.SCREEN_WIDTH // 2, 350))
        self.screen.blit(continue_text, continue_rect)

    def get_state(self) -> GameState:
        """Get current game state for external access."""
        return self.game_state
