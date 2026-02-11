"""Game entities for Vector Balloon Fight: Fish Hazard."""

import random
import math
from typing import List, Tuple, Optional
from config import Color, Physics, Game as GameConfig, Entity, Fish as FishConfig


class Balloon:
    """Represents a single balloon attached to a character."""

    def __init__(self, offset_x: float, color: Tuple[int, int, int]):
        self.offset_x = offset_x
        self.offset_y = -Entity.BALLOON_OFFSET
        self.radius = Entity.BALLOON_RADIUS
        self.color = color
        self.alive = True
        self.wobble_offset = random.random() * 6.28
        self.wobble_speed = 0.08

    def update(self) -> None:
        """Update balloon animation."""
        self.wobble_offset += self.wobble_speed

    def get_draw_pos(self, owner_x: float, owner_y: float) -> Tuple[float, float]:
        """Get the draw position with wobble effect."""
        wobble_x = 2 * math.sin(self.wobble_offset)
        return (owner_x + self.offset_x + wobble_x, owner_y + self.offset_y)

    def draw(self, surface, owner_x: float, owner_y: float) -> None:
        """Draw the balloon and its string."""
        if not self.alive:
            return

        import pygame
        bx, by = self.get_draw_pos(owner_x, owner_y)
        bx, by = int(bx), int(by)

        # Draw string
        string_end_y = int(owner_y - 5)
        pygame.draw.line(
            surface,
            Color.GRAY.value,
            (int(owner_x), string_end_y),
            (bx, by + self.radius),
            2
        )

        # Draw balloon
        pygame.draw.circle(surface, self.color, (bx, by), self.radius)
        # Highlight
        pygame.draw.circle(surface, (255, 255, 255), (bx - 4, by - 4), 5)


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
        self.alive = True
        self.facing_right = True
        self.flap_cooldown = 0

        self.balloons: List[Balloon] = []
        for i in range(GameConfig.MAX_BALLOONS):
            offset = -10 if i == 0 else 10
            self.balloons.append(Balloon(offset, color))

    def get_alive_balloon_count(self) -> int:
        """Return number of intact balloons."""
        return sum(1 for b in self.balloons if b.alive)

    def get_rect(self) -> Tuple[float, float, float, float]:
        """Return collision rectangle (left, top, right, bottom)."""
        return (
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.x + self.width / 2,
            self.y + self.height / 2
        )

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

    def pop_balloon(self) -> bool:
        """Pop one balloon. Returns True if a balloon was popped."""
        for balloon in self.balloons:
            if balloon.alive:
                balloon.alive = False
                return True
        return False

    def update(self, platforms: List['Platform']) -> None:
        """Update physics and state."""
        if not self.alive:
            return

        if self.flap_cooldown > 0:
            self.flap_cooldown -= 1

        # Apply balloon lift
        balloon_count = self.get_alive_balloon_count()
        if balloon_count > 0:
            self.vy -= Physics.BALLOON_LIFT * balloon_count

        # Apply gravity
        self.vy += Physics.GRAVITY

        # Clamp speeds
        self.vy = max(-Physics.MAX_FALL_SPEED, min(Physics.MAX_FALL_SPEED, self.vy))
        self.vx *= Physics.HORIZONTAL_FRICTION
        self.vx = max(-Physics.MAX_HORIZONTAL_SPEED, min(Physics.MAX_HORIZONTAL_SPEED, self.vx))

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Update balloon animation
        for balloon in self.balloons:
            balloon.update()

        # Platform collision
        self._handle_platform_collision(platforms)

        # Screen wrap
        if self.x < -20:
            self.x = GameConfig.SCREEN_WIDTH + 20
        elif self.x > GameConfig.SCREEN_WIDTH + 20:
            self.x = -20

    def _handle_platform_collision(self, platforms: List['Platform']) -> None:
        """Handle collision with platforms."""
        left, top, right, bottom = self.get_rect()

        for platform in platforms:
            plat_left, plat_top, plat_right, plat_bottom = platform.get_rect()

            if right > plat_left and left < plat_right and bottom > plat_top and top < plat_bottom:
                # Determine collision side
                overlap_left = right - plat_left
                overlap_right = plat_right - left
                overlap_top = bottom - plat_top
                overlap_bottom = plat_bottom - top

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_top and self.vy > 0:
                    self.y = plat_top - self.height / 2
                    self.vy = 0
                elif min_overlap == overlap_bottom and self.vy < 0:
                    self.y = plat_bottom + self.height / 2
                    self.vy = 0

    def draw(self, surface) -> None:
        """Draw the character."""
        if not self.alive:
            return

        import pygame

        # Draw balloons
        for balloon in self.balloons:
            balloon.draw(surface, self.x, self.y)

        # Draw body
        color = self.color if self.get_alive_balloon_count() > 0 else Color.GRAY.value
        body_rect = pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )
        pygame.draw.ellipse(surface, color, body_rect)

        # Draw eyes
        eye_offset = 4 if self.facing_right else -4
        eye_y = int(self.y - 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + eye_offset - 4), eye_y), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + eye_offset + 4), eye_y), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + eye_offset - 4), eye_y), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + eye_offset + 4), eye_y), 2)


