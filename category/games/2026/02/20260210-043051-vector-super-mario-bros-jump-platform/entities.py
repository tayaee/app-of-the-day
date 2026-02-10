"""Game entities for the platformer."""

from typing import List, Tuple, Optional
from config import *


class Camera:
    """Follows the player through the level."""

    def __init__(self, width: int, height: int):
        self.offset_x = 0
        self.width = width
        self.height = height

    def update(self, target_x: int) -> None:
        """Update camera to follow target."""
        target = target_x - self.width // 3
        self.offset_x += (target - self.offset_x) * 0.1
        self.offset_x = max(0, min(self.offset_x, LEVEL_WIDTH - self.width))


class Player:
    """The player character."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.on_ground = False
        self.alive = True
        self.finished = False
        self.max_distance = x

    def update(self, keys, platforms: List) -> None:
        """Update player physics and input."""
        if not self.alive or self.finished:
            return

        # Horizontal input
        if keys[0]:  # Left
            self.vx -= ACCELERATION
        if keys[1]:  # Right
            self.vx += ACCELERATION

        # Apply friction
        self.vx *= FRICTION

        # Clamp velocity
        self.vx = max(-MAX_FALL_SPEED, min(MAX_FALL_SPEED, self.vx))

        # Apply gravity
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL_SPEED)

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Track max distance
        if self.x > self.max_distance:
            self.max_distance = self.x

        # Check death
        if self.y > SCREEN_HEIGHT + 100:
            self.alive = False

        # Check collisions
        self._check_collisions(platforms)

        # Keep in bounds
        self.x = max(0, min(self.x, LEVEL_WIDTH - self.width))

    def jump(self) -> None:
        """Jump if on ground."""
        if self.on_ground:
            self.vy = JUMP_STRENGTH
            self.on_ground = False

    def _check_collisions(self, platforms: List) -> None:
        """Check and resolve platform collisions."""
        self.on_ground = False

        for platform in platforms:
            if self._collides_with(platform):
                # Landing on top
                if self.vy > 0 and self.y + self.height - self.vy <= platform.y + 5:
                    self.y = platform.y - self.height
                    self.vy = 0
                    self.on_ground = True

                    # Moving platform momentum
                    if platform.vx != 0:
                        self.x += platform.vx

    def _collides_with(self, platform) -> bool:
        """Check if colliding with platform."""
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)

    def get_rect(self) -> Tuple[int, int, int, int]:
        """Get collision rect."""
        return (int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface, camera_x: int) -> None:
        """Draw the player."""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        # Body
        import pygame
        pygame.draw.rect(surface, COLOR_PLAYER, (screen_x, screen_y, self.width, self.height), border_radius=4)

        # Eye
        eye_x = screen_x + (20 if self.vx >= 0 else 4)
        pygame.draw.circle(surface, COLOR_PLAYER_EYE, (eye_x, screen_y + 12), 5)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, screen_y + 12), 2)


class Platform:
    """A platform (static or moving)."""

    def __init__(self, x: int, y: int, width: int, move_type: str = "static"):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.move_type = move_type
        self.vx = 0
        self.vy = 0
        self.start_x = x
        self.start_y = y
        self.move_range = 80
        self.move_speed = 2

        if move_type == "horizontal":
            self.vx = self.move_speed
        elif move_type == "vertical":
            self.vy = self.move_speed

    def update(self) -> None:
        """Update moving platform."""
        if self.move_type == "horizontal":
            self.x += self.vx
            if abs(self.x - self.start_x) > self.move_range:
                self.vx *= -1
        elif self.move_type == "vertical":
            self.y += self.vy
            if abs(self.y - self.start_y) > self.move_range:
                self.vy *= -1

    def draw(self, surface, camera_x: int) -> None:
        """Draw the platform."""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        color = COLOR_PLATFORM_MOVING if self.move_type != "static" else COLOR_PLATFORM
        import pygame
        pygame.draw.rect(surface, color, (screen_x, screen_y, self.width, self.height), border_radius=3)

        # Pattern for moving platforms
        if self.move_type != "static":
            for i in range(0, self.width, 20):
                pygame.draw.line(surface, (120, 120, 80), (screen_x + i, screen_y), (screen_x + i + 10, screen_y + self.height))


class Flagpole:
    """The goal object."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = FLAGPOLE_WIDTH
        self.height = FLAGPOLE_HEIGHT
        self.reached = False

    def check_collision(self, player: Player) -> bool:
        """Check if player reached the flag."""
        if not self.reached:
            player_rect = player.get_rect()
            if (player_rect[0] < self.x + self.width and
                player_rect[0] + player_rect[2] > self.x and
                player_rect[1] < self.y + self.height and
                player_rect[1] + player_rect[3] > self.y):
                self.reached = True
                return True
        return False

    def draw(self, surface, camera_x: int) -> None:
        """Draw the flagpole."""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        import pygame
        # Pole
        pygame.draw.rect(surface, (150, 150, 150), (screen_x, screen_y, self.width, self.height))
        # Ball on top
        pygame.draw.circle(surface, (200, 200, 50), (screen_x + 5, screen_y), 8)
        # Flag
        flag_color = (100, 200, 100) if self.reached else COLOR_FLAG
        pygame.draw.polygon(surface, flag_color, [
            (screen_x + 10, screen_y + 5),
            (screen_x + 50, screen_y + 20),
            (screen_x + 10, screen_y + 35)
        ])


