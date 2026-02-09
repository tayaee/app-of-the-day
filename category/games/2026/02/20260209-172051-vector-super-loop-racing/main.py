"""
Vector Super Loop Racing
A high-speed 2D racing game where you maintain momentum through complex loops and sharp turns.
"""

import math
import pygame
import pygame.gfxdraw
from pygame.math import Vector2

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (10, 10, 15)
DARK_GRAY = (30, 30, 40)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 100, 220)
CYAN = (50, 200, 200)
YELLOW = (255, 220, 50)
WHITE = (240, 240, 240)
GRAY = (100, 100, 120)

# Game settings
TRACK_CENTER = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
TRACK_OUTER_RADIUS = 280
TRACK_INNER_RADIUS = 180
TRACK_WIDTH = TRACK_OUTER_RADIUS - TRACK_INNER_RADIUS

MAX_SPEED = 12.0
ACCELERATION = 0.15
BRAKING = 0.25
FRICTION = 0.02
TURN_SPEED = 0.06

WALL_PENALTY = 0.7
BOOST_MULTIPLIER = 1.5
OIL_FRICTION = 0.1

GAME_DURATION = 120  # seconds


class TrackZone:
    """Represents a special zone on the track (booster, oil, etc.)"""
    def __init__(self, angle_start, angle_end, zone_type, radius_offset=0):
        self.angle_start = angle_start
        self.angle_end = angle_end
        self.zone_type = zone_type  # 'booster', 'oil'
        self.radius_offset = radius_offset

    def contains(self, position):
        """Check if a position is within this zone"""
        rel_pos = position - TRACK_CENTER
        distance = rel_pos.length()
        angle = math.atan2(rel_pos.y, rel_pos.x)

        # Normalize angle to [0, 2pi]
        if angle < 0:
            angle += 2 * math.pi

        # Check radius range
        min_radius = TRACK_INNER_RADIUS - 10 + self.radius_offset
        max_radius = TRACK_OUTER_RADIUS + 10 + self.radius_offset

        if distance < min_radius or distance > max_radius:
            return False

        # Check angle range
        if self.angle_start <= self.angle_end:
            return self.angle_start <= angle <= self.angle_end
        else:  # Wraps around 2pi
            return angle >= self.angle_start or angle <= self.angle_end

    def draw(self, surface):
        """Draw the zone on the track"""
        rect = pygame.Rect(
            TRACK_CENTER.x - TRACK_OUTER_RADIUS - 20,
            TRACK_CENTER.y - TRACK_OUTER_RADIUS - 20,
            TRACK_OUTER_RADIUS * 2 + 40,
            TRACK_OUTER_RADIUS * 2 + 40
        )

        start_angle = -self.angle_end
        end_angle = -self.angle_start

        color = GREEN if self.zone_type == 'booster' else CYAN

        # Draw arc segment
        pygame.draw.arc(
            surface,
            color,
            rect,
            start_angle,
            end_angle,
            15
        )