class Player(Character):
    """Player-controlled character."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, Color.BLUE.value, is_player=True)

    def update(self, platforms: List['Platform']) -> None:
        """Update player with input handling."""
        super().update(platforms)

        # Keep in bounds horizontally
        self.x = max(20, min(GameConfig.SCREEN_WIDTH - 20, self.x))


class Enemy(Character):
    """AI-controlled enemy character."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, Color.RED.value, is_player=False)
        self.decision_timer = 0
        self.target_x = x
        self.target_y = y

    def update_ai(self, player_x: float, player_y: float, platforms: List['Platform']) -> None:
        """Update enemy AI behavior."""
        if not self.alive or self.get_alive_balloon_count() == 0:
            return

        self.decision_timer -= 1

        if self.decision_timer <= 0:
            self.decision_timer = random.randint(30, 90)

            # Set target near player
            self.target_x = player_x + random.randint(-100, 100)
            self.target_y = player_y + random.randint(-50, 50)

            # Flap occasionally
            if random.random() < 0.4:
                self.flap()

        # Move toward target
        dx = self.target_x - self.x
        if abs(dx) > 20:
            if dx > 0:
                self.move_right()
            else:
                self.move_left()

        # Stay away from water
        if self.y > GameConfig.WATER_LEVEL - 100 and self.flap_cooldown == 0:
            self.flap()


