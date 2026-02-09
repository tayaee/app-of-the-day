"""Game entities for Vector Balloon Fight."""

import random
from typing import List, Tuple, Optional
from config import Color, Physics, Game, Entity


class Balloon:
    """Represents a single balloon attached to a character."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.radius = Entity.BALLOON_RADIUS
        self.color = color
        self.alive = True
        # Oscillation for floating effect
        self.wobble_offset = random.random() * 6.28
        self.wobble_speed = 0.1

    def update(self, character_x: float, character_y: float) -> None:
        """Update balloon position following character."""
        if not self.alive:
            return

        # Add slight wobble effect
        self.wobble_offset += self.wobble_speed
        wobble_x = 2 * random.sin(self.wobble_offset)

        target_x = character_x + wobble_x
        target_y = character_y - Entity.BALLOON_OFFSET

        # Smooth follow
        self.x += (target_x - self.x) * 0.3
        self.y += (target_y - self.y) * 0.3

    def draw(self, surface, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw the balloon."""
        if not self.alive:
            return

        import pygame
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x - offset_x), int(self.y - offset_y)),
            self.radius
        )
        # Highlight
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x - offset_x - 5), int(self.y - offset_y - 5)),
            4
        )


class Platform:
    """Represents a platform in the game arena."""

    def __init__(self, x: float, y: float, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = 15

    def draw(self, surface, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw the platform."""
        import pygame
        rect = pygame.Rect(
            self.x - offset_x,
            self.y - offset_y,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, Color.PLATFORM.value, rect)


class Character:
    """Base class for playable characters and enemies."""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int], is_player: bool = False):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.width = Entity.PLAYER_WIDTH
        self.height = Entity.PLAYER_HEIGHT
        self.color = color
        self.is_player = is_player
        self.balloons: List[Balloon] = []
        self.flap_cooldown = 0
        self.alive = True
        self.facing_right = True

        # Create balloons
        for i in range(Game.MAX_BALLOONS):
            offset_x = -8 if i == 0 else 8
            self.balloons.append(Balloon(
                x + offset_x,
                y - Entity.BALLOON_OFFSET,
                color
            ))

    def get_alive_balloon_count(self) -> int:
        """Return number of intact balloons."""
        return sum(1 for b in self.balloons if b.alive)

    def get_top_y(self) -> float:
        """Get the highest point (top of balloons)."""
        if not self.balloons:
            return self.y - 10
        return min(b.y - b.radius for b in self.balloons if b.alive)

    def get_bottom_y(self) -> float:
        """Get the lowest point (bottom of character)."""
        return self.y + self.height / 2

    def flap(self) -> None:
        """Apply flap force to gain altitude."""
        if self.flap_cooldown == 0 and self.get_alive_balloon_count() > 0:
            self.vy = Physics.FLAP_FORCE
            self.flap_cooldown = Physics.FLAP_COOLDOWN

    def move_left(self) -> None:
        """Apply left movement."""
        if self.get_alive_balloon_count() > 0:
            self.vx -= Physics.HORIZONTAL_ACCEL
            self.facing_right = False

    def move_right(self) -> None:
        """Apply right movement."""
        if self.get_alive_balloon_count() > 0:
            self.vx += Physics.HORIZONTAL_ACCEL
            self.facing_right = True

    def pop_balloon(self) -> None:
        """Pop one balloon."""
        for balloon in self.balloons:
            if balloon.alive:
                balloon.alive = False
                break

    def update(self) -> None:
        """Update physics and state."""
        if not self.alive:
            return

        # Update cooldown
        if self.flap_cooldown > 0:
            self.flap_cooldown -= 1

        # Apply gravity (reduced by balloons)
        balloon_factor = self.get_alive_balloon_count() / Game.MAX_BALLOONS
        gravity = Physics.GRAVITY * (1.0 - balloon_factor * 0.5)
        self.vy += gravity

        # Clamp vertical speed
        self.vy = max(-Physics.MAX_FALL_SPEED, min(Physics.MAX_FALL_SPEED, self.vy))

        # Apply friction to horizontal movement
        self.vx *= Physics.HORIZONTAL_FRICTION

        # Clamp horizontal speed
        self.vx = max(-Physics.MAX_HORIZONTAL_SPEED,
                      min(Physics.MAX_HORIZONTAL_SPEED, self.vx))

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Update balloons
        for balloon in self.balloons:
            balloon.update(self.x, self.y)

    def draw(self, surface, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw the character."""
        if not self.alive:
            return

        # Draw balloons first (behind character)
        for balloon in self.balloons:
            balloon.draw(surface, offset_x, offset_y)

        # Draw strings to balloons
        import pygame
        for balloon in self.balloons:
            if balloon.alive:
                pygame.draw.line(
                    surface,
                    Color.GRAY.value,
                    (self.x - offset_x, self.y - offset_y - 5),
                    (balloon.x - offset_x, balloon.y - offset_y + balloon.radius),
                    2
                )

        # Draw character body (simple vector style)
        body_rect = pygame.Rect(
            self.x - self.width // 2 - offset_x,
            self.y - self.height // 2 - offset_y,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.color, body_rect)

        # Draw eyes
        eye_offset = 5 if self.facing_right else -5
        pygame.draw.circle(
            surface,
            Color.WHITE.value,
            (int(self.x + eye_offset - offset_x), int(self.y - 2 - offset_y)),
            4
        )
        pygame.draw.circle(
            surface,
            Color.BLACK.value,
            (int(self.x + eye_offset + (1 if self.facing_right else -1) - offset_x),
             int(self.y - 2 - offset_y)),
            2
        )


class Player(Character):
    """Player-controlled character."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, Color.BLUE.value, is_player=True)


class Enemy(Character):
    """AI-controlled enemy character."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, Color.RED.value, is_player=False)
        self.decision_timer = 0
        self.target_y = y

    def update_ai(self, player_x: float, player_y: float, platforms: List[Platform]) -> None:
        """Simple AI behavior."""
        if not self.alive or self.get_alive_balloon_count() == 0:
            return

        self.decision_timer -= 1

        if self.decision_timer <= 0:
            self.decision_timer = 20 + random.randint(0, 20)

            # Decision making
            dy = player_y - self.y

            # Flap to gain altitude if below player
            if dy < -50 and random.random() < 0.7:
                self.flap()

            # Move towards player
            if player_x < self.x - 50:
                self.move_left()
            elif player_x > self.x + 50:
                self.move_right()

            # Random flapping
            if random.random() < 0.3:
                self.flap()

        # Always try to stay above water
        if self.y > Game.SCREEN_HEIGHT - 150 and self.flap_cooldown == 0:
            self.flap()