class Car:
    """Player controlled vehicle"""
    def __init__(self):
        self.reset()

    def reset(self):
        angle = -math.pi / 2  # Start at top of track
        mid_radius = (TRACK_INNER_RADIUS + TRACK_OUTER_RADIUS) / 2
        self.position = TRACK_CENTER + Vector2(
            math.cos(angle) * mid_radius,
            math.sin(angle) * mid_radius
        )
        self.velocity = Vector2(0, 0)
        self.heading = 0  # Angle in radians
        self.speed = 0
        self.health = 100
        self.laps = 0
        self.last_checkpoint_angle = -math.pi / 2
        self.distance_traveled = 0

    def update(self, inputs, zones):
        # Handle input
        if inputs['up']:
            self.speed += ACCELERATION
        if inputs['down']:
            self.speed -= BRAKING

        # Apply friction
        if self.speed > 0:
            self.speed -= FRICTION
        elif self.speed < 0:
            self.speed += FRICTION

        # Clamp speed
        self.speed = max(-MAX_SPEED / 2, min(MAX_SPEED, self.speed))

        # Steering (only when moving)
        if abs(self.speed) > 0.5:
            turn_factor = min(1.0, abs(self.speed) / 5)
            if inputs['left']:
                self.heading -= TURN_SPEED * turn_factor
            if inputs['right']:
                self.heading += TURN_SPEED * turn_factor

        # Calculate velocity from heading and speed
        self.velocity = Vector2(
            math.cos(self.heading) * self.speed,
            math.sin(self.heading) * self.speed
        )

        # Apply centrifugal force on turns
        rel_pos = self.position - TRACK_CENTER
        if rel_pos.length() > 0:
            to_center = -rel_pos.normalize()
            # Perpendicular to velocity (tangential direction)
            tangent = Vector2(-self.velocity.y, self.velocity.x)
            if tangent.length() > 0:
                tangent = tangent.normalize()
                # Force outward based on speed
                centrifugal = -tangent * (self.speed * self.speed * 0.01)
                self.velocity += centrifugal

        # Check zones
        for zone in zones:
            if zone.contains(self.position):
                if zone.zone_type == 'booster':
                    self.velocity *= BOOST_MULTIPLIER
                elif zone.zone_type == 'oil':
                    self.velocity *= (1 - OIL_FRICTION)

        # Update position
        new_position = self.position + self.velocity

        # Check track boundaries
        rel_pos = new_position - TRACK_CENTER
        distance = rel_pos.length()

        if distance > TRACK_OUTER_RADIUS or distance < TRACK_INNER_RADIUS:
            # Wall collision
            self.speed *= -WALL_PENALTY
            self.health -= 10
            # Bounce back
            normal = -rel_pos.normalize() if distance > TRACK_OUTER_RADIUS else rel_pos.normalize()
            self.velocity = self.velocity.reflect(normal) * 0.5
            new_position = self.position + self.velocity

        self.position = new_position
        self.distance_traveled += abs(self.speed)

        # Check lap completion
        current_angle = math.atan2(rel_pos.y, rel_pos.x)
        angle_diff = current_angle - self.last_checkpoint_angle

        # Normalize angle diff
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi

        # Crossed start/finish line going forward
        if self.last_checkpoint_angle > math.pi / 2 and current_angle < -math.pi / 2:
            self.laps += 1
            self.health = min(100, self.health + 20)  # Heal on lap

        self.last_checkpoint_angle = current_angle

        # Clamp health
        self.health = max(0, min(100, self.health))

    def draw(self, surface):
        # Draw car as triangle
        size = 15
        tip = self.position + Vector2(math.cos(self.heading), math.sin(self.heading)) * size
        left_angle = self.heading + 2.5
        right_angle = self.heading - 2.5

        left = self.position + Vector2(math.cos(left_angle), math.sin(left_angle)) * size * 0.7
        right = self.position + Vector2(math.cos(right_angle), math.sin(right_angle)) * size * 0.7

        # Color based on health
        health_ratio = self.health / 100
        car_color = (
            int(220 * health_ratio),
            int(220 * health_ratio),
            int(220 * health_ratio)
        )

        pygame.draw.polygon(surface, car_color, [tip, left, right])

        # Draw speed indicator (small line)
        if abs(self.speed) > 0.5:
            end_pos = self.position + self.velocity.normalize() * (size + 5 + abs(self.speed) * 2)
            pygame.draw.line(surface, YELLOW, self.position, end_pos, 2)


