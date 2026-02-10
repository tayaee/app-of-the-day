import pygame
import sys
import random
from config import *
from entities import Player, Fireball, Goomba, Koopa, FloatingBlock


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Fireball Target")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.reset_game()

    def reset_game(self):
        self.player = Player(PLAYER_X, PLAYER_Y)
        self.fireballs = []
        self.enemies = []
        self.score = 0
        self.misses = 0
        self.enemies_hit = 0
        self.multi_hit_count = 0
        self.game_over = False
        self.won = False
        self.last_spawn = pygame.time.get_ticks()
        self.spawn_interval = SPAWN_INTERVAL_MIN
        self.difficulty = 1
        self.streak = 0

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_spawn > self.spawn_interval:
            enemy_type = random.choice(['goomba', 'goomba', 'koopa', 'block'])

            if enemy_type == 'goomba':
                self.enemies.append(Goomba(self.difficulty))
            elif enemy_type == 'koopa':
                self.enemies.append(Koopa(self.difficulty))
            else:
                self.enemies.append(FloatingBlock(self.difficulty))

            self.last_spawn = current_time

            # Adjust spawn interval based on score
            base_interval = SPAWN_INTERVAL_MIN + (SPAWN_INTERVAL_MAX - SPAWN_INTERVAL_MIN) * (1 - min(self.score / 3000, 1))
            self.spawn_interval = base_interval + random.randint(-500, 500)

    def check_fireball_collisions(self):
        for fireball in self.fireballs[:]:
            if not fireball.active:
                self.fireballs.remove(fireball)
                continue

            fireball_rect = fireball.get_rect()

            for enemy in self.enemies[:]:
                if not enemy.alive:
                    continue

                enemy_rect = enemy.get_rect()

                if fireball_rect.colliderect(enemy_rect) and not fireball.has_hit(enemy):
                    # Enemy hit
                    enemy.hit()
                    fireball.mark_hit(enemy)
                    self.enemies_hit += 1
                    self.streak += 1

                    # Check for multi-hit (same fireball hitting multiple enemies)
                    if len(fireball.enemies_hit) >= 2:
                        self.multi_hit_count += 1
                        self.score += SCORE_MULTI_HIT
                    else:
                        self.score += SCORE_HIT

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE:
                        self.throw_fireball()

        return True

    def throw_fireball(self):
        if len(self.fireballs) < MAX_FIREBALLS:
            launch_x, launch_y = self.player.get_launch_pos()
            self.fireballs.append(Fireball(launch_x, launch_y))

    def update(self):
        if self.game_over or self.won:
            return

        # Increase difficulty based on score
        self.difficulty = 1 + min(self.score / 1000, 4)

        # Spawn enemies
        self.spawn_enemy()

        # Update fireballs
        for fireball in self.fireballs:
            fireball.update()

        # Update enemies
        for enemy in self.enemies[:]:
            result = enemy.update()

            if result == "missed":
                self.enemies.remove(enemy)
                self.misses += 1
                self.streak = 0

                if self.misses >= MAX_MISSES:
                    self.game_over = True

            # Remove dead enemies after animation
            if not enemy.alive and enemy.hit_animation <= 0:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)

        # Check collisions
        self.check_fireball_collisions()

        # Check win condition
        if self.score >= WIN_SCORE:
            self.won = True

    def draw(self):
        # Draw sky background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw clouds
        for i in range(3):
            cloud_x = (i * 300 + pygame.time.get_ticks() // 50) % (SCREEN_WIDTH + 100) - 50
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cloud_x, 50 + i * 30, 60, 30))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (cloud_x + 20, 45 + i * 30, 50, 25))

        # Draw ground
        pygame.draw.rect(self.screen, GROUND_COLOR, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        # Draw ground pattern
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (100, 60, 30), (i, GROUND_Y), (i + 20, GROUND_Y + 50), 1)

        # Draw platform for player
        pygame.draw.rect(self.screen, PLATFORM_COLOR, (50, GROUND_Y - 5, 120, 5))

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw fireballs
        for fireball in self.fireballs:
            fireball.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, SCORE_COLOR)
        self.screen.blit(score_text, (10, 10))

        target_text = self.small_font.render(f"Target: {WIN_SCORE}", True, TEXT_COLOR)
        self.screen.blit(target_text, (10, 50))

        # Misses indicator
        misses_color = (255, 100, 100) if self.misses >= MAX_MISSES - 1 else TEXT_COLOR
        misses_text = self.small_font.render(f"Misses: {self.misses}/{MAX_MISSES}", True, misses_color)
        self.screen.blit(misses_text, (SCREEN_WIDTH - 120, 10))

        # Fireball count
        fireball_text = self.small_font.render(f"Fireballs: {len(self.fireballs)}/{MAX_FIREBALLS}", True, TEXT_COLOR)
        self.screen.blit(fireball_text, (SCREEN_WIDTH - 140, 35))

        # Streak indicator
        if self.streak > 1:
            streak_text = self.small_font.render(f"Streak: {self.streak}!", True, (255, 100, 100))
            self.screen.blit(streak_text, (SCREEN_WIDTH // 2 - 40, 10))

        # Instructions
        if self.score == 0 and len(self.enemies) == 0:
            inst_text = self.small_font.render("Press SPACE to throw fireballs!", True, TEXT_COLOR)
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 30))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            stats_text = self.small_font.render(
                f"Enemies Hit: {self.enemies_hit} | Multi-Hits: {self.multi_hit_count}",
                True, TEXT_COLOR
            )
            restart_text = self.small_font.render("Press SPACE or R to restart", True, (200, 200, 200))

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 60))

        # Win screen
        if self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            win_text = self.large_font.render("YOU WIN!", True, (255, 215, 0))
            score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            stats_text = self.small_font.render(
                f"Enemies Hit: {self.enemies_hit} | Multi-Hits: {self.multi_hit_count}",
                True, TEXT_COLOR
            )
            restart_text = self.small_font.render("Press SPACE or R to play again", True, (200, 200, 200))

            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
