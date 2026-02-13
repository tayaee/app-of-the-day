"""Main game loop and state management."""

import pygame
import random
import time
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS


class Target:
    """Represents a clickable target on screen."""

    def __init__(self):
        self.radius = 50
        self.max_radius = 50
        self.x = random.randint(self.max_radius + 10, SCREEN_WIDTH - self.max_radius - 10)
        self.y = random.randint(self.max_radius + 10, SCREEN_HEIGHT - self.max_radius - 10)
        self.shrink_rate = 0.5
        self.creation_time = time.time()
        self.color = COLORS['target']
        self.alive = True

    def update(self):
        """Shrink the target over time."""
        self.radius -= self.shrink_rate
        if self.radius <= 0:
            self.alive = False
            return 'missed'
        return None

    def draw(self, surface):
        """Draw the target on screen."""
        if self.alive and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(surface, COLORS['white'], (int(self.x), int(self.y)), int(self.radius), 2)

    def is_clicked(self, pos):
        """Check if position is within the target."""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


class Game:
    """Main game class."""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Reaction Reflex Test")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        self.score = 0
        self.misses = 0
        self.max_misses = 3
        self.targets = []
        self.spawn_timer = 0
        self.spawn_delay = 120  # frames between spawns
        self.game_over = False
        self.difficulty_multiplier = 1.0

    def spawn_target(self):
        """Create a new target."""
        target = Target()
        target.shrink_rate *= self.difficulty_multiplier
        self.targets.append(target)

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over and event.key == pygame.K_r:
                    self.reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    hit = False
                    best_score = 0
                    targets_to_remove = []

                    for target in self.targets:
                        if target.is_clicked(mouse_pos):
                            hit = True
                            # Score based on how quickly clicked (larger radius = more points)
                            click_score = int(target.radius * 2)
                            if click_score > best_score:
                                best_score = click_score
                            targets_to_remove.append(target)

                    for target in targets_to_remove:
                        self.targets.remove(target)

                    if hit:
                        self.score += best_score
                    else:
                        # Clicking empty space counts as a miss
                        self.misses += 1

        return True

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Spawn new targets
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_target()
            self.spawn_timer = 0

        # Update targets
        targets_to_remove = []
        for target in self.targets:
            result = target.update()
            if result == 'missed':
                targets_to_remove.append(target)
                self.misses += 1

        for target in targets_to_remove:
            self.targets.remove(target)

        # Check game over
        if self.misses >= self.max_misses:
            self.game_over = True

        # Increase difficulty over time
        self.difficulty_multiplier = 1.0 + (self.score / 1000.0)
        self.spawn_delay = max(30, 120 - int(self.score / 50))

    def draw(self):
        """Render the game."""
        self.screen.fill(COLORS['background'])

        # Draw targets
        for target in self.targets:
            target.draw(self.screen)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, COLORS['white'])
        misses_text = self.font.render(f"Misses: {self.misses}/{self.max_misses}", True, COLORS['white'])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(misses_text, (10, 50))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(COLORS['black'])
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, COLORS['white'])
            final_score_text = self.font.render(f"Final Score: {self.score}", True, COLORS['white'])
            restart_text = self.font.render("Press R to restart or ESC to quit", True, COLORS['white'])

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 300))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