class Game:
    """Main game controller"""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vector Super Loop Racing")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        self.car = Car()
        self.game_over = False
        self.time_remaining = GAME_DURATION
        self.score = 0

        # Create track zones
        self.zones = [
            # Boosters on straight sections
            TrackZone(0, 0.5, 'booster'),
            TrackZone(math.pi, math.pi + 0.5, 'booster'),
            # Oil slicks on curves
            TrackZone(1.5, 2.0, 'oil'),
            TrackZone(4.5, 5.0, 'oil'),
        ]

    def get_inputs(self):
        keys = pygame.key.get_pressed()
        return {
            'up': keys[pygame.K_UP] or keys[pygame.K_w],
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s],
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
        }

    def update(self, dt):
        if self.game_over:
            return

        self.time_remaining -= dt

        if self.time_remaining <= 0 or self.car.health <= 0:
            self.game_over = True
            return

        inputs = self.get_inputs()
        self.car.update(inputs, self.zones)

        # Update score
        self.score = int(self.car.distance_traveled + self.car.laps * 1000)

    def draw(self):
        self.screen.fill(BLACK)

        # Draw track
        pygame.draw.circle(
            self.screen,
            DARK_GRAY,
            (int(TRACK_CENTER.x), int(TRACK_CENTER.y)),
            TRACK_OUTER_RADIUS
        )
        pygame.draw.circle(
            self.screen,
            BLACK,
            (int(TRACK_CENTER.x), int(TRACK_CENTER.y)),
            TRACK_INNER_RADIUS
        )

        # Draw track borders
        pygame.draw.circle(
            self.screen,
            RED,
            (int(TRACK_CENTER.x), int(TRACK_CENTER.y)),
            TRACK_OUTER_RADIUS,
            3
        )
        pygame.draw.circle(
            self.screen,
            RED,
            (int(TRACK_CENTER.x), int(TRACK_CENTER.y)),
            TRACK_INNER_RADIUS,
            3
        )

        # Draw zones
        for zone in self.zones:
            zone.draw(self.screen)

        # Draw finish line
        finish_x = TRACK_CENTER.x
        finish_y_start = TRACK_CENTER.y - TRACK_OUTER_RADIUS
        finish_y_end = TRACK_CENTER.y - TRACK_INNER_RADIUS
        pygame.draw.line(self.screen, WHITE, (finish_x, finish_y_start), (finish_x, finish_y_end), 5)

        # Draw checkered pattern at finish
        for i, y in enumerate(range(int(finish_y_start), int(finish_y_end), 10)):
            color = WHITE if i % 2 == 0 else BLACK
            pygame.draw.rect(self.screen, color, (finish_x - 5, y, 10, 10))

        # Draw car
        self.car.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        # Background panel
        panel_rect = pygame.Rect(10, 10, 220, 130)
        s = pygame.Surface((panel_rect.width, panel_rect.height))
        s.set_alpha(180)
        s.fill(DARK_GRAY)
        self.screen.blit(s, panel_rect)

        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        # Laps
        laps_text = self.font.render(f"LAPS: {self.car.laps}", True, WHITE)
        self.screen.blit(laps_text, (20, 50))

        # Time
        time_color = WHITE if self.time_remaining > 30 else RED
        time_text = self.font.render(f"TIME: {int(self.time_remaining)}", True, time_color)
        self.screen.blit(time_text, (20, 80))

        # Health bar
        health_width = 200
        health_height = 15
        health_rect = pygame.Rect(20, 110, health_width, health_height)
        pygame.draw.rect(self.screen, GRAY, health_rect)

        health_ratio = self.car.health / 100
        fill_width = int(health_width * health_ratio)
        fill_color = GREEN if health_ratio > 0.5 else (YELLOW if health_ratio > 0.25 else RED)

        if fill_width > 0:
            fill_rect = pygame.Rect(20, 110, fill_width, health_height)
            pygame.draw.rect(self.screen, fill_color, fill_rect)

        pygame.draw.rect(self.screen, WHITE, health_rect, 2)

    def draw_game_over(self):
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(game_over_text, text_rect)

        # Final score
        score_text = self.font.render(f"FINAL SCORE: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # Laps completed
        laps_text = self.font.render(f"LAPS COMPLETED: {self.car.laps}", True, WHITE)
        laps_rect = laps_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(laps_text, laps_rect)

        # Restart instruction
        restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()

            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
