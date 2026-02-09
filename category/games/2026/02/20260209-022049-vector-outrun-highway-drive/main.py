"""Vector Outrun Highway Drive - Retro pseudo-3D racing game."""

import math
import random
import pygame

# Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_COLOR = (10, 10, 50)
HORIZON_COLOR = (30, 30, 80)
GRASS_COLOR = (20, 80, 20)
ROAD_COLOR = (60, 60, 60)
ROAD_MARKING_COLOR = (200, 200, 200)
ROAD_EDGE_COLOR = (180, 50, 50)
PLAYER_COLOR = (0, 150, 255)
TEXT_COLOR = (255, 255, 255)
HUD_COLOR = (255, 255, 0)

# Road parameters
ROAD_WIDTH = 2000
SEGMENT_LENGTH = 200
DRAW_DISTANCE = 100  # Number of segments to draw
CAMERA_HEIGHT = 1000
CAMERA_DEPTH = 0.84  # FOV scaling factor

# Player parameters
PLAYER_X = 0
PLAYER_Z = 0  # Position on road (0 = camera position)
MAX_SPEED = 300
ACCELERATION = 10
BRAKING = 15
FRICTION = 2
STEERING_SENSITIVITY = 3

# Traffic parameters
TRAFFIC_COLORS = [
    (255, 50, 50),    # Red car
    (50, 255, 50),    # Green car
    (255, 255, 50),   # Yellow car
    (255, 100, 0),    # Orange car
    (200, 50, 200),   # Purple car
    (100, 200, 255),  # Light blue car
]

class Segment:
    """A single road segment with 3D projection data."""

    def __init__(self, z):
        self.z = z
        self.curve = 0
        self.y = 0

    def project(self, camera_x, camera_y, camera_z):
        """Project 3D world coordinates to 2D screen coordinates."""
        # Relative position from camera
        rel_z = self.z - camera_z
        if rel_z <= 0:
            return None

        # Apply perspective projection
        scale = CAMERA_DEPTH / rel_z * SCREEN_WIDTH
        screen_x = SCREEN_WIDTH / 2 + scale * (self.x - camera_x)
        screen_y = SCREEN_HEIGHT / 2 - scale * (self.y - camera_y)
        screen_w = scale * ROAD_WIDTH

        return (screen_x, screen_y, screen_w, scale)


class Road:
    """Manages the pseudo-3D road with curves and hills."""

    def __init__(self):
        self.segments = []
        self.curve_amount = 0
        self.target_curve = 0
        self.current_curve = 0
        self.track_length = DRAW_DISTANCE * SEGMENT_LENGTH

        # Initialize segments
        for i in range(DRAW_DISTANCE + 50):
            self.add_segment()

    def add_segment(self):
        """Add a new segment to the road."""
        z = len(self.segments) * SEGMENT_LENGTH
        seg = Segment(z)

        # Add curve variation
        if len(self.segments) > 20:
            if random.random() < 0.02:
                self.target_curve = random.uniform(-3, 3)

        # Smooth curve transition
        self.current_curve += (self.target_curve - self.current_curve) * 0.01
        seg.curve = self.current_curve

        self.segments.append(seg)

    def update(self, speed):
        """Update road state based on player speed."""
        # Calculate total curve for current view
        self.curve_amount = sum(s.curve for s in self.segments[:DRAW_DISTANCE]) / DRAW_DISTANCE

    def get_segment(self, z):
        """Get the segment at a given Z position."""
        index = int((z % self.track_length) / SEGMENT_LENGTH)
        return self.segments[min(index, len(self.segments) - 1)]


class Car:
    """Traffic car on the road."""

    def __init__(self, z, x):
        self.z = z
        self.x = x  # Lateral position (-1 to 1)
        self.speed = random.uniform(50, 150)
        self.width = 0.15
        self.color = random.choice(TRAFFIC_COLORS)
        self.overtaken = False

    def update(self, dt, player_z, player_speed):
        """Update car position."""
        # Move car forward at its speed
        self.z += self.speed * dt

        # Mark as overtaken if player passes
        if self.z < player_z - 100 and not self.overtaken:
            self.overtaken = True
            return True  # Overtake bonus
        return False


