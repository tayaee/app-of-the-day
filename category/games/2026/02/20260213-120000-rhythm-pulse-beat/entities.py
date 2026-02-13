"""Game entities for Rhythm Pulse Beat."""

import math
import pygame
from config import (
    PULSE_START_RADIUS,
    PULSE_EXPANSION_RATE,
    COLOR_PULSE_CENTER,
    COLOR_PULSE_OUTER,
    COLOR_PERFECT,
    COLOR_GOOD,
    COLOR_MISS,
)


class Pulse:
    """Expanding circle representing the beat."""

    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = PULSE_START_RADIUS
        self.active = True
        self.hit = False
        self.hit_quality = None  # 'perfect', 'good', 'miss'

    def update(self, dt):
        """Update pulse radius."""
        if not self.hit:
            self.radius += PULSE_EXPANSION_RATE * dt

    def draw(self, surface):
        """Draw the pulse circle."""
        if self.hit and self.hit_quality:
            color = COLOR_PERFECT if self.hit_quality == 'perfect' else COLOR_GOOD
            width = 3
        elif self.hit and self.hit_quality == 'miss':
            color = COLOR_MISS
            width = 2
        else:
            alpha = max(0, 255 - int(self.radius * 0.8))
            color = (*COLOR_PULSE_CENTER, alpha)
            width = 4

        if self.radius > 0:
            pygame.draw.circle(
                surface,
                color[:3] if isinstance(color[0], int) else color,
                (int(self.center_x), int(self.center_y)),
                int(self.radius),
                width
            )

    def is_out_of_bounds(self, max_radius):
        """Check if pulse has expanded beyond target zone."""
        return self.radius > max_radius + 50


class TargetZone:
    """Static target zone where pulses should be hit."""

    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.pulse_phase = 0
        self.pulse_speed = 3

    def update(self, dt):
        """Animate target zone."""
        self.pulse_phase += self.pulse_speed * dt

    def draw(self, surface):
        """Draw the target zone with pulsing effect."""
        pulse_offset = math.sin(self.pulse_phase) * 3

        # Outer ring
        pygame.draw.circle(
            surface,
            COLOR_PULSE_OUTER,
            (int(self.center_x), int(self.center_y)),
            int(self.radius + pulse_offset),
            2
        )

        # Inner ring
        pygame.draw.circle(
            surface,
            COLOR_PULSE_OUTER,
            (int(self.center_x), int(self.center_y)),
            int(self.radius * 0.7 + pulse_offset * 0.5),
            1
        )


class HitEffect:
    """Visual effect when a pulse is hit."""

    def __init__(self, x, y, quality):
        self.x = x
        self.y = y
        self.quality = quality
        self.life = 0.5
        self.max_life = 0.5
        self.particles = []

        # Create particles
        particle_count = 12 if quality == 'perfect' else 8
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            speed = 100 if quality == 'perfect' else 60
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': 4 if quality == 'perfect' else 3
            })

    def update(self, dt):
        """Update particles."""
        self.life -= dt
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt

    def draw(self, surface):
        """Draw particles."""
        alpha = int((self.life / self.max_life) * 255)
        if alpha <= 0:
            return

        color = COLOR_PERFECT if self.quality == 'perfect' else COLOR_GOOD

        for p in self.particles:
            size = max(1, int(p['size'] * (self.life / self.max_life)))
            pygame.draw.circle(
                surface,
                (*color, alpha),
                (int(p['x']), int(p['y'])),
                size
            )

    def is_alive(self):
        """Check if effect is still visible."""
        return self.life > 0


class FloatingText:
    """Floating score text."""

    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0
        self.velocity_y = -50

    def update(self, dt):
        """Update floating text."""
        self.life -= dt
        self.y += self.velocity_y * dt

    def draw(self, surface, font):
        """Draw floating text."""
        if self.life <= 0:
            return

        alpha = int(self.life * 255)
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        surface.blit(text_surface, (int(self.x), int(self.y)))

    def is_alive(self):
        """Check if text is still visible."""
        return self.life > 0
