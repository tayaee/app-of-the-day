import pygame
import sys
import math
import random


class Bubble:
    SIZES = [50, 35, 20]  # Large, Medium, Small radii
    BOUNCE_SPEED = [7, 5, 3]  # Bounce height per size
    COLORS = [
        (255, 100, 100),  # Large - Red
        (100, 200, 100),  # Medium - Green
        (100, 100, 255)   # Small - Blue
    ]

    def __init__(self, x, y, size_index, vx=0):
        self.x = x
        self.y = y
        self.size_index = size_index
        self.radius = self.SIZES[size_index]
        self.color = self.COLORS[size_index]
        self.vx = vx if vx != 0 else random.choice([-3, 3])
        self.vy = -self.BOUNCE_SPEED[size_index]
        self.gravity = 0.15
        self.on_ground = False

    def update(self, screen_width, screen_height, ground_y):
        # Apply gravity
        self.vy += self.gravity

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Wall collision
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            self.vx *= -1

        # Ground collision
        if self.y + self.radius > ground_y:
            self.y = ground_y - self.radius
            if abs(self.vy) < 2:
                self.vy = 0
                self.on_ground = True
            else:
                self.vy *= -0.95  # Slight energy loss on bounce
                # Ensure minimum bounce for the game to work
                min_bounce = self.BOUNCE_SPEED[self.size_index] * 0.7
                if abs(self.vy) < min_bounce:
                    self.vy = -min_bounce
                self.on_ground = False
        else:
            self.on_ground = False

    def draw(self, surface):
        # Draw main bubble
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

        # Draw highlight (shine effect)
        highlight_offset = self.radius // 3
        highlight_radius = self.radius // 4
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x - highlight_offset), int(self.y - highlight_offset)),
            highlight_radius
        )

        # Draw outline
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x), int(self.y)),
            self.radius,
            2
        )


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.speed = 5
        self.color = (100, 200, 255)

    def update(self, screen_width):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed

        # Clamp to screen
        self.x = max(self.width // 2, min(screen_width - self.width // 2, self.x))

    def draw(self, surface):
        # Draw body
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (200, 230, 255), rect, 2)

        # Draw eyes
        eye_y = self.y - self.height + 10
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 5), eye_y), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 5), eye_y), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x - 5), eye_y), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 5), eye_y), 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height,
            self.width,
            self.height
        )


class WireShot:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.target_y = 0
        self.speed = 12
        self.width = 3
        self.head_size = 6

    def fire(self, x, start_y, target_y):
        self.active = True
        self.x = x
        self.y = start_y
        self.target_y = target_y

    def update(self):
        if self.active:
            self.y -= self.speed
            if self.y <= self.target_y:
                self.active = False
                return True
        return False

    def draw(self, surface):
        if self.active:
            # Draw wire line
            start_pos = (self.x, self.y)
            end_pos = (self.x, self.y + 100)  # Extend downward
            pygame.draw.line(surface, (200, 200, 200), start_pos, end_pos, self.width)

            # Draw wire head
            pygame.draw.circle(surface, (255, 255, 100), (int(self.x), int(self.y)), self.head_size)


