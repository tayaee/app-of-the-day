"""Main game logic for Vector Balloon Fight: Fish Hazard."""

import pygame
import random
from typing import List, Tuple

from config import Color, Game as GameConfig, Scoring, Physics, Fish
from entities import Player, Enemy, Platform, GiantFish


class Game:
    """Main game class managing state, rendering, and input."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Balloon Fight: Fish Hazard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.player = Player(GameConfig.SCREEN_WIDTH // 2, 200)
        self.enemies: List[Enemy] = []
        self.platforms: List[Platform] = self._create_platforms()
        self.fish = GiantFish()

        self.score = 0
        self.wave = 1
        self.game_over = False
        self.game_over_reason = ""
        self.spawn_enemies()

    def _create_platforms(self) -> List[Platform]:
        """Create the level platforms."""
        return [
            Platform(100, 150, 200),
            Platform(500, 220, 200),
            Platform(250, 320, 300),
            Platform(50, 420, 180),
            Platform(550, 400, 200),
        ]

    def spawn_enemies(self) -> None:
        """Spawn enemies for the current wave."""
        self.enemies = []
        count = GameConfig.ENEMY_COUNT + self.wave - 1
        for _ in range(count):
            x = random.randint(100, GameConfig.SCREEN_WIDTH - 100)
            y = random.randint(100, 300)
            self.enemies.append(Enemy(x, y))

    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.player.flap()

        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()

        return True

    def update(self) -> None:
        """Update game state."""
        if self.game_over:
            return

        # Update player
        self.player.update(self.platforms)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.platforms)
            enemy.update_ai(self.player.x, self.player.y, self.platforms)

        # Update fish
        ate_player, _ = self.fish.update(self.player.x, self.player.y)
        if ate_player:
            self._trigger_game_over("eaten by the giant fish!", Scoring.GAME_OVER_FISH)

        # Check player-fish collision during jump
        if self.fish.is_active():
            p_left, p_top, p_right, p_bottom = self.player.get_rect()
            f_left, f_top, f_right, f_bottom = self.fish.get_hazard_rect()
            if (p_right > f_left and p_left < f_right and
                p_bottom > f_top and p_top < f_bottom):
                self._trigger_game_over("eaten by the giant fish!", Scoring.GAME_OVER_FISH)

        # Check collisions with enemies
        self._check_enemy_collisions()

        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]

        # Check wave completion
        if len(self.enemies) == 0:
            self.score += Scoring.WAVE_BONUS
            self.wave += 1
            self.spawn_enemies()

        # Check if player fell into water
        if self.player.y > GameConfig.WATER_LEVEL:
            if self.player.get_alive_balloon_count() == 0:
                self._trigger_game_over("fell into the water!", Scoring.GAME_OVER_FALL)
            else:
                # Respawn player but lose a balloon
                self.player.pop_balloon()
                self.player.x = GameConfig.SCREEN_WIDTH // 2
                self.player.y = 200
                self.player.vx = 0
                self.player.vy = 0
                self.score += Scoring.BALLOON_LOST

        # Survival score
        self.score += Scoring.SURVIVAL_PER_FRAME

        # Check if player lost all balloons
        if self.player.get_alive_balloon_count() == 0 and self.player.y > GameConfig.SCREEN_HEIGHT:
            self._trigger_game_over("fell after losing all balloons!", Scoring.GAME_OVER_FALL)

    def _check_enemy_collisions(self) -> None:
        """Check and handle player-enemy collisions."""
        p_left, p_top, p_right, p_bottom = self.player.get_rect()
        player_center_y = self.player.y

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            e_left, e_top, e_right, e_bottom = enemy.get_rect()
            enemy_center_y = enemy.y

            if (p_right > e_left and p_left < e_right and
                p_bottom > e_top and p_top < e_bottom):

                # Player hitting enemy from above
                if player_center_y < enemy_center_y and self.player.vy > 0:
                    if enemy.pop_balloon():
                        self.score += Scoring.ENEMY_POPPED
                        if enemy.get_alive_balloon_count() == 0:
                            enemy.alive = False
                            self.score += Scoring.ENEMY_POPPED
                else:
                    # Enemy hitting player
                    if self.player.pop_balloon():
                        self.score += Scoring.BALLOON_LOST
                        if self.player.get_alive_balloon_count() == 0:
                            self._trigger_game_over("lost all balloons!", Scoring.GAME_OVER_FALL)

    def _trigger_game_over(self, reason: str, penalty: int) -> None:
        """Trigger game over state."""
        self.game_over = True
        self.game_over_reason = reason
        self.score += penalty

    def draw(self) -> None:
        """Render the game."""
        # Background
        self.screen.fill(Color.BLACK.value)

        # Draw sky gradient (simplified)
        for y in range(GameConfig.WATER_LEVEL):
            color_factor = y / GameConfig.WATER_LEVEL
            color = (
                int(30 * (1 - color_factor)),
                int(30 * (1 - color_factor)),
                int(50 * (1 - color_factor) + 20 * color_factor)
            )
            pygame.draw.line(self.screen, color, (0, y), (GameConfig.SCREEN_WIDTH, y))

        # Draw water
        water_rect = pygame.Rect(0, GameConfig.WATER_LEVEL, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT - GameConfig.WATER_LEVEL)
        pygame.draw.rect(self.screen, Color.WATER.value, water_rect)

        # Water waves effect
        for x in range(0, GameConfig.SCREEN_WIDTH, 40):
            wave_y = GameConfig.WATER_LEVEL + int(5 * pygame.time.get_ticks() / 100 % 3)
            pygame.draw.arc(self.screen, Color.WATER_DEEP.value,
                           (x, wave_y - 5, 40, 10), 0, 3.14, 3)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw fish
        self.fish.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {int(self.score)}", True, Color.WHITE.value)
        wave_text = self.font.render(f"Wave: {self.wave}", True, Color.WHITE.value)
        balloons = self.player.get_alive_balloon_count()
        balloon_text = self.font.render(f"Balloons: {balloons}", True,
                                       Color.RED.value if balloons == 1 else Color.WHITE.value)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(wave_text, (10, 50))
        self.screen.blit(balloon_text, (GameConfig.SCREEN_WIDTH - 150, 10))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, Color.RED.value)
            reason_text = self.font.render(f"You {self.game_over_reason}", True, Color.WHITE.value)
            final_score_text = self.font.render(f"Final Score: {int(self.score)}", True, Color.WHITE.value)
            restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, Color.YELLOW.value)

            self.screen.blit(game_over_text,
                           (GameConfig.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
            self.screen.blit(reason_text,
                           (GameConfig.SCREEN_WIDTH // 2 - reason_text.get_width() // 2, 230))
            self.screen.blit(final_score_text,
                           (GameConfig.SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 280))
            self.screen.blit(restart_text,
                           (GameConfig.SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(GameConfig.FPS)

        pygame.quit()
