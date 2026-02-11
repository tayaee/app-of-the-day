"""
Vector Elevator Action Spy Escape
Navigate through a high-security building using elevators and tactical movement
to retrieve documents and escape.
"""

import pygame
import random
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Building settings
NUM_FLOORS = 11  # Floors 10 (top) to 0 (basement/garage)
FLOOR_HEIGHT = SCREEN_HEIGHT // NUM_FLOORS
ELEVATOR_WIDTH = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_BLUE_DOOR = (50, 100, 200)
COLOR_RED_DOOR = (200, 50, 50)
COLOR_GREEN = (50, 200, 50)
COLOR_YELLOW = (255, 255, 50)
COLOR_CYAN = (50, 200, 255)
COLOR_ORANGE = (255, 165, 0)
COLOR_PURPLE = (150, 50, 200)
COLOR_RED = (255, 50, 50)

# Player settings
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 30
PLAYER_SPEED = 3
JUMP_FORCE = -8
GRAVITY = 0.4
CROUCH_HEIGHT = 15

# Bullet settings
BULLET_SPEED = 6
BULLET_LIFETIME = 60

# Scoring
SCORE_DOCUMENT = 100
SCORE_ENEMY_DEFEATED = 50
SCORE_ESCAPE = 1000


class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    WON = 2


class EntityType(Enum):
    PLAYER = 0
    ENEMY = 1
    BULLET = 2


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    owner: EntityType
    lifetime: int = BULLET_LIFETIME


@dataclass
class Door:
    x: int
    floor: int
    is_red: bool  # True = contains document, False = neutral
    collected: bool = False


class Enemy:
    """Security guard that patrols and shoots at the player."""

    def __init__(self, x: int, floor: int, patrol_range: int = 100):
        self.x = x
        self.floor = floor
        self.start_x = x
        self.patrol_range = patrol_range
        self.direction = 1
        self.speed = 1.5
        self.width = 20
        self.height = 30
        self.shoot_cooldown = random.randint(60, 180)
        self.alive = True
        self.state_timer = 0
        self.state = "patrol"  # patrol, alert
        self.alert_duration = 120

    def update(self, player) -> Optional[Bullet]:
        """Update enemy state. Returns bullet if fired."""
        if not self.alive:
            return None

        self.state_timer += 1
        self.shoot_cooldown -= 1

        # Check if player is on same floor
        player_floor = NUM_FLOORS - 1 - int(player.y // FLOOR_HEIGHT)
        same_floor = (player_floor == self.floor)

        # State machine
        if same_floor and abs(player.x - self.x) < 300:
            if self.state != "alert":
                self.state = "alert"
                self.state_timer = 0

        if self.state == "alert":
            # Face player
            self.direction = 1 if player.x > self.x else -1

            # Shoot at player
            if self.shoot_cooldown <= 0 and abs(player.x - self.x) < 250:
                self.shoot_cooldown = random.randint(90, 150)
                return Bullet(self.x + self.width // 2, self.get_y() + 10,
                             self.direction * BULLET_SPEED, 0, EntityType.ENEMY)

            # Return to patrol after alert duration
            if self.state_timer > self.alert_duration:
                self.state = "patrol"
        else:
            # Patrol behavior
            self.x += self.speed * self.direction

            # Reverse at patrol boundaries
            if self.x > self.start_x + self.patrol_range:
                self.direction = -1
            elif self.x < self.start_x - self.patrol_range:
                self.direction = 1

        # Keep in bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

        return None

    def get_y(self) -> int:
        """Get pixel Y position based on floor."""
        return (NUM_FLOORS - 1 - self.floor) * FLOOR_HEIGHT + (FLOOR_HEIGHT - self.height)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), self.get_y(), self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        rect = self.get_rect()

        # Body
        color = COLOR_RED if self.state == "alert" else COLOR_PURPLE
        pygame.draw.rect(surface, color, rect)

        # Hat/helmet
        pygame.draw.rect(surface, COLOR_DARK_GRAY,
                        (rect.x + 2, rect.y, rect.width - 4, 8))

        # Eyes
        eye_x = rect.right - 6 if self.direction > 0 else rect.left + 3
        pygame.draw.circle(surface, COLOR_WHITE, (eye_x, rect.y + 12), 3)
        pygame.draw.circle(surface, COLOR_BLACK, (eye_x, rect.y + 12), 1)

        # Gun
        gun_x = rect.right if self.direction > 0 else rect.left - 10
        pygame.draw.rect(surface, COLOR_DARK_GRAY,
                        (gun_x, rect.y + 18, 10, 4))


