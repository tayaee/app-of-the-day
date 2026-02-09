"""
Vector Wonder Boy Skate Dash
A simplified side-scrolling skateboard platformer inspired by Wonder Boy.
Master momentum-based physics, jump over obstacles, and collect fruit to maintain vitality.
"""

import pygame
import sys
import random
import math
from pathlib import Path

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
COLOR_BG = (135, 206, 235)  # Sky blue
COLOR_GROUND = (139, 90, 43)  # Brown
COLOR_GRASS = (34, 139, 34)  # Forest green
COLOR_PLAYER = (255, 140, 0)  # Orange (Wonder Boy inspired)
COLOR_PLAYER_SKATE = (200, 100, 50)
COLOR_ROCK = (128, 128, 128)  # Gray
COLOR_FIRE = (255, 69, 0)  # Red-orange
COLOR_FIRE_CORE = (255, 255, 0)  # Yellow
COLOR_FRUIT = (255, 20, 147)  # Deep pink (melon)
COLOR_VITALITY_FULL = (50, 205, 50)  # Lime green
COLOR_VITALITY_LOW = (255, 0, 0)  # Red
COLOR_VITALITY_BG = (50, 50, 50)  # Dark gray
COLOR_TEXT = (0, 0, 0)
COLOR_CLOUD = (255, 255, 255)
COLOR_HILL = (34, 100, 34)  # Darker green for hills

# Physics
GRAVITY = 0.5
JUMP_FORCE = -12
SCROLL_SPEED = 5

# Game settings
BASE_GROUND_Y = SCREEN_HEIGHT - 50
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40
SKATEBOARD_WIDTH = 35
SKATEBOARD_HEIGHT = 8
VITALITY_MAX = 100
VITALITY_DEPLETION_RATE = 0.04
VITALITY_FRUIT_BONUS = 25
VITALITY_DAMAGE_OBSTACLE = 30


