"""Game state and logic for Vector Rampaging Gorilla City."""

import pygame
import random
from constants import *
from entities import Gorilla, Building, Helicopter, Projectile


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Rampaging Gorilla City")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset all game state."""
        self.gorilla = Gorilla()
        self.buildings = self._generate_buildings()
        self.helicopters = []
        self.projectiles = []
        self.score = 0
        self.game_state = 'playing'  # 'playing', 'lost'
        self.last_helicopter_spawn = 0
        self.buildings_destroyed = 0
        self.total_segments = sum(b.segments for b in self.buildings)
        self.segments_destroyed = 0

    def _generate_buildings(self):
        """Generate procedural city buildings."""
        buildings = []
        x = 50

        for _ in range(BUILDING_COUNT):
            segments = random.randint(3, BUILDING_MAX_HEIGHT // SEGMENT_HEIGHT)
            building = Building(x, BUILDING_WIDTH, segments)
            buildings.append(building)
            x += BUILDING_WIDTH + 20

        return buildings

    def spawn_helicopter(self):
        """Spawn a new helicopter."""
        heli = Helicopter()
        self.helicopters.append(heli)

    def check_collisions(self):
        """Check all collision interactions."""
        gorilla_rect = self.gorilla.get_rect()
        punch_rect = self.gorilla.get_punch_rect()

        # Check punches against buildings
        if punch_rect:
            for building in self.buildings[:]:
                if not building.alive:
                    continue

                build_rect = building.get_rect()
                if punch_rect.colliderect(build_rect):
                    # Determine which segment was hit
                    segment_y = self.gorilla.y + self.gorilla.height // 2
                    segment_idx = building.get_segment_at_height(segment_y)

                    if building.hit_segment(segment_idx):
                        self.score += SCORE_SEGMENT
                        self.segments_destroyed += 1

                        if not building.alive:
                            self.buildings.remove(building)
                            self.buildings_destroyed += 1
                    break

        # Check punches against helicopters
        if punch_rect:
            for heli in self.helicopters[:]:
                if heli.alive and punch_rect.colliderect(heli.get_rect()):
                    heli.take_damage()
                    self.score += SCORE_HELICOPTER
                    self.helicopters.remove(heli)
                    break

        # Check climbing initiation
        if self.gorilla.climbing is None:
            for i, building in enumerate(self.buildings):
                if building.alive and gorilla_rect.colliderect(building.get_rect()):
                    self.gorilla.climbing = i
                    break

        # Check projectiles against gorilla
        for proj in self.projectiles[:]:
            if proj.alive and gorilla_rect.colliderect(proj.get_rect()):
                proj.alive = False
                if self.gorilla.take_damage(PROJECTILE_DAMAGE):
                    self.game_state = 'lost'
                break

        # Remove dead entities
        self.buildings = [b for b in self.buildings if b.alive]
        self.helicopters = [h for h in self.helicopters if h.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]

    def update(self, dt):
        """Update game state."""
        if self.game_state != 'playing':
            return

        # Update gorilla
        self.gorilla.update(self.buildings)

        # Update helicopters
        for heli in self.helicopters:
            heli.update()

            # Helicopter shooting
            if heli.can_shoot():
                proj = heli.shoot(self.gorilla.x + self.gorilla.width // 2,
                                 self.gorilla.y + self.gorilla.height // 2)
                self.projectiles.append(proj)

        # Update projectiles
        for proj in self.projectiles:
            proj.update()

        # Spawn helicopters
        now = pygame.time.get_ticks()
        if now - self.last_helicopter_spawn > HELICOPTER_SPAWN_INTERVAL:
            self.spawn_helicopter()
            self.last_helicopter_spawn = now
            # Decrease spawn interval over time
            global HELICOPTER_SPAWN_INTERVAL
            HELICOPTER_SPAWN_INTERVAL = max(3000, HELICOPTER_SPAWN_INTERVAL - 200)

        # Check collisions
        self.check_collisions()

        # Check win condition (all buildings destroyed)
        if not self.buildings:
            # Regenerate buildings for endless play
            self.buildings = self._generate_buildings()
            self.total_segments = sum(b.segments for b in self.buildings)

    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if self.gorilla.climbing is None:
            if keys[pygame.K_LEFT]:
                self.gorilla.move_left()
            elif keys[pygame.K_RIGHT]:
                self.gorilla.move_right()
            else:
                self.gorilla.stop_horizontal()

        # Climbing
        if keys[pygame.K_UP]:
            if self.gorilla.climbing is not None:
                self.gorilla.climb_up()
            else:
                self.gorilla.stop_climbing()
        elif keys[pygame.K_DOWN]:
            self.gorilla.climb_down()
        else:
            self.gorilla.stop_climbing()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # Jump
                if event.key == pygame.K_UP and self.gorilla.climbing is None:
                    self.gorilla.jump()

                # Punch
                if event.key == pygame.K_SPACE:
                    self.gorilla.punch()

                # Restart
                if self.game_state != 'playing' and event.key == pygame.K_SPACE:
                    self.reset_game()

        return True

    def draw(self):
        """Draw the game."""
        # Background gradient (night sky)
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            r = int(COLOR_BG[0] * (1 - color_factor * 0.5))
            g = int(COLOR_BG[1] * (1 - color_factor * 0.5))
            b = int(COLOR_BG[2] * (1 - color_factor * 0.3))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Draw ground
        pygame.draw.rect(self.screen, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        # Draw buildings
        for building in self.buildings:
            building.draw(self.screen)

        # Draw gorilla
        self.gorilla.draw(self.screen)

        # Draw helicopters
        for heli in self.helicopters:
            heli.draw(self.screen)

        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """Draw the user interface."""
        # Health bar
        pygame.draw.rect(self.screen, COLOR_HEALTH_BG, (10, 10, 200, 20))
        health_width = int(200 * (self.gorilla.health / GORILLA_MAX_HEALTH))
        health_width = max(0, health_width)
        pygame.draw.rect(self.screen, COLOR_HEALTH, (10, 10, health_width, 20))
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 10, 200, 20), 2)

        # Text info
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        building_text = self.font.render(f"Buildings: {self.buildings_destroyed}", True, COLOR_TEXT)

        self.screen.blit(score_text, (10, 40))
        self.screen.blit(building_text, (SCREEN_WIDTH - 200, 10))

        # Controls hint
        hint = self.small_font.render("Arrows: Move/Climb | Space: Punch", True, (150, 150, 150))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 25))

        # Game over screen
        if self.game_state != 'playing':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            msg = "GAME OVER"
            color = (255, 50, 50)

            title = self.font.render(msg, True, color)
            final_score = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart = self.small_font.render("Press SPACE to restart or ESC to quit", True, COLOR_TEXT)

            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
            self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, 250))
            self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 320))

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS)

            running = self.handle_events()

            if self.game_state == 'playing':
                self.handle_input()

            self.update(dt)
            self.draw()

        pygame.quit()
