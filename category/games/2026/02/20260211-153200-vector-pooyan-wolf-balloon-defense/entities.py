"""Game entities: Player, Wolf, Arrow."""

import pygame
from config import *


class Player:
    """Player-controlled piglet in a gondola."""

    def __init__(self):
        self.x = PLAYER_X
        self.y = SCREEN_HEIGHT // 2
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.moving_up = False
        self.moving_down = False

    def update(self):
        """Update player position based on input."""
        if self.moving_up:
            self.y -= self.speed
        if self.moving_down:
            self.y += self.speed

        # Clamp position
        self.y = max(PLAYER_MIN_Y, min(PLAYER_MAX_Y, self.y))

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def get_center_y(self):
        """Get center Y position for arrow spawn."""
        return self.y

    def draw(self, screen):
        """Draw the piglet gondola."""
        # Gondola (basket)
        basket_rect = pygame.Rect(
            self.x - 15,
            self.y + 5,
            30,
            20
        )
        pygame.draw.rect(screen, (139, 90, 43), basket_rect)
        pygame.draw.rect(screen, (101, 67, 33), basket_rect, 2)

        # Balloon
        pygame.draw.ellipse(screen, PLAYER_COLOR, (
            self.x - 20,
            self.y - 25,
            40,
            30
        ))
        pygame.draw.ellipse(screen, (255, 150, 150), (
            self.x - 20,
            self.y - 25,
            40,
            30
        ), 2)

        # Ropes connecting balloon to basket
        pygame.draw.line(screen, STRING_COLOR, (self.x - 15, self.y), (self.x - 12, self.y + 5), 2)
        pygame.draw.line(screen, STRING_COLOR, (self.x + 15, self.y), (self.x + 12, self.y + 5), 2)

        # Piglet face
        pygame.draw.circle(screen, (255, 200, 200), (int(self.x), int(self.y - 8)), 8)
        # Ears
        pygame.draw.ellipse(screen, (255, 200, 200), (self.x - 12, self.y - 18, 8, 10))
        pygame.draw.ellipse(screen, (255, 200, 200), (self.x + 4, self.y - 18, 8, 10))
        # Snout
        pygame.draw.ellipse(screen, (255, 180, 180), (self.x - 5, self.y - 5, 10, 8))
        # Eyes
        pygame.draw.circle(screen, BLACK, (int(self.x - 3), int(self.y - 10)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 3), int(self.y - 10)), 2)
        # Nostrils
        pygame.draw.circle(screen, BLACK, (int(self.x - 2), int(self.y - 2)), 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + 2), int(self.y - 2)), 1)


class Arrow:
    """Projectile fired by the player."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ARROW_WIDTH
        self.height = ARROW_HEIGHT
        self.speed = ARROW_SPEED
        self.active = True

    def update(self):
        """Update arrow position."""
        self.x -= self.speed
        if self.x < -self.width:
            self.active = False

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def draw(self, screen):
        """Draw the arrow."""
        # Shaft
        shaft_end = self.x + self.width // 2
        pygame.draw.line(screen, ARROW_COLOR, (self.x - self.width // 2, self.y), (shaft_end, self.y), 3)

        # Arrowhead
        head_size = 8
        pygame.draw.polygon(screen, ARROW_COLOR, [
            (self.x - self.width // 2, self.y),
            (self.x - self.width // 2 + head_size, self.y - head_size // 2),
            (self.x - self.width // 2 + head_size, self.y + head_size // 2)
        ])

        # Fletching (feathers)
        fletch_x = self.x + self.width // 2 - 5
        pygame.draw.polygon(screen, (200, 200, 200), [
            (fletch_x, self.y),
            (fletch_x + 5, self.y - 4),
            (fletch_x + 3, self.y),
            (fletch_x + 5, self.y + 4)
        ])


class Wolf:
    """Enemy wolf floating upward with balloons."""

    def __init__(self, shielded=False):
        self.x = WOLF_START_X
        self.y = SCREEN_HEIGHT + 50
        self.width = WOLF_WIDTH
        self.height = WOLF_HEIGHT
        self.speed = WOLF_SPEED
        self.shielded = shielded
        self.balloons_popped = 0
        self.required_hits = 2 if shielded else 1
        self.active = True
        self.reached_ledge = False

    def update(self):
        """Update wolf position."""
        if not self.reached_ledge:
            self.y -= self.speed
            if self.y <= LEDGE_Y + 20:
                self.reached_ledge = True
                self.active = False

    def get_rect(self):
        """Get collision rectangle for the wolf body."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y,
            self.width,
            self.height
        )

    def get_balloon_rects(self):
        """Get collision rectangles for balloons."""
        balloons = []
        for i in range(self.required_hits):
            balloon_x = self.x - 10 + (i * 20)
            balloon_y = self.y - 30
            balloons.append(pygame.Rect(
                balloon_x - BALLOON_RADIUS,
                balloon_y - BALLOON_RADIUS,
                BALLOON_RADIUS * 2,
                BALLOON_RADIUS * 2
            ))
        return balloons

    def hit(self):
        """Handle balloon hit."""
        self.balloons_popped += 1
        if self.balloons_popped >= self.required_hits:
            self.active = False
            return True
        return False

    def draw(self, screen):
        """Draw the wolf with balloons."""
        # Draw balloons
        for i in range(self.required_hits - self.balloons_popped):
            balloon_x = self.x - 10 + (i * 20)
            balloon_y = self.y - 30

            color = SHIELD_BALLOON_COLOR if self.shielded and i == 0 else BALLOON_COLOR

            # Balloon
            pygame.draw.circle(screen, color, (int(balloon_x), int(balloon_y)), BALLOON_RADIUS)
            pygame.draw.circle(screen, (color[0] - 30, color[1] - 30, color[2] - 30),
                             (int(balloon_x - 4), int(balloon_y - 4)), 5)

            # String
            pygame.draw.line(screen, STRING_COLOR,
                           (balloon_x, balloon_y + BALLOON_RADIUS),
                           (balloon_x, self.y), 1)

        # Wolf body
        body_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y,
            self.width,
            self.height - 10
        )
        pygame.draw.ellipse(screen, WOLF_COLOR, body_rect)

        # Wolf head
        pygame.draw.circle(screen, WOLF_COLOR, (int(self.x), int(self.y - 5)), 12)

        # Ears
        pygame.draw.polygon(screen, WOLF_COLOR, [
            (self.x - 10, self.y - 10),
            (self.x - 15, self.y - 25),
            (self.x - 5, self.y - 15)
        ])
        pygame.draw.polygon(screen, WOLF_COLOR, [
            (self.x + 10, self.y - 10),
            (self.x + 15, self.y - 25),
            (self.x + 5, self.y - 15)
        ])

        # Eyes
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x - 4), int(self.y - 8)), 3)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 4), int(self.y - 8)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x - 4), int(self.y - 8)), 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + 4), int(self.y - 8)), 1)

        # Snout
        pygame.draw.ellipse(screen, (100, 100, 100), (self.x - 5, self.y - 3, 10, 8))
        pygame.draw.circle(screen, BLACK, (int(self.x - 2), int(self.y)), 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + 2), int(self.y)), 1)

    def is_shielded(self):
        """Check if wolf still has shield."""
        return self.shielded and self.balloons_popped == 0