class Elevator:
    """Vertical transport between floors."""

    def __init__(self, x: int):
        self.x = x
        self.width = ELEVATOR_WIDTH
        self.height = FLOOR_HEIGHT - 10
        self.floor = NUM_FLOORS - 1  # Start at top
        self.target_floor = self.floor
        self.move_speed = 2
        self.moving = False
        self.doors_open = True
        self.door_anim = 1.0  # 1.0 = fully open, 0.0 = closed
        self.wait_timer = 0

    def get_y(self) -> int:
        """Get pixel Y position based on current floor."""
        target_y = (NUM_FLOORS - 1 - self.floor) * FLOOR_HEIGHT + 5
        return target_y

    def request(self, floor: int) -> None:
        """Request elevator to go to floor."""
        if 0 <= floor < NUM_FLOORS:
            self.target_floor = floor
            self.moving = True

    def update(self, player) -> bool:
        """Update elevator state. Returns True if player is inside."""
        current_y = self.get_y()

        # Calculate target Y
        target_y = (NUM_FLOORS - 1 - self.target_floor) * FLOOR_HEIGHT + 5

        if abs(current_y - target_y) < self.move_speed:
            # Arrived at target floor
            self.floor = self.target_floor
            self.moving = False
            self.doors_open = True
        else:
            # Moving toward target
            self.moving = True
            self.doors_open = False
            if current_y < target_y:
                self.floor += self.move_speed / FLOOR_HEIGHT
            else:
                self.floor -= self.move_speed / FLOOR_HEIGHT

        # Animate doors
        if self.doors_open:
            self.door_anim = min(1.0, self.door_anim + 0.1)
        else:
            self.door_anim = max(0.0, self.door_anim - 0.1)

        # Check if player is inside elevator
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        elevator_rect = self.get_rect()

        # Shrink elevator rect for door detection
        inner_width = int(self.width * self.door_anim)
        if inner_width < 10:
            inner_width = 10

        inner_rect = pygame.Rect(
            elevator_rect.centerx - inner_width // 2,
            elevator_rect.top + 5,
            inner_width,
            elevator_rect.height - 10
        )

        return player_rect.colliderect(inner_rect)

    def get_rect(self) -> pygame.Rect:
        y = self.get_y() if not self.moving else (NUM_FLOORS - 1 - self.floor) * FLOOR_HEIGHT + 5
        return pygame.Rect(int(self.x), int(y), self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()

        # Shaft background
        shaft_rect = pygame.Rect(rect.x, 0, rect.width, SCREEN_HEIGHT)
        pygame.draw.rect(surface, (30, 30, 30), shaft_rect)

        # Elevator car
        car_color = COLOR_CYAN if self.moving else COLOR_GRAY
        pygame.draw.rect(surface, car_color, rect)
        pygame.draw.rect(surface, COLOR_WHITE, rect, 2)

        # Doors
        door_width = self.width // 2 - 2
        open_offset = int((self.width // 2 - 5) * (1 - self.door_anim))

        # Left door
        left_door = pygame.Rect(
            rect.x + 2 - open_offset,
            rect.y + 5,
            door_width,
            rect.height - 10
        )
        pygame.draw.rect(surface, COLOR_DARK_GRAY, left_door)
        pygame.draw.rect(surface, COLOR_WHITE, left_door, 1)

        # Right door
        right_door = pygame.Rect(
            rect.centerx + 2 + open_offset,
            rect.y + 5,
            door_width,
            rect.height - 10
        )
        pygame.draw.rect(surface, COLOR_DARK_GRAY, right_door)
        pygame.draw.rect(surface, COLOR_WHITE, right_door, 1)

        # Floor indicator
        floor_text = pygame.font.Font(None, 24).render(str(int(self.floor)), True, COLOR_YELLOW)
        surface.blit(floor_text, (rect.centerx - floor_text.get_width() // 2, rect.y + 5))


class Player:
    """The spy character controlled by the player."""

    def __init__(self):
        self.x = 100
        self.y = 50  # Start near top
        self.vx = 0
        self.vy = 0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.on_ground = True
        self.crouching = False
        self.in_elevator = False
        self.facing = 1  # 1 = right, -1 = left
        self.shoot_cooldown = 0
        self.invincible = 0
        self.lives = 3

    def get_floor(self) -> int:
        """Get current floor number."""
        return NUM_FLOORS - 1 - int(self.y // FLOOR_HEIGHT)

    def update(self, keys, elevator: Elevator, doors: List[Door]) -> Optional[Bullet]:
        """Update player state. Returns bullet if fired."""
        if self.invincible > 0:
            self.invincible -= 1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Check if in elevator
        was_in_elevator = self.in_elevator
        self.in_elevator = elevator.update(self)

        # Movement in elevator
        if self.in_elevator:
            # Up/Down to change floors
            if keys[pygame.K_UP]:
                if elevator.wait_timer <= 0:
                    elevator.request(max(0, self.get_floor() - 1))
                    elevator.wait_timer = 30
            elif keys[pygame.K_DOWN]:
                if elevator.wait_timer <= 0:
                    elevator.request(min(NUM_FLOORS - 1, self.get_floor() + 1))
                    elevator.wait_timer = 30
            else:
                elevator.wait_timer = 0

            # Sync position with elevator
            elev_rect = elevator.get_rect()
            self.x = elev_rect.centerx - self.width // 2
            self.y = elev_rect.y + 10
            self.vx = 0
            self.vy = 0
            self.on_ground = True
            return None

        # Regular movement
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
            self.facing = -1
        elif keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
            self.facing = 1

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False

        # Crouch
        self.crouching = keys[pygame.K_DOWN] and self.on_ground
        if self.crouching:
            self.height = CROUCH_HEIGHT
        else:
            self.height = PLAYER_HEIGHT

        # Gravity
        if not self.on_ground:
            self.vy += GRAVITY

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Floor collision
        floor_bottom = (self.get_floor() + 1) * FLOOR_HEIGHT
        if self.y + self.height > floor_bottom:
            self.y = floor_bottom - self.height
            self.vy = 0
            self.on_ground = True

        # Screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

        # Collect documents from red doors
        bullet = None
        player_rect = self.get_rect()
        player_center = player_rect.center

        for door in doors:
            if door.is_red and not door.collected:
                # Check if passing in front of door
                door_x = door.x
                door_y = (NUM_FLOORS - 1 - door.floor) * FLOOR_HEIGHT
                door_rect = pygame.Rect(door_x, door_y, 30, FLOOR_HEIGHT)

                if abs(player_center[0] - door_rect.centerx) < 25:
                    player_floor = self.get_floor()
                    if player_floor == door.floor:
                        door.collected = True

        # Shoot
        if keys[pygame.K_z] and self.shoot_cooldown <= 0:
            self.shoot_cooldown = 15
            bullet = Bullet(
                self.x + (self.width if self.facing > 0 else 0),
                self.y + 10,
                self.facing * BULLET_SPEED,
                0,
                EntityType.PLAYER
            )

        return bullet

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
            return  # Blink when invincible

        rect = self.get_rect()

        # Body
        pygame.draw.rect(surface, COLOR_CYAN, rect)

        # Head
        head_y = rect.y - 8 if not self.crouching else rect.y
        pygame.draw.circle(surface, COLOR_WHITE, (rect.centerx, head_y), 8)

        # Eyes
        eye_offset = 3 * self.facing
        pygame.draw.circle(surface, COLOR_BLACK,
                          (rect.centerx + eye_offset, head_y - 1), 2)

        # Hat
        pygame.draw.rect(surface, (30, 30, 100),
                        (rect.centerx - 8, head_y - 12, 16, 4))

        # Gun arm
        arm_x = rect.right if self.facing > 0 else rect.left - 8
        pygame.draw.rect(surface, COLOR_GRAY,
                        (arm_x if self.facing > 0 else arm_x, rect.y + 12, 8, 4))


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Elevator Action Spy Escape")
        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.player = Player()
        self.elevator = Elevator(SCREEN_WIDTH // 2 - ELEVATOR_WIDTH // 2)
        self.doors: List[Door] = []
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.particles: List[dict] = []
        self.score = 0
        self.state = GameState.PLAYING

        self._init_building()

    def _init_building(self) -> None:
        """Initialize building layout with doors and enemies."""
        self.doors = []
        self.enemies = []

        # Create doors on each floor
        for floor in range(1, NUM_FLOORS - 1):  # Skip basement for now
            # Red doors (with documents) - 2 per floor
            red_positions = random.sample(range(50, SCREEN_WIDTH - 100, 60), min(2, 4))
            for pos in red_positions:
                self.doors.append(Door(pos, floor, True))

            # Blue doors (neutral)
            blue_positions = [p for p in range(50, SCREEN_WIDTH - 100, 80)
                             if p not in red_positions][:3]
            for pos in blue_positions:
                self.doors.append(Door(pos, floor, False))

        # Add escape car indicator in basement
        self.escape_car_x = SCREEN_WIDTH // 2 - 40

        # Place enemies on floors
        enemy_floors = [1, 3, 5, 7, 9]
        for floor in enemy_floors:
            num_enemies = random.randint(1, 2)
            for i in range(num_enemies):
                x = random.randint(50, SCREEN_WIDTH - 100)
                # Avoid elevator area
                if abs(x - SCREEN_WIDTH // 2) < 80:
                    x += 120 if x < SCREEN_WIDTH // 2 else -120
                self.enemies.append(Enemy(x, floor))

    def handle_input(self) -> None:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.state != GameState.PLAYING:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()

    def update(self) -> None:
        """Update game state."""
        if self.state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()

        # Update player
        bullet = self.player.update(keys, self.elevator, self.doors)
        if bullet:
            self.bullets.append(bullet)

        # Check document collection
        collected_count = sum(1 for d in self.doors if d.is_red and d.collected)
        total_red = sum(1 for d in self.doors if d.is_red)
        if collected_count > self.score // SCORE_DOCUMENT:
            self.score = collected_count * SCORE_DOCUMENT

        # Update enemies
        for enemy in self.enemies:
            enemy_bullet = enemy.update(self.player)
            if enemy_bullet:
                self.bullets.append(enemy_bullet)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.x += bullet.vx
            bullet.y += bullet.vy
            bullet.lifetime -= 1

            # Remove expired bullets
            if bullet.lifetime <= 0:
                self.bullets.remove(bullet)
                continue

            # Screen bounds
            if not (0 <= bullet.x <= SCREEN_WIDTH and 0 <= bullet.y <= SCREEN_HEIGHT):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            # Check bullet collisions
            bullet_rect = pygame.Rect(int(bullet.x) - 3, int(bullet.y) - 3, 6, 6)

            if bullet.owner == EntityType.PLAYER:
                # Check enemy hits
                for enemy in self.enemies:
                    if enemy.alive and enemy.get_rect().colliderect(bullet_rect):
                        enemy.alive = False
                        self.score += SCORE_ENEMY_DEFEATED
                        self._spawn_particles(enemy.x + enemy.width // 2,
                                              enemy.get_y() + enemy.height // 2,
                                              COLOR_PURPLE)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
            else:
                # Check player hit
                if self.player.invincible <= 0:
                    player_rect = self.player.get_rect()
                    # Smaller hitbox for fairness
                    hitbox = player_rect.inflate(-4, -4)
                    if hitbox.colliderect(bullet_rect):
                        self.player.lives -= 1
                        self.player.invincible = 120
                        self._spawn_particles(self.player.x + self.player.width // 2,
                                              self.player.y + self.player.height // 2,
                                              COLOR_CYAN)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

                        if self.player.lives <= 0:
                            self.state = GameState.GAME_OVER

        # Check enemy collision with player
        if self.player.invincible <= 0:
            player_rect = self.player.get_rect()
            for enemy in self.enemies:
                if enemy.alive and enemy.get_rect().colliderect(player_rect):
                    self.player.lives -= 1
                    self.player.invincible = 120
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER

        # Check win condition
        if collected_count >= total_red:
            # All documents collected, check if player reached basement
            if self.player.get_floor() == 0:
                # Check if near escape car
                if abs(self.player.x - self.escape_car_x) < 60:
                    self.state = GameState.WON
                    self.score += SCORE_ESCAPE

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def _spawn_particles(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Spawn visual effect particles."""
        for _ in range(10):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': random.randint(20, 40),
                'color': color,
                'size': random.randint(2, 5)
            })

    def draw(self) -> None:
        """Draw all game elements."""
        self.screen.fill(COLOR_BLACK)

        # Draw building
        self._draw_building()

        # Draw escape car in basement
        self._draw_escape_car()

        # Draw elevator
        self.elevator.draw(self.screen)

        # Draw doors
        for door in self.doors:
            self._draw_door(door)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            color = COLOR_YELLOW if bullet.owner == EntityType.PLAYER else COLOR_RED
            pygame.draw.circle(self.screen, color, (int(bullet.x), int(bullet.y)), 4)

        # Draw particles
        for p in self.particles:
            alpha = int(255 * (p['life'] / 40))
            s = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], alpha), (p['size'], p['size']), p['size'])
            self.screen.blit(s, (int(p['x']) - p['size'], int(p['y']) - p['size']))

        # Draw UI
        self._draw_ui()

        # Draw overlays
        if self.state == GameState.GAME_OVER:
            self._draw_overlay("MISSION FAILED", f"Final Score: {self.score}",
                             "Press SPACE to Retry")
        elif self.state == GameState.WON:
            self._draw_overlay("ESCAPE SUCCESSFUL!", f"Final Score: {self.score}",
                             "Press SPACE to Play Again")

        pygame.display.flip()

    def _draw_building(self) -> None:
        """Draw building structure."""
        # Floor lines
        for i in range(NUM_FLOORS):
            y = i * FLOOR_HEIGHT
            pygame.draw.line(self.screen, (60, 60, 70), (0, y), (SCREEN_WIDTH, y), 2)

            # Floor numbers
            floor_num = NUM_FLOORS - 1 - i
            floor_text = self.font_small.render(f"F{floor_num if floor_num > 0 else 'G'}",
                                                True, (80, 80, 90))
            self.screen.blit(floor_text, (5, y + 5))

    def _draw_door(self, door: Door) -> None:
        """Draw a door."""
        y = (NUM_FLOORS - 1 - door.floor) * FLOOR_HEIGHT

        if door.is_red and door.collected:
            # Already collected - show empty frame
            color = (60, 30, 30)
        else:
            color = COLOR_RED_DOOR if door.is_red else COLOR_BLUE_DOOR

        # Door frame
        door_rect = pygame.Rect(door.x, y + 10, 30, FLOOR_HEIGHT - 20)
        pygame.draw.rect(self.screen, color, door_rect)
        pygame.draw.rect(self.screen, COLOR_WHITE, door_rect, 2)

        # Door handle
        pygame.draw.circle(self.screen, COLOR_YELLOW,
                          (door.x + door_rect.width - 8, y + FLOOR_HEIGHT // 2), 3)

        # Document indicator for red doors
        if door.is_red and not door.collected:
            pygame.draw.polygon(self.screen, COLOR_YELLOW, [
                (door.x + door_rect.width // 2, y + 20),
                (door.x + door_rect.width // 2 - 5, y + 28),
                (door.x + door_rect.width // 2 + 5, y + 28)
            ])

    def _draw_escape_car(self) -> None:
        """Draw the escape car in basement."""
        y = (NUM_FLOORS - 1) * FLOOR_HEIGHT + FLOOR_HEIGHT // 2 - 20

        # Car body
        car_rect = pygame.Rect(self.escape_car_x, y, 80, 30)
        collected_count = sum(1 for d in self.doors if d.is_red and d.collected)
        total_red = sum(1 for d in self.doors if d.is_red)
        all_collected = collected_count >= total_red

        color = COLOR_GREEN if all_collected else (100, 80, 60)
        pygame.draw.rect(self.screen, color, car_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLOR_WHITE, car_rect, 2, border_radius=5)

        # Windshield
        pygame.draw.polygon(self.screen, (100, 150, 200), [
            (car_rect.left + 15, car_rect.top + 5),
            (car_rect.right - 15, car_rect.top + 5),
            (car_rect.right - 20, car_rect.top + 15),
            (car_rect.left + 10, car_rect.top + 15)
        ])

        # Wheels
        pygame.draw.circle(self.screen, COLOR_BLACK,
                          (car_rect.left + 15, car_rect.bottom + 3), 6)
        pygame.draw.circle(self.screen, COLOR_BLACK,
                          (car_rect.right - 15, car_rect.bottom + 3), 6)

        # Ready indicator
        if all_collected:
            ready_text = self.font_small.render("READY!", True, COLOR_GREEN)
            self.screen.blit(ready_text,
                           (car_rect.centerx - ready_text.get_width() // 2, y - 20))

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # Background panel
        pygame.draw.rect(self.screen, (20, 20, 30), (0, 0, SCREEN_WIDTH, 40))
        pygame.draw.line(self.screen, COLOR_WHITE, (0, 40), (SCREEN_WIDTH, 40), 2)

        # Score
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (120, 8))

        # Lives
        lives_text = self.font_medium.render(f"LIVES: {self.player.lives}", True, COLOR_RED)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 180, 8))

        # Documents progress
        collected = sum(1 for d in self.doors if d.is_red and d.collected)
        total = sum(1 for d in self.doors if d.is_red)
        doc_text = self.font_small.render(f"DOCS: {collected}/{total}", True, COLOR_YELLOW)
        self.screen.blit(doc_text, (SCREEN_WIDTH // 2 - 40, 10))

        # Instructions
        instr_bg = pygame.Surface((SCREEN_WIDTH, 25))
        instr_bg.set_alpha(180)
        instr_bg.fill((0, 0, 0))
        self.screen.blit(instr_bg, (0, SCREEN_HEIGHT - 25))

        instr_text = self.font_small.render(
            "Arrows: Move/Jump/Crouch | Z: Shoot | ESC: Quit",
            True, (150, 150, 150)
        )
        self.screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2,
                                      SCREEN_HEIGHT - 20))

    def _draw_overlay(self, title: str, subtitle: str, instruction: str) -> None:
        """Draw game overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title_color = COLOR_GREEN if self.state == GameState.WON else COLOR_RED
        title_text = self.font_large.render(title, True, title_color)
        subtitle_text = self.font_medium.render(subtitle, True, COLOR_WHITE)
        instr_text = self.font_small.render(instruction, True, COLOR_YELLOW)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(instr_text, instr_rect)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.clock.tick(FPS)

            self.handle_input()
            self.update()
            self.draw()

        pygame.quit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