class Player:
    """The player's car."""

    def __init__(self):
        self.x = 0  # Lateral position (-1 to 1, -1 = left, 1 = right)
        self.z = 0
        self.speed = 0
        self.width = 0.12
        self.distance = 0
        self.score = 0
        self.overtake_count = 0
        self.game_over = False
        self.crashed = False

    def update(self, dt, inputs):
        """Update player state."""
        if self.game_over:
            return

        # Steering
        if inputs['left']:
            self.x -= STEERING_SENSITIVITY * dt * (self.speed / MAX_SPEED + 0.3)
        if inputs['right']:
            self.x += STEERING_SENSITIVITY * dt * (self.speed / MAX_SPEED + 0.3)

        # Clamp lateral position
        self.x = max(-1.2, min(1.2, self.x))

        # Acceleration/Braking
        if inputs['up']:
            self.speed += ACCELERATION
        elif inputs['down']:
            self.speed -= BRAKING
        else:
            self.speed -= FRICTION  # Natural slowdown

        # Clamp speed
        self.speed = max(0, min(MAX_SPEED, self.speed))

        # Move forward
        self.distance += self.speed * dt

        # Off-road penalty
        if abs(self.x) > 0.9:
            self.speed *= 0.98


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Outrun Highway Drive")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset()

    def reset(self):
        """Reset game state."""
        self.road = Road()
        self.player = Player()
        self.traffic = []
        self.traffic_timer = 0
        self.base_speed = 100
        self.difficulty = 1

    def spawn_traffic(self):
        """Spawn a new traffic car."""
        # Spawn ahead of player
        z = self.player.distance + random.uniform(500, 1500)
        x = random.uniform(-0.7, 0.7)
        self.traffic.append(Car(z, x))

    def check_collisions(self):
        """Check for collisions with traffic."""
        player_hitbox = (self.player.x - self.player.width / 2,
                        self.player.x + self.player.width / 2)

        for car in self.traffic[:]:
            # Check if car is close to player in Z
            z_diff = abs(car.z - self.player.distance)
            if z_diff < 50:
                # Check lateral overlap
                car_hitbox = (car.x - car.width / 2, car.x + car.width / 2)
                if (player_hitbox[0] < car_hitbox[1] and
                    player_hitbox[1] > car_hitbox[0]):
                    self.player.crashed = True
                    self.player.game_over = True
                    self.player.speed = 0

    def project_world_to_screen(self, world_x, world_y, world_z):
        """Project world coordinates to screen coordinates."""
        camera_z = self.player.distance
        rel_z = world_z - camera_z
        if rel_z <= 0:
            return None

        scale = CAMERA_DEPTH / rel_z * SCREEN_WIDTH
        screen_x = SCREEN_WIDTH / 2 + scale * (world_x * ROAD_WIDTH / 2)
        screen_y = SCREEN_HEIGHT / 2 - scale * (world_y - CAMERA_HEIGHT)
        return int(screen_x), int(screen_y), scale

    def draw_road(self):
        """Draw the pseudo-3D road."""
        # Draw sky gradient
        for y in range(SCREEN_HEIGHT // 2):
            factor = y / (SCREEN_HEIGHT // 2)
            color = (
                int(SKY_COLOR[0] * (1 - factor) + HORIZON_COLOR[0] * factor),
                int(SKY_COLOR[1] * (1 - factor) + HORIZON_COLOR[1] * factor),
                int(SKY_COLOR[2] * (1 - factor) + HORIZON_COLOR[2] * factor),
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        # Draw ground
        pygame.draw.rect(self.screen, GRASS_COLOR, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Draw road segments
        prev_x, prev_y, prev_w = None, None, None

        for i in range(DRAW_DISTANCE, 0, -1):
            seg_index = i % len(self.road.segments)
            seg = self.road.segments[seg_index]

            # Calculate curve offset
            curve_offset = self.road.curve_amount * (DRAW_DISTANCE - i) / DRAW_DISTANCE * 0.5

            # Project segment
            world_z = self.player.distance + i * SEGMENT_LENGTH
            result = self.project_world_to_screen(curve_offset, 0, world_z)

            if result is None:
                continue

            screen_x, screen_y, scale = result
            screen_w = int(scale * ROAD_WIDTH)

            if prev_y is not None:
                # Road surface
                road_points = [
                    (prev_x - prev_w // 2, prev_y),
                    (prev_x + prev_w // 2, prev_y),
                    (screen_x + screen_w // 2, screen_y),
                    (screen_x - screen_w // 2, screen_y),
                ]
                pygame.draw.polygon(self.screen, ROAD_COLOR, road_points)

                # Road edges (red/white stripes)
                edge_width = max(2, int(screen_w * 0.02))
                stripe_color = ROAD_EDGE_COLOR if (i // 3) % 2 == 0 else (255, 255, 255)

                # Left edge
                left_edge = [
                    (prev_x - prev_w // 2, prev_y),
                    (prev_x - prev_w // 2 + edge_width, prev_y),
                    (screen_x - screen_w // 2 + edge_width, screen_y),
                    (screen_x - screen_w // 2, screen_y),
                ]
                pygame.draw.polygon(self.screen, stripe_color, left_edge)

                # Right edge
                right_edge = [
                    (prev_x + prev_w // 2 - edge_width, prev_y),
                    (prev_x + prev_w // 2, prev_y),
                    (screen_x + screen_w // 2, screen_y),
                    (screen_x + screen_w // 2 - edge_width, screen_y),
                ]
                pygame.draw.polygon(self.screen, stripe_color, right_edge)

                # Lane markings
                if (i // 4) % 2 == 0:
                    marking_width = max(1, int(screen_w * 0.01))
                    marking_points = [
                        (prev_x - marking_width // 2, prev_y),
                        (prev_x + marking_width // 2, prev_y),
                        (screen_x + marking_width // 2, screen_y),
                        (screen_x - marking_width // 2, screen_y),
                    ]
                    pygame.draw.polygon(self.screen, ROAD_MARKING_COLOR, marking_points)

            prev_x, prev_y, prev_w = screen_x, screen_y, screen_w

    def draw_traffic(self):
        """Draw traffic cars."""
        # Sort by distance (far to near)
        sorted_traffic = sorted(self.traffic, key=lambda c: c.z, reverse=True)

        for car in sorted_traffic:
            result = self.project_world_to_screen(car.x, 0, car.z)
            if result is None:
                continue

            screen_x, screen_y, scale = result

            # Car dimensions
            car_width = max(10, int(scale * ROAD_WIDTH * car.width))
            car_height = max(10, int(car_width * 0.6))

            # Draw car body
            car_rect = pygame.Rect(
                screen_x - car_width // 2,
                screen_y - car_height,
                car_width,
                car_height
            )
            pygame.draw.rect(self.screen, car.color, car_rect)

            # Car windshield
            windshield_width = car_width // 2
            windshield_height = car_height // 3
            windshield_rect = pygame.Rect(
                screen_x - windshield_width // 2,
                screen_y - car_height + car_height // 6,
                windshield_width,
                windshield_height
            )
            pygame.draw.rect(self.screen, (50, 50, 50), windshield_rect)

            # Car outline
            pygame.draw.rect(self.screen, (0, 0, 0), car_rect, 1)

    def draw_player(self):
        """Draw the player's car."""
        # Player car is fixed at bottom center
        car_width = 80
        car_height = 50
        screen_x = SCREEN_WIDTH // 2 + self.player.x * SCREEN_WIDTH // 3
        screen_y = SCREEN_HEIGHT - 100

        # Car body
        car_rect = pygame.Rect(
            screen_x - car_width // 2,
            screen_y - car_height,
            car_width,
            car_height
        )
        pygame.draw.rect(self.screen, PLAYER_COLOR, car_rect)

        # Windshield
        windshield_rect = pygame.Rect(
            screen_x - car_width // 3,
            screen_y - car_height + 5,
            car_width // 1.5,
            car_height // 3
        )
        pygame.draw.rect(self.screen, (100, 200, 255), windshield_rect)

        # Racing stripes
        pygame.draw.line(self.screen, (255, 255, 255),
                        (screen_x, screen_y - car_height),
                        (screen_x, screen_y), 3)

        # Outline
        pygame.draw.rect(self.screen, (255, 255, 255), car_rect, 2)

    def draw_hud(self):
        """Draw the heads-up display."""
        # Speed gauge
        speed_text = self.font.render(f"SPEED: {int(self.player.speed)} km/h", True, HUD_COLOR)
        self.screen.blit(speed_text, (20, 20))

        # Distance score
        distance_text = self.font.render(f"DISTANCE: {int(self.player.distance)} m", True, HUD_COLOR)
        self.screen.blit(distance_text, (20, 60))

        # Overtake count
        overtake_text = self.font.render(f"OVERTAKES: {self.player.overtake_count}", True, HUD_COLOR)
        self.screen.blit(overtake_text, (20, 100))

        # Total score
        total_score = int(self.player.distance) + self.player.overtake_count * 100
        score_text = self.font.render(f"SCORE: {total_score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 20))

        # Difficulty indicator
        diff_text = self.font.render(f"LEVEL: {self.difficulty}", True, (255, 100, 100))
        self.screen.blit(diff_text, (SCREEN_WIDTH - 200, 60))

        # Off-road warning
        if abs(self.player.x) > 0.9:
            warning_text = self.font.render("OFF ROAD!", True, (255, 0, 0))
            self.screen.blit(warning_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 150))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render("CRASH!", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        final_score = int(self.player.distance) + self.player.overtake_count * 100
        score_text = self.font.render(f"Final Score: {final_score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font.render("Press R to Restart or ESC to Quit", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            # Input handling
            inputs = {'left': False, 'right': False, 'up': False, 'down': False}

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.player.game_over:
                        self.reset()

            keys = pygame.key.get_pressed()
            inputs['left'] = keys[pygame.K_LEFT]
            inputs['right'] = keys[pygame.K_RIGHT]
            inputs['up'] = keys[pygame.K_UP]
            inputs['down'] = keys[pygame.K_DOWN]

            # Update game state
            if not self.player.game_over:
                self.player.update(dt, inputs)
                self.road.update(self.player.speed)

                # Spawn traffic
                self.traffic_timer += dt
                spawn_rate = max(0.5, 2.0 - self.difficulty * 0.1)
                if self.traffic_timer >= spawn_rate:
                    self.spawn_traffic()
                    self.traffic_timer = 0

                # Update traffic
                for car in self.traffic[:]:
                    bonus = car.update(dt, self.player.distance, self.player.speed)
                    if bonus:
                        self.player.overtake_count += 1

                    # Remove cars that are too far behind
                    if car.z < self.player.distance - 200:
                        self.traffic.remove(car)

                # Increase difficulty over time
                self.difficulty = 1 + int(self.player.distance / 1000)

                self.check_collisions()

            # Draw everything
            self.draw_road()
            self.draw_traffic()
            self.draw_player()
            self.draw_hud()

            if self.player.game_over:
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
