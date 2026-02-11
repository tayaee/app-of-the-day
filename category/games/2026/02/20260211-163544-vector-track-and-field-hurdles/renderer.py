"""
Vector graphics rendering for Track and Field Hurdles.
"""

import pygame
import math
from game_state import State, GameState
from hurdles import Hurdles


class Colors:
    SKY = (20, 20, 40)
    TRACK = (60, 60, 70)
    TRACK_LINES = (100, 100, 110)
    GRASS = (30, 50, 30)

    TEXT = (255, 255, 255)
    TEXT_SHADOW = (0, 0, 0)
    WARNING = (255, 100, 100)

    ATHLETE = (255, 255, 255)
    ATHLETE_ACCENT = (0, 200, 255)

    HURDLE = (255, 200, 0)
    HURDLE_BAR = (255, 100, 0)
    FINISH = (255, 255, 255)


class Renderer:
    """Handles all drawing operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Layout constants
        self.track_y = self.height - 120
        self.track_height = 80
        self.ground_y = self.track_y + self.track_height

        # Scrolling offset
        self.camera_x = 0

    def update_camera(self, state: State):
        """Update camera position to follow athlete."""
        target_x = state.distance * 0.7 - self.width * 0.3
        self.camera_x = max(0, target_x)

    def world_to_screen(self, world_x: float) -> float:
        """Convert world coordinates to screen coordinates."""
        return world_x * 0.7 - self.camera_x

    def draw_background(self, state: State):
        """Draw the track environment."""
        self.screen.fill(Colors.SKY)

        # Parallax background lines
        for i in range(0, 2000, 100):
            screen_x = i - self.camera_x * 0.1
            if -10 < screen_x < self.width + 10:
                pygame.draw.line(self.screen, (30, 30, 50),
                               (screen_x, 0), (screen_x, self.track_y), 1)

        # Ground
        pygame.draw.rect(self.screen, Colors.GRASS,
                        (0, self.ground_y, self.width, self.height - self.ground_y))

        # Track
        pygame.draw.rect(self.screen, Colors.TRACK,
                        (0, self.track_y, self.width, self.track_height))

        # Track lane lines
        for i in range(-10, 100):
            world_x = i * 50
            screen_x = self.world_to_screen(world_x)
            if -10 < screen_x < self.width + 10:
                pygame.draw.line(self.screen, Colors.TRACK_LINES,
                               (screen_x, self.track_y),
                               (screen_x, self.ground_y), 1)

        # Distance markers
        for i in range(0, int(state.TARGET_DISTANCE) + 1, 100):
            screen_x = self.world_to_screen(i)
            if 0 < screen_x < self.width:
                marker_text = self.font_small.render(f"{i}m", True, Colors.TRACK_LINES)
                self.screen.blit(marker_text, (screen_x - 15, self.track_y - 20))

    def draw_finish_line(self, state: State):
        """Draw the finish line."""
        screen_x = self.world_to_screen(state.TARGET_DISTANCE)
        if -20 < screen_x < self.width + 20:
            # Checkered pattern
            square_size = 10
            for i in range(0, self.track_height, square_size):
                color = Colors.FINISH if (i // square_size) % 2 == 0 else (0, 0, 0)
                pygame.draw.rect(self.screen, color,
                               (screen_x - 5, self.track_y + i, 10, square_size))

    def draw_hurdles(self, state: State, hurdles: Hurdles):
        """Draw all hurdles."""
        for hurdle_pos in hurdles.positions:
            screen_x = self.world_to_screen(hurdle_pos)

            if -30 < screen_x < self.width + 30:
                # Skip cleared hurdles
                if hurdle_pos in hurdles.cleared:
                    continue

                hurdle_height = 50
                base_y = self.track_y + self.track_height - 5

                # Hurdle posts
                pygame.draw.line(self.screen, Colors.HURDLE,
                               (screen_x - 8, base_y),
                               (screen_x - 8, base_y - hurdle_height), 3)
                pygame.draw.line(self.screen, Colors.HURDLE,
                               (screen_x + 8, base_y),
                               (screen_x + 8, base_y - hurdle_height), 3)

                # Hurdle bar
                pygame.draw.line(self.screen, Colors.HURDLE_BAR,
                               (screen_x - 10, base_y - hurdle_height),
                               (screen_x + 10, base_y - hurdle_height), 4)

    def draw_athlete(self, state: State):
        """Draw the athlete."""
        # Fixed screen position for athlete
        athlete_screen_x = 100
        base_y = self.track_y + self.track_height - 10

        # Jump offset (negative Y is up)
        jump_offset = state.vertical_position

        # Collision shake effect
        shake_x = 0
        if state.is_in_collision():
            shake_x = (pygame.time.get_ticks() % 100) // 25 - 2

        athlete_x = athlete_screen_x + shake_x
        athlete_y = base_y + jump_offset

        # Animation frame
        run_frame = 0
        if state.velocity > 0.5 and not state.is_jumping():
            run_frame = (pygame.time.get_ticks() // (150 - int(state.velocity * 8))) % 2

        # Body dimensions
        head_radius = 10
        body_height = 30
        leg_length = 25

        # Head
        head_y = athlete_y - body_height - leg_length - head_radius
        pygame.draw.circle(self.screen, Colors.ATHLETE,
                          (int(athlete_x), int(head_y)), head_radius)

        # Body
        body_top = (athlete_x, head_y + head_radius)
        body_bottom = (athlete_x, head_y + head_radius + body_height)
        pygame.draw.line(self.screen, Colors.ATHLETE, body_top, body_bottom, 4)

        # Arms
        arm_y = head_y + head_radius + 8
        if state.is_jumping():
            # Arms up when jumping
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, arm_y),
                           (athlete_x - 15, arm_y - 20), 3)
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, arm_y),
                           (athlete_x + 15, arm_y - 20), 3)
        else:
            # Running animation
            arm_angle = 25 if run_frame == 0 else -25
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, arm_y),
                           (athlete_x - 12, arm_y + 15 + arm_angle), 3)
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, arm_y),
                           (athlete_x + 12, arm_y + 15 - arm_angle), 3)

        # Legs
        leg_y = body_bottom[1]
        if state.is_jumping():
            # Legs tucked when jumping
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, leg_y),
                           (athlete_x - 10, leg_y + 10), 3)
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, leg_y),
                           (athlete_x + 10, leg_y + 10), 3)
        else:
            # Running animation
            leg_angle = 20 if run_frame == 0 else -20
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, leg_y),
                           (athlete_x - 8, leg_y + leg_length - leg_angle), 3)
            pygame.draw.line(self.screen, Colors.ATHLETE,
                           (athlete_x, leg_y),
                           (athlete_x + 8, leg_y + leg_length + leg_angle), 3)

        # Accent glow when running fast
        if state.velocity > state.MAX_VELOCITY * 0.8:
            glow_surface = pygame.Surface((50, 80), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surface, (*Colors.ATHLETE_ACCENT, 50),
                              (0, 0, 50, 80))
            self.screen.blit(glow_surface,
                           (athlete_x - 25, head_y - head_radius - 5))

    def draw_ui(self, state: State, hurdles: Hurdles):
        """Draw game UI elements."""
        # Distance progress
        progress = state.distance / state.TARGET_DISTANCE * 100
        dist_text = f"{state.distance:.0f}m / {int(state.TARGET_DISTANCE)}m ({progress:.1f}%)"
        self._draw_text(dist_text, (self.width // 2, 20), self.font_medium)

        # Timer
        time_str = f"Time: {state.time_elapsed:.2f}s"
        self._draw_text(time_str, (self.width // 2, 50), self.font_large)

        # Hurdle stats
        stats_text = f"Cleared: {state.hurdles_cleared}  Hit: {state.hurdles_hit}"
        self._draw_text(stats_text, (self.width - 100, 20), self.font_small)

        # Distance to next hurdle
        next_dist = hurdles.get_distance_to_next_hurdle()
        if next_dist < float('inf'):
            # Warning when close
            if next_dist < 15:
                color = Colors.WARNING
                hurdle_text = f"! HURDLE: {next_dist:.1f}m !"
            else:
                color = Colors.TEXT
                hurdle_text = f"Next hurdle: {next_dist:.1f}m"
            self._draw_text(hurdle_text, (150, self.height - 40),
                          self.font_small, color)

        # Speed indicator
        speed_kmh = state.velocity * 3.6
        speed_text = f"Speed: {speed_kmh:.0f} km/h"
        self._draw_text(speed_text, (self.width - 100, 50), self.font_small)

        # Jump indicator
        if state.is_jumping():
            jump_height = abs(state.vertical_position)
            self._draw_text(f"JUMP ({jump_height:.0f})", (150, 50), self.font_small,
                          Colors.ATHLETE_ACCENT)

        # Collision warning
        if state.is_in_collision():
            self._draw_text("COLLISION! RECOVERING...",
                          (self.width // 2, 100), self.font_medium, Colors.WARNING)

    def draw_menu(self, state: State):
        """Draw start menu."""
        self._draw_text("TRACK & FIELD HURDLES", (self.width // 2, 80),
                       self.font_large)
        self._draw_text("1000 Meter Hurdle Race", (self.width // 2, 130),
                       self.font_medium)

        self._draw_text("Press SPACE to Start", (self.width // 2, 200),
                       self.font_medium)

        self._draw_text("Controls:", (self.width // 2, 260),
                       self.font_small)
        self._draw_text("Alternate LEFT/RIGHT arrows to run", (self.width // 2, 285),
                       self.font_small)
        self._draw_text("Press SPACE to jump over hurdles", (self.width // 2, 310),
                       self.font_small)

        self._draw_text("Tip: Jump when 5-8m from the hurdle!", (self.width // 2, 360),
                       self.font_small, Colors.WARNING)

    def draw_finished(self, state: State):
        """Draw finish screen."""
        self._draw_text("FINISH!", (self.width // 2, 80), self.font_large)

        time_str = f"Time: {state.finish_time:.2f}s"
        self._draw_text(time_str, (self.width // 2, 140), self.font_medium)

        # Hurdle stats
        cleared_text = f"Hurdles Cleared: {state.hurdles_cleared}"
        self._draw_text(cleared_text, (self.width // 2, 180), self.font_medium)

        hit_text = f"Hurdles Hit: {state.hurdles_hit}"
        self._draw_text(hit_text, (self.width // 2, 210), self.font_medium)

        # Score
        score = state.calculate_score()
        score_text = f"Score: {score}"
        self._draw_text(score_text, (self.width // 2, 260), self.font_large)

        self._draw_text("Press SPACE to play again", (self.width // 2, 320),
                       self.font_medium)
        self._draw_text("Press ESC to quit", (self.width // 2, 350), self.font_small)

    def _draw_text(self, text: str, pos: tuple, font, color=None):
        """Draw centered text with shadow."""
        if color is None:
            color = Colors.TEXT

        text_surface = font.render(text, True, color)
        shadow_surface = font.render(text, True, Colors.TEXT_SHADOW)

        rect = text_surface.get_rect(center=pos)
        shadow_rect = shadow_surface.get_rect(center=(pos[0] + 2, pos[1] + 2))

        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, rect)
