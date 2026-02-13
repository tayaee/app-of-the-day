"""Main game logic for Rhythm Pulse Beat."""

import pygame
import sys
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    COLOR_BG,
    COLOR_TARGET_ZONE,
    COLOR_PERFECT,
    COLOR_GOOD,
    COLOR_MISS,
    COLOR_TEXT,
    BPM_BASE,
    BPM_MIN,
    BPM_MAX,
    TARGET_RADIUS,
    PERFECT_WINDOW,
    GOOD_WINDOW,
    MISS_THRESHOLD,
    SCORE_PERFECT,
    SCORE_GOOD,
    LIVES,
    BEATS_PER_LEVEL,
    BPM_INCREASE_PER_LEVEL,
    COMBO_MULTIPLIER,
    MAX_COMBO_MULTIPLIER,
)
from entities import Pulse, TargetZone, HitEffect, FloatingText


class Game:
    """Main game class for Rhythm Pulse Beat."""

    def __init__(self, headless=False):
        """Initialize game state."""
        pygame.init()

        self.headless = headless
        if not headless:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Rhythm Pulse Beat")
            self.clock = pygame.time.Clock()
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2

        self.reset_game()

    def reset_game(self):
        """Reset game to initial state."""
        self.state = 'menu'  # menu, playing, gameover
        self.score = 0
        self.lives = LIVES
        self.combo = 0
        self.level = 1
        self.bpm = BPM_BASE
        self.beat_count = 0
        self.beats_hit_in_level = 0

        self.target_zone = TargetZone(self.center_x, self.center_y, TARGET_RADIUS)
        self.pulses = []
        self.effects = []
        self.floating_texts = []

        self.beat_timer = 0
        self.beat_interval = 60 / self.bpm

        # For AI agent input
        self.last_input_action = None
        self.game_over_reason = None

    def get_state(self):
        """Get current game state for AI agents."""
        active_pulse = self.pulses[0] if self.pulses else None

        state = {
            'screen': (WINDOW_WIDTH, WINDOW_HEIGHT),
            'center': (self.center_x, self.center_y),
            'target_radius': TARGET_RADIUS,
            'score': self.score,
            'lives': self.lives,
            'combo': self.combo,
            'level': self.level,
            'bpm': self.bpm,
            'state': self.state,
            'beat_timer': self.beat_timer,
            'beat_interval': self.beat_interval,
        }

        if active_pulse:
            state['active_pulse'] = {
                'radius': active_pulse.radius,
                'distance_to_target': abs(active_pulse.radius - TARGET_RADIUS),
            }

        return state

    def handle_input(self, action):
        """Handle input action (for AI agents)."""
        if action == 'hit':
            self.try_hit_pulse()

    def try_hit_pulse(self):
        """Try to hit the active pulse."""
        if not self.pulses:
            return

        pulse = self.pulses[0]
        if pulse.hit:
            return

        distance = abs(pulse.radius - TARGET_RADIUS)

        if distance <= PERFECT_WINDOW:
            quality = 'perfect'
            points = SCORE_PERFECT
            self.combo += 1
            self.beats_hit_in_level += 1
        elif distance <= GOOD_WINDOW:
            quality = 'good'
            points = SCORE_GOOD
            self.combo += 1
            self.beats_hit_in_level += 1
        elif distance <= MISS_THRESHOLD:
            quality = 'miss'
            points = SCORE_MISS
            self.combo = 0
            self.lives -= 1
        else:
            # Too early or late, count as miss
            quality = 'miss'
            points = SCORE_MISS
            self.combo = 0
            self.lives -= 1

        pulse.hit = True
        pulse.hit_quality = quality

        # Apply combo multiplier
        multiplier = min(COMBO_MULTIPLIER ** self.combo, MAX_COMBO_MULTIPLIER)
        final_points = int(points * multiplier)
        self.score += final_points

        # Create visual effects
        if not self.headless:
            effect_x = self.center_x + (pulse.radius - TARGET_RADIUS) * 0.7
            if quality in ('perfect', 'good'):
                self.effects.append(HitEffect(effect_x, self.center_y, quality))

            color = COLOR_PERFECT if quality == 'perfect' else (
                COLOR_GOOD if quality == 'good' else COLOR_MISS
            )
            text = quality.upper() if quality != 'miss' else 'MISS'
            self.floating_texts.append(
                FloatingText(effect_x, self.center_y - 50, text, color)
            )

        # Check game over
        if self.lives <= 0:
            self.state = 'gameover'
            self.game_over_reason = 'no_lives'

    def spawn_pulse(self):
        """Spawn a new pulse at the center."""
        self.pulses.append(Pulse(self.center_x, self.center_y))
        self.beat_count += 1

    def update(self, dt):
        """Update game state."""
        if self.state != 'playing':
            return

        self.target_zone.update(dt)

        # Update beat timer
        self.beat_timer -= dt

        # Spawn new pulse on beat
        if self.beat_timer <= 0:
            self.spawn_pulse()
            self.beat_timer = self.beat_interval

        # Update pulses
        for pulse in self.pulses:
            pulse.update(dt)

        # Remove missed pulses
        for pulse in self.pulses[:]:
            if pulse.is_out_of_bounds(TARGET_RADIUS) and not pulse.hit:
                pulse.hit = True
                pulse.hit_quality = 'miss'
                self.combo = 0
                self.lives -= 1
                if not self.headless:
                    self.floating_texts.append(
                        FloatingText(self.center_x, self.center_y - 50, 'MISS', COLOR_MISS)
                    )
                if self.lives <= 0:
                    self.state = 'gameover'
                    self.game_over_reason = 'no_lives'

        # Clean up old pulses
        self.pulses = [p for p in self.pulses if not (
            p.hit and p.radius > TARGET_RADIUS + 100
        )]

        # Update effects
        for effect in self.effects:
            effect.update(dt)
        self.effects = [e for e in self.effects if e.is_alive()]

        # Update floating texts
        for text in self.floating_texts:
            text.update(dt)
        self.floating_texts = [t for t in self.floating_texts if t.is_alive()]

        # Check level progression
        if self.beats_hit_in_level >= BEATS_PER_LEVEL:
            self.level += 1
            self.beats_hit_in_level = 0
            self.bpm = min(self.bpm + BPM_INCREASE_PER_LEVEL, BPM_MAX)
            self.beat_interval = 60 / self.bpm

    def draw(self):
        """Draw the game."""
        if self.headless:
            return

        self.screen.fill(COLOR_BG)

        if self.state == 'menu':
            self._draw_menu()
        elif self.state == 'playing':
            self._draw_game()
        elif self.state == 'gameover':
            self._draw_gameover()

        pygame.display.flip()

    def _draw_menu(self):
        """Draw menu screen."""
        title = self.font_large.render("RHYTHM PULSE BEAT", True, COLOR_TEXT)
        subtitle = self.font_medium.render("Press SPACE to Start", True, COLOR_TEXT)
        instructions = self.font_small.render("Press SPACE when pulse hits the target zone", True, COLOR_TEXT)

        self.screen.blit(title, (self.center_x - title.get_width() // 2, 150))
        self.screen.blit(subtitle, (self.center_x - subtitle.get_width() // 2, 300))
        self.screen.blit(instructions, (self.center_x - instructions.get_width() // 2, 400))

    def _draw_game(self):
        """Draw game screen."""
        # Draw target zone
        self.target_zone.draw(self.screen)

        # Draw target circle
        pygame.draw.circle(
            self.screen,
            COLOR_TARGET_ZONE,
            (self.center_x, self.center_y),
            TARGET_RADIUS,
            2
        )

        # Draw perfect/good zone indicators
        pygame.draw.circle(
            self.screen,
            COLOR_PERFECT,
            (self.center_x, self.center_y),
            TARGET_RADIUS + PERFECT_WINDOW,
            1
        )
        pygame.draw.circle(
            self.screen,
            COLOR_GOOD,
            (self.center_x, self.center_y),
            TARGET_RADIUS + GOOD_WINDOW,
            1
        )

        # Draw pulses
        for pulse in self.pulses:
            pulse.draw(self.screen)

        # Draw effects
        for effect in self.effects:
            effect.draw(self.screen)

        # Draw floating texts
        for text in self.floating_texts:
            text.draw(self.screen, self.font_small)

        # Draw UI
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
        lives_text = self.font_medium.render(f"Lives: {'♥' * self.lives}", True, COLOR_MISS)
        combo_text = self.font_small.render(f"Combo: {self.combo}x", True, COLOR_PERFECT)
        level_text = self.font_small.render(f"Level: {self.level} | BPM: {self.bpm}", True, COLOR_TEXT)

        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (WINDOW_WIDTH - 150, 20))
        self.screen.blit(combo_text, (20, 60))
        self.screen.blit(level_text, (WINDOW_WIDTH - 200, 60))

    def _draw_gameover(self):
        """Draw game over screen."""
        self._draw_game()

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        gameover_text = self.font_large.render("GAME OVER", True, COLOR_MISS)
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        level_text = self.font_medium.render(f"Level Reached: {self.level}", True, COLOR_TEXT)
        restart_text = self.font_medium.render("Press SPACE to Restart", True, COLOR_TEXT)
        quit_text = self.font_small.render("Press ESC to Quit", True, COLOR_TEXT)

        self.screen.blit(gameover_text, (self.center_x - gameover_text.get_width() // 2, 150))
        self.screen.blit(score_text, (self.center_x - score_text.get_width() // 2, 250))
        self.screen.blit(level_text, (self.center_x - level_text.get_width() // 2, 300))
        self.screen.blit(restart_text, (self.center_x - restart_text.get_width() // 2, 400))
        self.screen.blit(quit_text, (self.center_x - quit_text.get_width() // 2, 450))

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_SPACE:
                        if self.state == 'menu':
                            self.state = 'playing'
                        elif self.state == 'gameover':
                            self.reset_game()
                            self.state = 'playing'
                        elif self.state == 'playing':
                            self.try_hit_pulse()

            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
