"""Game entities for Vector Rampaging Gorilla City."""

import pygame
import random
from constants import *


class Gorilla:
    """Player controlled giant gorilla."""

    def __init__(self):
        self.x = 100
        self.y = GROUND_Y - GORILLA_HEIGHT
        self.width = GORILLA_WIDTH
        self.height = GORILLA_HEIGHT
        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.climbing = None  # None or building index
        self.health = GORILLA_MAX_HEALTH
        self.facing_right = True
        self.is_punching = False
        self.punch_timer = 0
        self.last_punch = 0
        self.punch_arm = 0  # 0 = down, 1 = extended

    def update(self, buildings):
        """Update gorilla state."""
        # Handle punch animation
        if self.is_punching:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_punch > PUNCH_DURATION:
                self.is_punching = False
                self.punch_arm = 0

        # Check if still climbing
        if self.climbing is not None:
            if self.climbing >= len(buildings) or not buildings[self.climbing].alive:
                self.climbing = None

        # Apply movement
        if self.climbing is None:
            self.x += self.vx
            self.y += self.vy

            # Gravity
            if not self.on_ground:
                self.vy += 0.5

            # Ground collision
            if self.y >= GROUND_Y - self.height:
                self.y = GROUND_Y - self.height
                self.vy = 0
                self.on_ground = True
        else:
            # Climbing movement
            self.y += self.vy
            building = buildings[self.climbing]

            # Clamp to building
            min_y = building.y - self.height + SEGMENT_HEIGHT
            max_y = GROUND_Y - self.height

            if self.y < min_y:
                self.y = min_y
            if self.y > max_y:
                self.y = max_y
                self.climbing = None

            # Snap x to building
            self.x = building.x + (building.width - self.width) // 2

        # Screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def move_left(self):
        """Move left."""
        if self.climbing is None:
            self.vx = -GORILLA_SPEED
            self.facing_right = False

    def move_right(self):
        """Move right."""
        if self.climbing is None:
            self.vx = GORILLA_SPEED
            self.facing_right = True

    def stop_horizontal(self):
        """Stop horizontal movement."""
        self.vx = 0

    def climb_up(self):
        """Climb up if on building."""
        self.vy = -GORILLA_CLIMB_SPEED

    def climb_down(self):
        """Climb down."""
        if self.climbing is not None or not self.on_ground:
            self.vy = GORILLA_CLIMB_SPEED
        else:
            self.vy = 0

    def stop_climbing(self):
        """Stop climbing."""
        self.vy = 0

    def jump(self):
        """Jump."""
        if self.on_ground and self.climbing is None:
            self.vy = -12
            self.on_ground = False

    def punch(self):
        """Punch attack."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_punch > PUNCH_COOLDOWN:
            self.is_punching = True
            self.last_punch = current_time
            self.punch_arm = 1
            return True
        return False

    def take_damage(self, amount):
        """Take damage."""
        self.health -= amount
        return self.health <= 0

    def get_punch_rect(self):
        """Get punch hitbox."""
        if not self.is_punching:
            return None

        punch_x = self.x + self.width if self.facing_right else self.x - PUNCH_RANGE
        return pygame.Rect(punch_x, self.y + 10, PUNCH_RANGE, 40)

    def draw(self, surface):
        """Draw the gorilla."""
        # Body
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLOR_GORILLA, body_rect)
        pygame.draw.rect(surface, COLOR_GORILLA_FACE, body_rect, 2)

        # Face
        face_size = 25
        face_x = self.x + 10 if self.facing_right else self.x + self.width - face_size - 10
        face_y = self.y + 10
        pygame.draw.rect(surface, COLOR_GORILLA_FACE, (face_x, face_y, face_size, 20))

        # Eyes
        eye_offset = 15 if self.facing_right else 0
        pygame.draw.circle(surface, (255, 255, 255), (int(face_x + 8 + eye_offset/2), int(face_y + 8)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(face_x + 17 + eye_offset/2), int(face_y + 8)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(face_x + 9 + eye_offset/2), int(face_y + 8)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(face_x + 18 + eye_offset/2), int(face_y + 8)), 2)

        # Arms
        arm_width = 15
        arm_length = 25 if self.punch_arm == 0 else 45
        arm_y = self.y + 30

        if self.facing_right:
            punch_arm_x = self.x + self.width - 5
            back_arm_x = self.x - 10
        else:
            punch_arm_x = self.x + 5 - arm_length
            back_arm_x = self.x + self.width - 5

        # Punching arm
        pygame.draw.rect(surface, COLOR_GORILLA, (punch_arm_x, arm_y, arm_length, arm_width))

        # Back arm
        pygame.draw.rect(surface, COLOR_GORILLA, (back_arm_x, arm_y, 20, arm_width))

        # Legs
        pygame.draw.rect(surface, COLOR_GORILLA, (self.x + 5, self.y + self.height - 20, 18, 20))
        pygame.draw.rect(surface, COLOR_GORILLA, (self.x + self.width - 23, self.y + self.height - 20, 18, 20))

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Building:
    """Destructible building."""

    def __init__(self, x, width, segments):
        self.x = x
        self.width = width
        self.segments = segments  # Number of segments
        self.segment_height = SEGMENT_HEIGHT
        self.total_height = segments * self.segment_height
        self.y = GROUND_Y - self.total_height
        self.alive = True
        self.damaged_segments = [False] * segments
        self.windows = self._generate_windows()

    def _generate_windows(self):
        """Generate window positions."""
        windows = []
        for seg in range(self.segments):
            seg_windows = []
            cols = 3
            rows = 2
            for row in range(rows):
                for col in range(cols):
                    seg_windows.append((col, row))
            windows.append(seg_windows)
        return windows

    def hit_segment(self, segment_index):
        """Hit a specific segment."""
        if 0 <= segment_index < self.segments and not self.damaged_segments[segment_index]:
            self.damaged_segments[segment_index] = True

            # Check if building should collapse
            # Building collapses if all segments are damaged or base is damaged
            if self.damaged_segments[0] or all(self.damaged_segments):
                self.alive = False

            return True
        return False

    def get_segment_at_height(self, y):
        """Get segment index at given y coordinate."""
        for i in range(self.segments):
            seg_y = self.y + i * self.segment_height
            if seg_y <= y < seg_y + self.segment_height:
                return i
        return self.segments - 1

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(self.x, self.y, self.width, self.total_height)

    def draw(self, surface):
        """Draw the building."""
        for i in range(self.segments):
            seg_y = self.y + i * self.segment_height
            color = COLOR_BUILDING_DMG if self.damaged_segments[i] else COLOR_BUILDING

            # Draw segment
            pygame.draw.rect(surface, color, (self.x, seg_y, self.width, self.segment_height))
            pygame.draw.rect(surface, (30, 30, 50), (self.x, seg_y, self.width, self.segment_height), 2)

            # Draw windows
            window_size = 12
            window_spacing_x = self.width // 4
            window_spacing_y = self.segment_height // 3

            for col, row in self.windows[i]:
                wx = self.x + window_spacing_x * (col + 1) - window_size // 2
                wy = seg_y + window_spacing_y * (row + 1) - window_size // 2
                window_color = COLOR_WINDOW if not self.damaged_segments[i] else (50, 50, 50)
                pygame.draw.rect(surface, window_color, (wx, wy, window_size, window_size))


class Helicopter:
    """Enemy helicopter that shoots at the gorilla."""

    def __init__(self):
        self.width = HELICOPTER_WIDTH
        self.height = HELICOPTER_HEIGHT
        self.direction = 1 if random.random() < 0.5 else -1
        self.x = -self.width if self.direction == 1 else SCREEN_WIDTH
        self.y = random.randint(50, 200)
        self.alive = True
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        """Update helicopter position."""
        self.x += HELICOPTER_SPEED * self.direction

        # Remove if off screen
        if (self.direction == 1 and self.x > SCREEN_WIDTH + 50) or \
           (self.direction == -1 and self.x < -self.width - 50):
            self.alive = False

    def can_shoot(self):
        """Check if helicopter can shoot."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > HELICOPTER_FIRE_RATE:
            self.last_shot = current_time
            return True
        return False

    def shoot(self, target_x, target_y):
        """Create a projectile aimed at target."""
        return Projectile(self.x + self.width // 2, self.y + self.height, target_x, target_y)

    def take_damage(self):
        """Take damage."""
        self.alive = False

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        """Draw the helicopter."""
        # Body
        pygame.draw.ellipse(surface, COLOR_HELICOPTER, (self.x, self.y + 5, self.width, self.height - 5))

        # Tail
        tail_len = 20
        if self.direction == 1:
            tail_x = self.x - tail_len + 10
        else:
            tail_x = self.x + self.width - 10
        pygame.draw.rect(surface, COLOR_HELICOPTER, (tail_x, self.y + 10, tail_len, 8))

        # Rotor
        rotor_width = 40
        pygame.draw.line(surface, (150, 150, 150),
                        (self.x + self.width // 2 - rotor_width // 2, self.y + 5),
                        (self.x + self.width // 2 + rotor_width // 2, self.y + 5), 3)

        # Cockpit
        cockpit_x = self.x + 5 if self.direction == 1 else self.x + self.width - 20
        pygame.draw.rect(surface, (100, 200, 255), (cockpit_x, self.y + 8, 15, 12))


class Projectile:
    """Projectile fired by helicopter."""

    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.alive = True

        # Calculate direction to target
        dx = target_x - x
        dy = target_y - y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        self.vx = (dx / dist) * PROJECTILE_SPEED
        self.vy = (dy / dist) * PROJECTILE_SPEED

    def update(self):
        """Update projectile position."""
        self.x += self.vx
        self.y += self.vy

        # Remove if off screen
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.alive = False

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def draw(self, surface):
        """Draw the projectile."""
        pygame.draw.circle(surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), self.width // 2)
