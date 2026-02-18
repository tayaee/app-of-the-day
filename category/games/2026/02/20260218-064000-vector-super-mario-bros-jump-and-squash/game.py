"""Main game loop and rendering logic."""

import pygame
import random
import time
import config
from entities import Player, Enemy


class Game:
    """Main game class handling loop, rendering, and input."""

    def __init__(self):
        """Initialize game."""
        pygame.init()
        pygame.display.set_caption("Vector Super Mario Bros Jump and Squash")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.tiny_font = pygame.font.Font(None, 24)
        self.state = config.STATE_MENU

        self.reset_game()

    def reset_game(self):
        """Reset game to initial state."""
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_rate = config.INITIAL_SPAWN_RATE
        self.start_time = 0
        self.survival_time = 0
        self.enemies_squashed = 0

    def run(self):
        """Run main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == config.KEY_EXIT:
                        running = False
                    elif self.state == config.STATE_MENU:
                        if event.key == config.KEY_JUMP:
                            self.start_game()
                    elif self.state == config.STATE_GAMEOVER:
                        if event.key == config.KEY_JUMP:
                            self.reset_game()
                            self.start_game()

            if self.state == config.STATE_PLAYING:
                self.update()

            self.render()
            self.clock.tick(config.FPS)

        pygame.quit()

    def start_game(self):
        """Start playing."""
        self.state = config.STATE_PLAYING
        self.start_time = time.time()

    def update(self):
        """Update game logic."""
        if self.game_over:
            self.state = config.STATE_GAMEOVER
            return

        # Update survival time
        self.survival_time = time.time() - self.start_time

        # Handle continuous input
        keys = pygame.key.get_pressed()
        if keys[config.KEY_LEFT]:
            self.player.move_left()
        elif keys[config.KEY_RIGHT]:
            self.player.move_right()
        else:
            self.player.stop_horizontal()

        # Update player
        self.player.update()

        # Spawn enemies
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0
            # Decrease spawn rate over time (make game harder)
            self.spawn_rate = max(config.MIN_SPAWN_RATE,
                                 self.spawn_rate - 1)

        # Update enemies
        for enemy in self.enemies[:]:
            if not enemy.update():
                self.enemies.remove(enemy)

        # Check collisions
        self.check_collisions()

        # Update score based on survival
        self.score = self.enemies_squashed * config.POINTS_PER_STOMP + \
                     int(self.survival_time * config.POINTS_PER_SECOND)

    def spawn_enemy(self):
        """Spawn a new enemy from a random side."""
        spawn_side = random.choice(["left", "right"])
        self.enemies.append(Enemy(spawn_side))

    def check_collisions(self):
        """Check player-enemy collisions."""
        player_rect = self.player.rect

        for enemy in self.enemies:
            if enemy.squashed:
                continue

            enemy_rect = enemy.rect

            if player_rect.colliderect(enemy_rect):
                # Check if player is falling and above enemy (stomp)
                player_bottom = self.player.get_bottom_y()
                player_center_x = self.player.center_x
                player_center_y = self.player.center_y

                enemy_top = enemy.top_y
                enemy_center_y = enemy.center_y

                # Stomp condition: player falling, above enemy, landing on top half
                is_falling = self.player.vy > 0
                is_above = player_bottom <= enemy_top + enemy.height * 0.6
                is_horizontal_aligned = abs(player_center_x - enemy.center_x) < enemy.width * 0.7

                if is_falling and is_above and is_horizontal_aligned:
                    # Successful stomp
                    enemy.squash()
                    self.enemies_squashed += 1
                    # Small bounce
                    self.player.vy = config.JUMP_FORCE * 0.5
                else:
                    # Player hit - game over
                    self.game_over = True

    def render(self):
        """Render current frame."""
        self.screen.fill(config.COLOR_BG)

        if self.state == config.STATE_MENU:
            self.render_menu()
        elif self.state == config.STATE_PLAYING or self.state == config.STATE_GAMEOVER:
            self.render_game()

        pygame.display.flip()

    def render_menu(self):
        """Render menu screen."""
        # Title
        title = self.font.render("JUMP AND SQUASH", True, config.COLOR_PLAYER)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Instructions
        lines = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "LEFT/RIGHT - Move",
            "SPACE - Jump",
            "",
            "Jump on enemies to squash them!",
            "Don't let them touch you from the side."
        ]

        for i, line in enumerate(lines):
            color = config.COLOR_TEXT if i == 0 else config.COLOR_UI
            text = self.small_font.render(line, True, color)
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, 280 + i * 30))
            self.screen.blit(text, text_rect)

    def render_game(self):
        """Render game world."""
        # Draw platform
        pygame.draw.rect(self.screen, config.COLOR_PLATFORM,
                       (0, config.PLATFORM_Y, config.SCREEN_WIDTH,
                        config.SCREEN_HEIGHT - config.PLATFORM_Y))

        # Draw enemies
        for enemy in self.enemies:
            if enemy.squashed:
                # Draw squashed enemy (flat)
                squashed_height = enemy.height // 3
                pygame.draw.rect(self.screen, config.COLOR_ENEMY,
                               (enemy.x, enemy.y + enemy.height - squashed_height,
                                enemy.width, squashed_height), border_radius=2)
            else:
                # Draw normal enemy (Goomba-like)
                pygame.draw.ellipse(self.screen, config.COLOR_ENEMY,
                                 (enemy.x, enemy.y, enemy.width, enemy.height))
                # Eyes
                eye_offset = 8 if enemy.vx > 0 else -8
                eye_y = enemy.y + enemy.height // 3
                pygame.draw.circle(self.screen, config.COLOR_ENEMY_EYES,
                                 (int(enemy.x + enemy.width // 2 + eye_offset), int(eye_y)), 4)

        # Draw player (Mario-like)
        pygame.draw.rect(self.screen, config.COLOR_PLAYER,
                       (self.player.x, self.player.y,
                        self.player.width, self.player.height), border_radius=4)

        # Player eyes
        eye_offset = 6 if self.player.facing_right else -6
        eye_y = self.player.y + 8
        pygame.draw.circle(self.screen, config.COLOR_PLAYER_EYES,
                         (int(self.player.x + self.player.width // 2 + eye_offset), int(eye_y)), 5)
        pygame.draw.circle(self.screen, (0, 0, 0),
                         (int(self.player.x + self.player.width // 2 + eye_offset), int(eye_y)), 2)

        # HUD
        score_text = self.small_font.render(f"Score: {self.score}", True, config.COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        stomp_text = self.small_font.render(f"Squashed: {self.enemies_squashed}",
                                           True, config.COLOR_ACCENT)
        self.screen.blit(stomp_text, (10, 45))

        time_text = self.small_font.render(f"Time: {int(self.survival_time)}s", True, config.COLOR_UI)
        self.screen.blit(time_text, (config.SCREEN_WIDTH - 120, 10))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, config.COLOR_PLAYER)
            game_over_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, 230))
            self.screen.blit(game_over_text, game_over_rect)

            final_score = self.small_font.render(f"Final Score: {self.score}",
                                                True, config.COLOR_TEXT)
            score_rect = final_score.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
            self.screen.blit(final_score, score_rect)

            squashed_text = self.small_font.render(f"Enemies Squashed: {self.enemies_squashed}",
                                                 True, config.COLOR_ACCENT)
            squashed_rect = squashed_text.get_rect(center=(config.SCREEN_WIDTH // 2, 340))
            self.screen.blit(squashed_text, squashed_rect)

            restart_text = self.small_font.render("Press SPACE to Restart",
                                                True, config.COLOR_UI)
            restart_rect = restart_text.get_rect(center=(config.SCREEN_WIDTH // 2, 400))
            self.screen.blit(restart_text, restart_rect)

    # AI Interface Methods

    def get_observation(self):
        """Get current game state for AI."""
        return {
            "player_x": self.player.x,
            "player_y": self.player.y,
            "player_vx": self.player.vx,
            "player_vy": self.player.vy,
            "on_ground": self.player.on_ground,
            "enemies": [
                {
                    "x": e.x,
                    "y": e.y,
                    "vx": e.vx,
                    "squashed": e.squashed
                }
                for e in self.enemies if not e.squashed
            ],
            "score": self.score,
            "survival_time": self.survival_time,
            "game_over": self.game_over
        }

    def step_ai(self, action):
        """Execute AI action and return result.

        Args:
            action: 0=Stay, 1=Left, 2=Right, 3=Jump

        Returns:
            (observation, reward, done)
        """
        old_score = self.score
        old_enemies = len(self.enemies)

        # Execute action
        if action == config.ACTION_LEFT:
            self.player.move_left()
        elif action == config.ACTION_RIGHT:
            self.player.move_right()
        elif action == config.ACTION_JUMP:
            self.player.jump()
        # ACTION_STAY does nothing

        # Update
        self.player.update()
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in self.enemies[:]:
            if not enemy.update():
                self.enemies.remove(enemy)

        self.check_collisions()
        self.survival_time = time.time() - self.start_time
        self.score = self.enemies_squashed * config.POINTS_PER_STOMP + \
                     int(self.survival_time * config.POINTS_PER_SECOND)

        # Calculate reward
        reward = self.score - old_score
        if self.game_over:
            reward -= 100
            done = True
        else:
            done = False

        return self.get_observation(), reward, done

    def reset_for_ai(self):
        """Reset game state for AI training."""
        self.reset_game()
        self.start_game()
        return self.get_observation()
