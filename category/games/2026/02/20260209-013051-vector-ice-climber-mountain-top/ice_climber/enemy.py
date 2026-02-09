"""
Enemy that patrols floors and repairs holes in the ice.
"""

import pygame
from typing import List, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .ice_floor import IceFloor


class Enemy:
    """Patrolling enemy that repairs ice holes."""

    # Enemy constants
    SPEED = 1.5
    REPAIR_DELAY = 120  # frames between repairs
    REPAIR_RANGE = 30  # pixels to detect holes

    def __init__(self, x: float, y: float, width: int, height: int, floor_y: float):
        """Initialize enemy.

        Args:
            x: Initial x position
            y: Initial y position
            width: Enemy width
            height: Enemy height
            floor_y: Y position of the floor this enemy patrols
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.floor_y = floor_y

        # Movement
        self.vx = self.SPEED
        self.direction = 1  # 1 = right, -1 = left

        # Repair timer
        self.repair_timer = 0

    @property
    def rect(self) -> pygame.Rect:
        """Get enemy collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, floors: List["IceFloor"]):
        """Update enemy movement and behavior.

        Args:
            floors: List of ice floors in the level
        """
        # Move horizontally
        self.x += self.vx * self.direction

        # Bounce off screen edges
        if self.x <= 0:
            self.direction = 1
        elif self.x + self.width >= 800:  # SCREEN_WIDTH
            self.direction = -1

        # Keep on floor
        self.y = self.floor_y + 5

        # Update repair timer
        if self.repair_timer > 0:
            self.repair_timer -= 1

    def repair_holes(self, floor: "IceFloor") -> bool:
        """Repair holes in the given floor if nearby.

        Args:
            floor: The floor to check for holes

        Returns:
            True if a hole was repaired
        """
        # Check if this is the enemy's floor
        if abs(floor.y - self.floor_y) > 10:
            return False

        # Check repair timer
        if self.repair_timer > 0:
            return False

        # Find nearest hole
        enemy_center = self.x + self.width / 2

        for col in range(floor.grid_width):
            if floor.blocks[0][col] == 0:  # Hole found
                hole_center = col * floor.block_size + floor.block_size / 2

                if abs(hole_center - enemy_center) < self.REPAIR_RANGE:
                    # Repair this hole
                    floor.repair_block(col, 0)
                    self.repair_timer = self.REPAIR_DELAY

                    # Occasionally add extra blocks nearby
                    if random.random() < 0.3:
                        offset = random.choice([-1, 1])
                        if 0 <= col + offset < floor.grid_width:
                            floor.repair_block(col + offset, 0)

                    return True

        return False

    def draw(self, screen: pygame.Surface, color: tuple, scroll_offset: int):
        """Draw the enemy.

        Args:
            screen: Pygame surface to draw on
            color: Color tuple for enemy
            scroll_offset: Vertical scroll offset
        """
        draw_x = int(self.x)
        draw_y = int(self.y + scroll_offset)

        # Draw body (rounded rectangle)
        pygame.draw.ellipse(screen, color, (draw_x, draw_y, self.width, self.height))

        # Draw eyes
        eye_y = draw_y + 8
        eye_offset = 6 if self.direction > 0 else 2

        # White part of eyes
        pygame.draw.circle(screen, (255, 255, 255), (draw_x + eye_offset, eye_y), 4)
        pygame.draw.circle(screen, (255, 255, 255), (draw_x + eye_offset + 8, eye_y), 4)

        # Pupils (look in movement direction)
        pupil_offset = 1 if self.direction > 0 else -1
        pygame.draw.circle(screen, (0, 0, 0), (draw_x + eye_offset + pupil_offset, eye_y), 2)
        pygame.draw.circle(screen, (0, 0, 0), (draw_x + eye_offset + 8 + pupil_offset, eye_y), 2)

        # Draw repair indicator (small wrench-like shape)
        if self.repair_timer > 0:
            # Flash when repairing
            if (self.repair_timer // 10) % 2 == 0:
                pygame.draw.line(
                    screen,
                    (255, 255, 0),
                    (draw_x + self.width // 2, draw_y - 5),
                    (draw_x + self.width // 2, draw_y - 15),
                    3,
                )
                pygame.draw.circle(
                    screen,
                    (255, 255, 0),
                    (draw_x + self.width // 2, draw_y - 5),
                    3,
                )