class GameState:
    """Manages game state."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset game state."""
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.platforms = self._create_platforms()
        self.flagpole = Flagpole(LEVEL_WIDTH - 150, SCREEN_HEIGHT - GROUND_HEIGHT - FLAGPOLE_HEIGHT)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.score = 0
        self.time_left = TIME_LIMIT
        self.game_over = False
        self.victory = False
        self.waiting_start = True

    def _create_platforms(self) -> List[Platform]:
        """Create level platforms."""
        platforms = []

        # Ground segments
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        gaps = [(400, 550), (900, 1050), (1500, 1700), (2100, 2300), (2700, 2800)]
        current_x = 0

        for gap_start, gap_end in gaps:
            platforms.append(Platform(current_x, ground_y, gap_start - current_x))
            current_x = gap_end

        platforms.append(Platform(current_x, ground_y, LEVEL_WIDTH - current_x))

        # Floating platforms over gaps
        platforms.extend([
            # Gap 1 platforms
            Platform(420, 450, 100),
            Platform(500, 380, 80, "horizontal"),

            # Gap 2 platforms
            Platform(920, 420, 90),
            Platform(1000, 350, 70, "vertical"),

            # Gap 3 platforms - moving chain
            Platform(1520, 400, 80, "horizontal"),
            Platform(1620, 320, 80, "horizontal"),
            Platform(1720, 400, 80, "horizontal"),

            # Gap 4 platforms
            Platform(2120, 380, 100, "vertical"),
            Platform(2220, 450, 90),
            Platform(2320, 350, 70, "horizontal"),

            # Gap 5 platforms
            Platform(2720, 420, 80, "horizontal"),
            Platform(2820, 350, 80, "horizontal"),

            # Final ascent platforms
            Platform(2900, 300, 100, "vertical"),
            Platform(2950, 220, 80),
            Platform(3020, 150, 80, "horizontal"),
        ])

        return platforms

    def update(self, keys: Tuple[bool, bool, bool]) -> None:
        """Update game state."""
        if self.waiting_start:
            if keys[2]:  # Jump to start
                self.waiting_start = False
            return

        if self.game_over or self.victory:
            return

        # Update player
        self.player.update(keys, self.platforms)

        # Update platforms
        for p in self.platforms:
            p.update()

        # Update camera
        self.camera.update(self.player.x)

        # Check flagpole
        if self.flagpole.check_collision(self.player):
            self.player.finished = True
            self.victory = True
            self._calculate_score()

        # Check death
        if not self.player.alive:
            self.game_over = True

        # Update time
        self.time_left -= 1 / FPS
        if self.time_left <= 0:
            self.game_over = True

    def _calculate_score(self) -> None:
        """Calculate final score."""
        distance_score = int(self.player.max_distance * DISTANCE_POINTS / 10)
        height_bonus = int((SCREEN_HEIGHT - self.player.y) * FLAG_HEIGHT_BONUS / 100)
        time_bonus = int(self.time_left * TIME_POINTS_PER_SECOND)
        self.score = distance_score + height_bonus + time_bonus

    def handle_jump(self) -> None:
        """Handle jump input."""
        if self.waiting_start:
            self.waiting_start = False
        else:
            self.player.jump()

    def get_observation(self) -> dict:
        """Get AI observation."""
        nearest = self._find_nearest_platform()
        return {
            "player": {"x": self.player.x, "y": self.player.y, "vx": self.player.vx, "vy": self.player.vy},
            "on_ground": self.player.on_ground,
            "nearest_platform": nearest,
            "flagpole": {"x": self.flagpole.x, "y": self.flagpole.y},
            "camera_x": self.camera.offset_x,
            "time_left": self.time_left,
        }

    def _find_nearest_platform(self) -> Optional[dict]:
        """Find nearest platform ahead."""
        nearest = None
        min_dist = float('inf')

        for p in self.platforms:
            dist = p.x - self.player.x
            if 0 < dist < min_dist:
                min_dist = dist
                nearest = {"x": p.x, "y": p.y, "vx": p.vx, "vy": p.vy, "width": p.width}

        return nearest