class Platform:
    """Represents a platform in the game arena."""

    def __init__(self, x: float, y: float, width: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = 16

    def get_rect(self) -> Tuple[float, float, float, float]:
        """Return collision rectangle."""
        return (
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )

    def draw(self, surface) -> None:
        """Draw the platform."""
        import pygame
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        pygame.draw.rect(surface, Color.PLATFORM.value, rect, border_radius=4)
        pygame.draw.rect(surface, Color.PLATFORM_HIGHLIGHT.value, rect, 2, border_radius=4)


class GiantFish:
    """The giant fish hazard that jumps from the water."""

    def __init__(self):
        self.x = GameConfig.SCREEN_WIDTH / 2
        self.y = GameConfig.SCREEN_HEIGHT + 50
        self.width = FishConfig.WIDTH
        self.height = FishConfig.HEIGHT
        self.state = "idle"  # idle, warning, jumping, eating
        self.timer = random.randint(FishConfig.COOLDOWN_MIN, FishConfig.COOLDOWN_MAX)
        self.jump_target_x = 0
        self.mouth_open = 0.0

    def update(self, player_x: float, player_y: float) -> Tuple[bool, bool]:
        """Update fish state. Returns (ate_player, should_reset)."""
        self.timer -= 1

        if self.state == "idle":
            if self.timer <= 0:
                self.state = "warning"
                self.timer = FishConfig.WARNING_FRAMES
                # Target near player's x position
                self.jump_target_x = max(100, min(GameConfig.SCREEN_WIDTH - 100, player_x))

        elif self.state == "warning":
            self.x += (self.jump_target_x - self.x) * 0.1
            if self.timer <= 0:
                self.state = "jumping"
                self.vy = FishConfig.JUMP_SPEED

        elif self.state == "jumping":
            self.y += self.vy
            self.vy += 0.3  # Gravity

            # Check if reached apex and falling near player
            if self.vy > 0 and self.y > GameConfig.WATER_LEVEL - 50:
                # Check if player is close
                if abs(player_x - self.x) < 60 and abs(player_y - self.y) < 50:
                    self.state = "eating"
                    self.timer = 30
                    return True, False

            # Return to water
            if self.y > GameConfig.SCREEN_HEIGHT + 50:
                self.state = "idle"
                self.timer = random.randint(FishConfig.COOLDOWN_MIN, FishConfig.COOLDOWN_MAX)
                return False, True

        elif self.state == "eating":
            self.mouth_open = min(1.0, self.mouth_open + 0.1)
            self.timer -= 1
            if self.timer <= 0:
                self.state = "idle"
                self.mouth_open = 0
                self.timer = random.randint(FishConfig.COOLDOWN_MIN, FishConfig.COOLDOWN_MAX)
                return False, True

        return False, False

    def is_active(self) -> bool:
        """Check if fish is in active state (warning or above water)."""
        return self.state in ["warning", "jumping", "eating"]

    def get_hazard_rect(self) -> Tuple[float, float, float, float]:
        """Get the danger zone for collision detection."""
        return (
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.x + self.width / 2,
            self.y + self.height / 2
        )

    def draw(self, surface) -> None:
        """Draw the giant fish."""
        import pygame

        if self.state == "idle":
            return

        # Draw warning shadow when in warning state
        if self.state == "warning":
            shadow_width = int(self.width * (self.timer / FishConfig.WARNING_FRAMES))
            shadow_rect = pygame.Rect(
                int(self.x - shadow_width / 2),
                GameConfig.WATER_LEVEL - 5,
                shadow_width,
                10
            )
            pygame.draw.ellipse(surface, (40, 60, 100), shadow_rect)
            return

        # Body
        body_rect = pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

        # Draw body shape (simplified fish)
        color = Color.FISH.value
        pygame.draw.ellipse(surface, color, body_rect)

        # Tail
        tail_offset = -20 if self.vy < 0 else 20
        tail_points = [
            (int(self.x - self.width / 2), int(self.y)),
            (int(self.x - self.width / 2 - 30), int(self.y - 20)),
            (int(self.x - self.width / 2 - 30), int(self.y + 20))
        ]
        pygame.draw.polygon(surface, Color.FISH_DARK.value, tail_points)

        # Fin
        fin_y = int(self.y - self.height / 2)
        pygame.draw.polygon(surface, Color.FISH_DARK.value, [
            (int(self.x), fin_y),
            (int(self.x - 15), fin_y - 20),
            (int(self.x + 15), fin_y - 20)
        ])

        # Eye
        eye_x = int(self.x + self.width / 4)
        eye_y = int(self.y - self.height / 6)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, eye_y), 8)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x + 2, eye_y), 4)

        # Mouth (opens when eating)
        mouth_width = 20 + int(self.mouth_open * 30)
        mouth_rect = pygame.Rect(
            int(self.x + self.width / 3),
            int(self.y + self.height / 6),
            mouth_width,
            10 + int(self.mouth_open * 15)
        )
        pygame.draw.ellipse(surface, (50, 50, 50), mouth_rect)

        # Teeth when eating
        if self.mouth_open > 0.5:
            for i in range(3):
                tooth_x = mouth_rect.x + 5 + i * 10
                pygame.draw.polygon(surface, (255, 255, 255), [
                    (tooth_x, mouth_rect.y),
                    (tooth_x + 4, mouth_rect.y - 8),
                    (tooth_x + 8, mouth_rect.y)
                ])