class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = 120
        self.ground_y = BASE_GROUND_Y
        self.y = self.ground_y - self.height - SKATEBOARD_HEIGHT
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = True
        self.is_jumping = False
        self.vitality = VITALITY_MAX
        self.alive = True
        self.invincible_timer = 0
        self.slope_angle = 0
        self.skateboard_offset_x = -3
        self.skateboard_offset_y = 0
        self.wheel_rotation = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.is_jumping = True

    def update(self, terrain_segments):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Handle terrain collision
        ground_y = self.get_ground_y(terrain_segments)
        self.ground_y = ground_y

        # Ground collision
        if self.y >= self.ground_y - self.height - SKATEBOARD_HEIGHT:
            self.y = self.ground_y - self.height - SKATEBOARD_HEIGHT
            self.vel_y = 0
            self.on_ground = True
            self.is_jumping = False

            # Calculate slope for visual rotation
            self.slope_angle = self.calculate_slope_angle(terrain_segments)
        else:
            self.on_ground = False

        # Wheel rotation animation
        if self.on_ground:
            self.wheel_rotation += SCROLL_SPEED

        # Invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Vitality depletion
        self.vitality -= VITALITY_DEPLETION_RATE
        if self.vitality <= 0:
            self.alive = False

    def get_ground_y(self, terrain_segments):
        player_center = self.x + self.width // 2

        for segment in terrain_segments:
            if segment['x_start'] <= player_center <= segment['x_end']:
                return segment['y']

        # Default to base ground if no segment found
        return BASE_GROUND_Y

    def calculate_slope_angle(self, terrain_segments):
        player_center = self.x + self.width // 2

        for i, segment in enumerate(terrain_segments):
            if segment['x_start'] <= player_center <= segment['x_end']:
                # Look at next segment to determine slope
                if i < len(terrain_segments) - 1:
                    next_segment = terrain_segments[i + 1]
                    dy = next_segment['y'] - segment['y']
                    dx = next_segment['x_end'] - next_segment['x_start']
                    return math.degrees(math.atan2(dy, dx))
        return 0

    def draw(self, surface):
        # Flash when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        # Draw skateboard
        board_x = self.x + self.skateboard_offset_x
        board_y = self.y + self.height + self.skateboard_offset_y

        # Rotate skateboard based on slope
        angle_rad = math.radians(self.slope_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        def rotate_point(px, py, cx, cy):
            dx = px - cx
            dy = py - cy
            return (cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a)

        # Skateboard board (rounded rectangle)
        board_points = []
        for bx in [board_x, board_x + SKATEBOARD_WIDTH]:
            for by in [board_y, board_y + SKATEBOARD_HEIGHT]:
                board_points.append(rotate_point(bx, by, board_x + SKATEBOARD_WIDTH // 2, board_y + SKATEBOARD_HEIGHT // 2))

        pygame.draw.polygon(surface, COLOR_PLAYER_SKATE, board_points)

        # Wheels
        wheel_radius = 5
        wheel_y_offset = 3

        front_wheel_x = board_x + SKATEBOARD_WIDTH - 8
        back_wheel_x = board_x + 8
        wheel_y = board_y + SKATEBOARD_HEIGHT + wheel_y_offset

        for wx in [back_wheel_x, front_wheel_x]:
            # Rotate wheel position
            rotated_pos = rotate_point(wx, wheel_y, board_x + SKATEBOARD_WIDTH // 2, board_y + SKATEBOARD_HEIGHT // 2)
            pygame.draw.circle(surface, (50, 50, 50), (int(rotated_pos[0]), int(rotated_pos[1])), wheel_radius)
            pygame.draw.circle(surface, (150, 150, 150), (int(rotated_pos[0]), int(rotated_pos[1])), wheel_radius - 2)

        # Draw player body
        body_color = COLOR_PLAYER
        pygame.draw.rect(surface, body_color, (self.x, self.y, self.width, self.height))

        # Draw face
        pygame.draw.circle(surface, (255, 220, 180), (self.x + self.width // 2, self.y + 12), 8)

        # Draw eyes
        pygame.draw.circle(surface, (0, 0, 0), (self.x + self.width // 2 + 3, self.y + 11), 2)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + self.width // 2 + 3, self.y + 13), 2)

        # Draw cap/hair
        pygame.draw.rect(surface, (200, 50, 50), (self.x + 5, self.y - 3, self.width - 10, 8))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_hitbox(self):
        # Smaller hitbox for forgiving gameplay
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 5)


class Terrain:
    def __init__(self):
        self.segments = []
        self.pits = []
        self.hills = []
        self.segment_width = 50
        self.generate_initial_terrain()

    def generate_initial_terrain(self):
        # Start with flat ground
        for i in range(20):
            self.segments.append({
                'x_start': i * self.segment_width,
                'x_end': (i + 1) * self.segment_width,
                'y': BASE_GROUND_Y,
                'type': 'flat'
            })

    def update(self):
        # Scroll terrain
        for segment in self.segments:
            segment['x_start'] -= SCROLL_SPEED
            segment['x_end'] -= SCROLL_SPEED

        for pit in self.pits[:]:
            pit['x'] -= SCROLL_SPEED
            if pit['x'] + pit['width'] < 0:
                self.pits.remove(pit)

        # Remove off-screen segments
        self.segments = [s for s in self.segments if s['x_end'] > 0]

        # Add new segments
        last_segment = self.segments[-1] if self.segments else None
        if last_segment and last_segment['x_end'] < SCREEN_WIDTH + 200:
            self.generate_new_segments(last_segment)

    def generate_new_segments(self, last_segment):
        base_x = last_segment['x_end']
        base_y = last_segment['y']

        # Decide what to generate
        rand = random.random()

        if rand < 0.1 and not any(p['x'] < SCREEN_WIDTH + 200 for p in self.pits):
            # Create a pit (gap)
            pit_width = random.randint(60, 120)
            self.pits.append({
                'x': base_x,
                'width': pit_width,
                'y': BASE_GROUND_Y
            })

            # Add landing platform
            for i in range(3):
                self.segments.append({
                    'x_start': base_x + pit_width + i * self.segment_width,
                    'x_end': base_x + pit_width + (i + 1) * self.segment_width,
                    'y': BASE_GROUND_Y,
                    'type': 'flat'
                })
        elif rand < 0.25:
            # Create rolling hills
            hill_height = random.randint(-30, 30)
            hill_length = random.randint(2, 4)

            for i in range(hill_length):
                # Interpolate height
                progress = i / hill_length
                y_offset = int(hill_height * math.sin(progress * math.pi))
                self.segments.append({
                    'x_start': base_x + i * self.segment_width,
                    'x_end': base_x + (i + 1) * self.segment_width,
                    'y': BASE_GROUND_Y - y_offset,
                    'type': 'hill'
                })

            # Return to flat
            self.segments.append({
                'x_start': base_x + hill_length * self.segment_width,
                'x_end': base_x + (hill_length + 1) * self.segment_width,
                'y': BASE_GROUND_Y,
                'type': 'flat'
            })
        else:
            # Flat ground
            for i in range(random.randint(2, 4)):
                self.segments.append({
                    'x_start': base_x + i * self.segment_width,
                    'x_end': base_x + (i + 1) * self.segment_width,
                    'y': BASE_GROUND_Y,
                    'type': 'flat'
                })

    def get_pit_rects(self):
        rects = []
        for pit in self.pits:
            rects.append(pygame.Rect(pit['x'], pit['y'], pit['width'], SCREEN_HEIGHT - pit['y']))
        return rects

    def draw(self, surface):
        # Draw terrain segments
        for segment in self.segments:
            points = [
                (segment['x_start'], segment['y']),
                (segment['x_end'], segment['y']),
                (segment['x_end'], SCREEN_HEIGHT),
                (segment['x_start'], SCREEN_HEIGHT)
            ]
            color = COLOR_HILL if segment['type'] == 'hill' else COLOR_GROUND
            pygame.draw.polygon(surface, color, points)

            # Draw grass on top
            pygame.draw.line(surface, COLOR_GRASS,
                           (segment['x_start'], segment['y']),
                           (segment['x_end'], segment['y']), 4)


class Obstacle:
    def __init__(self, x, obstacle_type):
        self.x = x
        self.type = obstacle_type
        self.passed = False
        self.animation_frame = 0

        if self.type == "rock":
            self.width = 30
            self.height = 30
            self.y = BASE_GROUND_Y - self.height
            self.color = COLOR_ROCK
            self.vel_x = 0
        elif self.type == "fire":
            self.width = 35
            self.height = 40
            self.y = BASE_GROUND_Y - self.height
            self.color = COLOR_FIRE
            self.vel_x = 0

    def update(self, scroll_speed):
        self.x -= scroll_speed + self.vel_x
        self.animation_frame += 1

    def draw(self, surface):
        if self.type == "rock":
            # Draw boulder (rough circle)
            pygame.draw.circle(surface, self.color, (int(self.x + self.width // 2), int(self.y + self.height // 2)), self.width // 2)
            # Add some detail
            pygame.draw.circle(surface, (100, 100, 100), (int(self.x + self.width // 2 - 5), int(self.y + self.height // 2 - 5)), 5)
            pygame.draw.circle(surface, (150, 150, 150), (int(self.x + self.width // 2 + 5), int(self.y + self.height // 2 + 5)), 4)

        elif self.type == "fire":
            # Animate fire
            flicker = int(5 * math.sin(self.animation_frame * 0.3))

            # Draw flame shape
            flame_points = [
                (self.x, self.y + self.height),
                (self.x + self.width // 2 - flicker, self.y + 10),
                (self.x + self.width // 4, self.y + self.height // 2),
                (self.x + self.width // 2 - flicker - 3, self.y),
                (self.x + self.width // 2, self.y + 10),
                (self.x + self.width // 2 + flicker + 3, self.y),
                (self.x + self.width * 3 // 4, self.y + self.height // 2),
                (self.x + self.width, self.y + self.height),
            ]
            pygame.draw.polygon(surface, self.color, flame_points)

            # Core
            core_points = [
                (self.x + self.width // 3, self.y + self.height),
                (self.x + self.width // 2, self.y + 15 + flicker // 2),
                (self.x + self.width * 2 // 3, self.y + self.height),
            ]
            pygame.draw.polygon(surface, COLOR_FIRE_CORE, core_points)

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 5)

    def is_off_screen(self):
        return self.x + self.width < 0


class Fruit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.collected = False
        self.bob_offset = random.random() * 6.28
        self.time = 0

    def update(self, scroll_speed):
        self.x -= scroll_speed
        self.time += 0.1

    def draw(self, surface):
        if self.collected:
            return

        # Bobbing animation
        bob_y = self.y + int(3 * math.sin(self.time + self.bob_offset))

        # Draw fruit (melon - oval)
        rect = pygame.Rect(self.x - self.radius, bob_y - self.radius * 0.8,
                          self.radius * 2, self.radius * 1.6)
        pygame.draw.ellipse(surface, COLOR_FRUIT, rect)

        # Highlight
        pygame.draw.ellipse(surface, (255, 150, 200),
                          (self.x - self.radius // 2, bob_y - self.radius * 0.6,
                           self.radius, self.radius * 0.6))

    def get_rect(self):
        bob_y = self.y + int(3 * math.sin(self.time + self.bob_offset))
        return pygame.Rect(self.x - self.radius, bob_y - self.radius,
                          self.radius * 2, self.radius * 2)

    def is_off_screen(self):
        return self.x + self.radius < 0


class Cloud:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 0.2 + random.random() * 0.3

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        # Draw simple cloud
        pygame.draw.circle(surface, COLOR_CLOUD, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, COLOR_CLOUD, (int(self.x + self.size), int(self.y - 5)), int(self.size * 0.8))
        pygame.draw.circle(surface, COLOR_CLOUD, (int(self.x + self.size * 2), int(self.y)), int(self.size * 0.9))

    def is_off_screen(self):
        return self.x + self.size * 3 < 0


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Wonder Boy Skate Dash")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.terrain = Terrain()
        self.obstacles = []
        self.fruits = []
        self.clouds = []

        # Initialize clouds
        for i in range(5):
            self.clouds.append(Cloud(
                100 + i * 200,
                40 + random.randint(0, 40),
                20 + random.randint(0, 15)
            ))

        self.score = 0
        self.distance = 0
        self.game_over = False
        self.next_obstacle_distance = 300
        self.next_fruit_distance = 150

    def spawn_obstacle(self):
        if self.next_obstacle_distance <= 0:
            # Check if we can spawn (not too close to a pit)
            can_spawn = True
            for pit in self.terrain.pits:
                if pit['x'] < SCREEN_WIDTH + 100:
                    can_spawn = False
                    break

            if can_spawn:
                obstacle_type = random.choice(["rock", "rock", "fire"])
                self.obstacles.append(Obstacle(SCREEN_WIDTH + 50, obstacle_type))

                # Set distance to next obstacle
                self.next_obstacle_distance = random.randint(250, 400)

                # Maybe spawn fruit with obstacle
                if random.random() < 0.4:
                    fruit_y = BASE_GROUND_Y - 70 - random.randint(0, 40)
                    self.fruits.append(Fruit(SCREEN_WIDTH + 100, fruit_y))

    def spawn_fruit(self):
        # Occasionally spawn floating fruit
        if self.next_fruit_distance <= 0:
            if random.random() < 0.3:
                fruit_y = BASE_GROUND_Y - 60 - random.randint(0, 50)
                self.fruits.append(Fruit(SCREEN_WIDTH, fruit_y))
            self.next_fruit_distance = random.randint(100, 200)

    def update(self):
        if self.game_over:
            return

        self.score += 1
        self.distance = self.score // 10

        # Update terrain
        self.terrain.update()

        # Update player
        self.player.update(self.terrain.segments)

        # Check if player fell into pit
        player_rect = self.player.get_rect()
        for pit_rect in self.terrain.get_pit_rects():
            if player_rect.colliderect(pit_rect):
                self.player.alive = False
                self.game_over = True
                return

        if not self.player.alive:
            self.game_over = True
            return

        # Update clouds
        for cloud in self.clouds[:]:
            cloud.update()
            if cloud.is_off_screen():
                self.clouds.remove(cloud)
                self.clouds.append(Cloud(
                    SCREEN_WIDTH + 50,
                    40 + random.randint(0, 40),
                    20 + random.randint(0, 15)
                ))

        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(SCROLL_SPEED)
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)

        # Update fruits
        for fruit in self.fruits[:]:
            fruit.update(SCROLL_SPEED)
            if fruit.is_off_screen():
                self.fruits.remove(fruit)

        # Spawn new obstacles and fruits
        self.next_obstacle_distance -= SCROLL_SPEED
        self.next_fruit_distance -= SCROLL_SPEED
        self.spawn_obstacle()
        self.spawn_fruit()

        # Check collisions
        self.check_collisions()

    def check_collisions(self):
        player_hitbox = self.player.get_hitbox()

        # Obstacle collision
        if self.player.invincible_timer == 0:
            for obstacle in self.obstacles:
                if player_hitbox.colliderect(obstacle.get_rect()):
                    self.player.vitality -= VITALITY_DAMAGE_OBSTACLE
                    self.player.invincible_timer = 60
                    if self.player.vitality <= 0:
                        self.player.alive = False
                    return

        # Fruit collection
        for fruit in self.fruits:
            if not fruit.collected and player_hitbox.colliderect(fruit.get_rect()):
                fruit.collected = True
                self.player.vitality = min(VITALITY_MAX, self.player.vitality + VITALITY_FRUIT_BONUS)
                self.score += 100

    def draw(self):
        # Draw background
        self.screen.fill(COLOR_BG)

        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)

        # Draw terrain
        self.terrain.draw(self.screen)

        # Draw fruits
        for fruit in self.fruits:
            fruit.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Distance
        distance_text = self.small_font.render(f"Distance: {self.distance}m", True, COLOR_TEXT)
        self.screen.blit(distance_text, (10, 35))

        # Vitality bar
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 65

        # Background
        pygame.draw.rect(self.screen, COLOR_VITALITY_BG, (bar_x, bar_y, bar_width, bar_height))

        # Vitality fill
        fill_width = int(bar_width * (self.player.vitality / VITALITY_MAX))
        vitality_color = COLOR_VITALITY_FULL if self.player.vitality > 30 else COLOR_VITALITY_LOW
        pygame.draw.rect(self.screen, vitality_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Vitality text
        vitality_text = self.small_font.render("Vitality", True, COLOR_TEXT)
        self.screen.blit(vitality_text, (bar_x + bar_width + 10, bar_y))

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        # Score text
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        # Distance text
        distance_text = self.small_font.render(f"Distance: {self.distance}m", True, (255, 255, 255))
        distance_rect = distance_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(distance_text, distance_rect)

        # Restart text
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if not self.game_over:
                            self.player.jump()

            # Update
            self.update()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