class PangGame:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vector Super Pang - Bubble Split")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)

        self.ground_y = self.height - 50
        self.player = Player(self.width // 2, self.ground_y)
        self.wire = WireShot()
        self.bubbles = []

        self.score = 0
        self.level = 1
        self.time_limit = 120  # seconds
        self.time_remaining = self.time_limit
        self.game_over = False
        self.won = False
        self.can_fire = True

        # Visual effects
        self.particles = []

        self.reset_level()

    def reset_level(self):
        self.bubbles.clear()
        self.wire.active = False
        self.can_fire = True

        # Spawn bubbles based on level
        num_bubbles = min(1 + (self.level - 1) // 2, 4)
        for i in range(num_bubbles):
            x = 150 + i * (self.width - 300) // max(1, num_bubbles - 1)
            self.bubbles.append(Bubble(x, 200, 0))

        self.time_remaining = self.time_limit

    def spawn_split_bubbles(self, parent_bubble):
        if parent_bubble.size_index < 2:  # Can split further
            new_size = parent_bubble.size_index + 1
            # Create two bubbles moving in opposite directions
            bubble1 = Bubble(parent_bubble.x, parent_bubble.y, new_size, -3)
            bubble2 = Bubble(parent_bubble.x, parent_bubble.y, new_size, 3)
            return [bubble1, bubble2]
        return []

    def create_explosion(self, x, y, color):
        for _ in range(15):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'radius': random.randint(3, 8),
                'color': color,
                'alpha': 255
            })

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_SPACE and self.can_fire and not self.game_over:
                    self.wire.fire(self.player.x, self.player.y - self.player.height, 50)
                    self.can_fire = False

                if self.game_over and event.key == pygame.K_SPACE:
                    if self.won:
                        self.level += 1
                        self.game_over = False
                        self.won = False
                        self.reset_level()
                    else:
                        # Restart game
                        self.score = 0
                        self.level = 1
                        self.game_over = False
                        self.reset_level()

        if not self.wire.active:
            self.can_fire = True

        return True

    def check_collisions(self):
        if self.wire.active:
            # Check wire collision with bubbles
            wire_head_rect = pygame.Rect(
                self.wire.x - self.wire.head_size,
                self.wire.y - self.wire.head_size,
                self.wire.head_size * 2,
                self.wire.head_size * 2
            )

            for bubble in self.bubbles[:]:
                # Check collision using distance
                dx = self.wire.x - bubble.x
                dy = self.wire.y - bubble.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < bubble.radius + self.wire.head_size:
                    # Hit!
                    self.bubbles.remove(bubble)

                    # Score based on size
                    points = [100, 200, 500][bubble.size_index]
                    self.score += points

                    # Create explosion effect
                    self.create_explosion(bubble.x, bubble.y, bubble.color)

                    # Spawn smaller bubbles if not smallest
                    new_bubbles = self.spawn_split_bubbles(bubble)
                    self.bubbles.extend(new_bubbles)

                    # Deactivate wire
                    self.wire.active = False
                    self.can_fire = True
                    break

        # Check player collision with bubbles
        player_rect = self.player.get_rect()
        for bubble in self.bubbles:
            # Closest point on rectangle to circle center
            closest_x = max(player_rect.left, min(bubble.x, player_rect.right))
            closest_y = max(player_rect.top, min(bubble.y, player_rect.bottom))

            dx = bubble.x - closest_x
            dy = bubble.y - closest_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < bubble.radius:
                self.game_over = True
                return

    def update(self):
        if self.game_over:
            return

        dt = 1 / 60
        self.time_remaining -= dt

        if self.time_remaining <= 0:
            self.game_over = True
            return

        # Update player
        self.player.update(self.width)

        # Update wire
        self.wire.update()

        # Update bubbles
        for bubble in self.bubbles:
            bubble.update(self.width, self.height, self.ground_y)

        # Check collisions
        self.check_collisions()

        # Check win condition
        if len(self.bubbles) == 0:
            self.won = True
            self.game_over = True

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            particle['alpha'] -= 5
            if particle['alpha'] <= 0:
                self.particles.remove(particle)

    def draw(self):
        # Background gradient
        for y in range(self.height):
            color_value = 20 + int(15 * y / self.height)
            pygame.draw.line(
                self.screen,
                (color_value, color_value, color_value + 10),
                (0, y),
                (self.width, y)
            )

        # Draw ground
        pygame.draw.rect(
            self.screen,
            (60, 50, 40),
            (0, self.ground_y, self.width, self.height - self.ground_y)
        )
        pygame.draw.line(
            self.screen,
            (100, 80, 60),
            (0, self.ground_y),
            (self.width, self.ground_y),
            3
        )

        # Draw bubbles
        for bubble in self.bubbles:
            bubble.draw(self.screen)

        # Draw wire
        self.wire.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw particles
        for particle in self.particles:
            particle_surface = pygame.Surface(
                (particle['radius'] * 2, particle['radius'] * 2),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                particle_surface,
                (*particle['color'], int(particle['alpha'])),
                (particle['radius'], particle['radius']),
                particle['radius']
            )
            self.screen.blit(
                particle_surface,
                (particle['x'] - particle['radius'], particle['y'] - particle['radius'])
            )

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, (200, 200, 200))
        self.screen.blit(score_text, (20, 20))

        level_text = self.font.render(f"Level: {self.level}", True, (200, 200, 200))
        self.screen.blit(level_text, (20, 60))

        # Time bar
        time_width = int((self.time_remaining / self.time_limit) * 200)
        time_color = (100, 200, 100) if self.time_remaining > 30 else (200, 100, 100)
        pygame.draw.rect(self.screen, (50, 50, 50), (self.width - 220, 20, 200, 20))
        pygame.draw.rect(self.screen, time_color, (self.width - 220, 20, time_width, 20))
        pygame.draw.rect(self.screen, (150, 150, 150), (self.width - 220, 20, 200, 20), 2)
        time_text = self.small_font.render("TIME", True, (180, 180, 180))
        self.screen.blit(time_text, (self.width - 220, 45))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.won:
                title_text = self.large_font.render("LEVEL COMPLETE!", True, (100, 255, 100))
            else:
                title_text = self.large_font.render("GAME OVER", True, (255, 100, 100))
            title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(title_text, title_rect)

            final_score_text = self.font.render(f"Final Score: {self.score}", True, (200, 200, 200))
            score_rect = final_score_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
            self.screen.blit(final_score_text, score_rect)

            if self.won:
                restart_text = self.font.render("Press SPACE for next level", True, (255, 200, 100))
            else:
                restart_text = self.font.render("Press SPACE to try again", True, (255, 200, 100))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

        # Draw controls
        controls = [
            "LEFT/RIGHT: Move player",
            "SPACE: Fire wire shot",
            "Split bubbles until they disappear!",
            "ESC: Quit"
        ]
        for i, line in enumerate(controls):
            text = self.small_font.render(line, True, (80, 80, 80))
            self.screen.blit(text, (10, self.height - 90 + i * 20))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PangGame()
    game.run()
