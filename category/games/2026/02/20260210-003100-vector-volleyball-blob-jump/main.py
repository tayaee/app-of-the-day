"""Vector Volleyball Blob Jump

A 1-on-1 blob volleyball game with physics-based jumping and spiking.
"""

import pygame
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
NET_COLOR = (200, 150, 100)
FLOOR_COLOR = (50, 50, 50)
PLAYER1_COLOR = (100, 200, 255)
PLAYER2_COLOR = (255, 100, 100)
BALL_COLOR = (255, 255, 100)
TEXT_COLOR = (255, 255, 255)

# Physics constants
GRAVITY = 0.5
FRICTION = 0.98
BOUNCE_DAMPING = 0.8

# Game settings
WINNING_SCORE = 11
MAX_TOUCHES = 3
NET_X = SCREEN_WIDTH // 2
NET_HEIGHT = 150
NET_WIDTH = 10

FLOOR_Y = SCREEN_HEIGHT - 30


class Vector:
    """Simple 2D vector class for physics calculations."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def sub(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def mul(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector(0, 0)
        return Vector(self.x / l, self.y / l)

    def dot(self, other):
        return self.x * other.x + self.y * other.y


class Ball:
    """Volleyball with physics."""

    def __init__(self, x, y):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.radius = 12

    def update(self):
        # Apply gravity
        self.vel.y += GRAVITY

        # Apply friction
        self.vel = self.vel.mul(FRICTION)

        # Update position
        self.pos = self.pos.add(self.vel)

        # Wall collisions
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.vel.x *= -BOUNCE_DAMPING
        elif self.pos.x + self.radius > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH - self.radius
            self.vel.x *= -BOUNCE_DAMPING

        # Ceiling collision
        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.vel.y *= -BOUNCE_DAMPING

    def draw(self, surface):
        # Draw ball
        pygame.draw.circle(surface, BALL_COLOR, (int(self.pos.x), int(self.pos.y)), self.radius)
        # Draw highlight
        pygame.draw.circle(surface, WHITE, (int(self.pos.x - 3), int(self.pos.y - 3)), 4)

    def reset(self, server_side):
        """Reset ball to serving position."""
        self.vel = Vector(0, 0)
        if server_side == 1:  # Left side
            self.pos = Vector(150, 100)
        else:
            self.pos = Vector(SCREEN_WIDTH - 150, 100)


class Blob:
    """Player character blob."""

    def __init__(self, x, y, color, is_left):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.radius = 25
        self.color = color
        self.is_left = is_left

        # Movement settings
        self.speed = 6
        self.jump_power = -13
        self.is_jumping = False
        self.on_ground = False

        # Jump tracking for spike detection
        self.jump_start_y = y
        self.at_peak = False

    def update(self, keys):
        # Horizontal movement
        move = 0
        if self.is_left:
            if keys[pygame.K_a]:
                move = -1
            if keys[pygame.K_d]:
                move = 1
        else:
            if keys[pygame.K_LEFT]:
                move = -1
            if keys[pygame.K_RIGHT]:
                move = 1

        self.vel.x = move * self.speed

        # Jumping
        if self.on_ground:
            jump_key = pygame.K_w if self.is_left else pygame.K_UP
            if keys[jump_key]:
                self.vel.y = self.jump_power
                self.on_ground = False
                self.is_jumping = True
                self.jump_start_y = self.pos.y

        # Check if at peak of jump (for spike detection)
        if self.is_jumping and self.vel.y >= 0 and not self.at_peak:
            self.at_peak = True

        # Apply gravity
        if not self.on_ground:
            self.vel.y += GRAVITY

        # Update position
        self.pos = self.pos.add(self.vel)

        # Net boundary
        if self.is_left:
            max_x = NET_X - NET_WIDTH // 2 - self.radius
            min_x = self.radius
        else:
            max_x = SCREEN_WIDTH - self.radius
            min_x = NET_X + NET_WIDTH // 2 + self.radius

        self.pos.x = max(min_x, min(max_x, self.pos.x))

        # Ground collision
        if self.pos.y + self.radius >= FLOOR_Y:
            self.pos.y = FLOOR_Y - self.radius
            self.vel.y = 0
            self.on_ground = True
            self.is_jumping = False
            self.at_peak = False

    def draw(self, surface):
        # Draw blob body (squash effect based on velocity)
        squash = 1 + abs(self.vel.y) * 0.02
        squash = min(1.3, max(0.8, squash))

        width = int(self.radius * 2 * (2 - squash))
        height = int(self.radius * 2 * squash)

        rect = pygame.Rect(
            self.pos.x - width // 2,
            self.pos.y - height // 2,
            width,
            height
        )
        pygame.draw.ellipse(surface, self.color, rect)

        # Draw eyes
        eye_offset_x = -8 if self.is_left else 8
        eye_y = self.pos.y - 5
        pygame.draw.circle(surface, WHITE, (int(self.pos.x + eye_offset_x), int(eye_y)), 6)
        pygame.draw.circle(surface, BLACK, (int(self.pos.x + eye_offset_x), int(eye_y)), 3)

    def get_touching_bounds(self):
        """Get bounding box for collision detection."""
        return pygame.Rect(
            self.pos.x - self.radius,
            self.pos.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class Game:
    """Main game state and logic."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Volleyball Blob Jump")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset entire game."""
        self.player1 = Blob(150, FLOOR_Y - 25, PLAYER1_COLOR, True)
        self.player2 = Blob(SCREEN_WIDTH - 150, FLOOR_Y - 25, PLAYER2_COLOR, False)

        self.ball = Ball(150, 100)
        self.server = 1

        self.score1 = 0
        self.score2 = 0

        self.touches_left = MAX_TOUCHES
        self.touches_right = MAX_TOUCHES

        self.last_touched = 0  # 0 = none, 1 = player1, 2 = player2
        self.ball_on_side = 1  # 1 = left, 2 = right

        self.game_over = False
        self.winner = 0
        self.message = ""
        self.message_timer = 0

    def check_ball_blob_collision(self, player):
        """Check and handle collision between ball and blob."""
        dx = self.ball.pos.x - player.pos.x
        dy = self.ball.pos.y - player.pos.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.ball.radius + player.radius:
            # Collision detected
            normal = Vector(dx, dy).normalize()

            # Determine if it's a spike (hit at peak of jump)
            is_spike = player.at_peak and not player.on_ground
            power_multiplier = 1.5 if is_spike else 1.0

            # Calculate new ball velocity based on player movement
            player_speed_factor = player.vel.length() * 0.3

            # Add player's velocity to ball
            new_vel = normal.mul((8 + player_speed_factor) * power_multiplier)
            new_vel = new_vel.add(player.vel.mul(0.5))

            self.ball.vel = new_vel

            # Separate ball from player
            overlap = (self.ball.radius + player.radius) - dist
            self.ball.pos = self.ball.pos.add(normal.mul(overlap))

            # Update touch tracking
            if player.is_left:
                self.touches_left -= 1
                self.last_touched = 1
            else:
                self.touches_right -= 1
                self.last_touched = 2

            return True
        return False

    def check_net_collision(self):
        """Check if ball hits the net."""
        net_rect = pygame.Rect(NET_X - NET_WIDTH // 2, FLOOR_Y - NET_HEIGHT, NET_WIDTH, NET_HEIGHT)

        ball_rect = pygame.Rect(
            self.ball.pos.x - self.ball.radius,
            self.ball.pos.y - self.ball.radius,
            self.ball.radius * 2,
            self.ball.radius * 2
        )

        if net_rect.colliderect(ball_rect):
            # Determine bounce direction
            if self.ball.pos.x < NET_X:
                self.ball.vel.x = -abs(self.ball.vel.x) * BOUNCE_DAMPING
                self.ball.pos.x = NET_X - NET_WIDTH // 2 - self.ball.radius
            else:
                self.ball.vel.x = abs(self.ball.vel.x) * BOUNCE_DAMPING
                self.ball.pos.x = NET_X + NET_WIDTH // 2 + self.ball.radius

    def check_scoring(self):
        """Check if a point is scored."""
        if self.ball.pos.y + self.ball.radius >= FLOOR_Y:
            # Ball hit the floor
            if self.ball.pos.x < NET_X:
                # Landed on left side - player 2 scores
                self.score2 += 1
                self.server = 2
            else:
                # Landed on right side - player 1 scores
                self.score1 += 1
                self.server = 1

            # Reset for next round
            self.ball.reset(self.server)
            self.touches_left = MAX_TOUCHES
            self.touches_right = MAX_TOUCHES
            self.last_touched = 0

            self.show_message("Point!")

            # Check for winner
            if self.score1 >= WINNING_SCORE:
                self.game_over = True
                self.winner = 1
                self.show_message("Player 1 Wins!")
            elif self.score2 >= WINNING_SCORE:
                self.game_over = True
                self.winner = 2
                self.show_message("Player 2 Wins!")

    def check_touch_violation(self):
        """Check if maximum touches exceeded."""
        if self.ball.pos.x < NET_X and self.touches_left <= 0 and self.last_touched == 1:
            # Player 1 exceeded touches
            self.score2 += 1
            self.server = 2
            self.ball.reset(self.server)
            self.touches_left = MAX_TOUCHES
            self.touches_right = MAX_TOUCHES
            self.last_touched = 0
            self.show_message("Too many touches!")

        elif self.ball.pos.x >= NET_X and self.touches_right <= 0 and self.last_touched == 2:
            # Player 2 exceeded touches
            self.score1 += 1
            self.server = 1
            self.ball.reset(self.server)
            self.touches_left = MAX_TOUCHES
            self.touches_right = MAX_TOUCHES
            self.last_touched = 0
            self.show_message("Too many touches!")

    def show_message(self, text):
        """Display a temporary message."""
        self.message = text
        self.message_timer = 60

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Update players
        self.player1.update(keys)
        self.player2.update(keys)

        # Update ball
        self.ball.update()

        # Check collisions
        self.check_ball_blob_collision(self.player1)
        self.check_ball_blob_collision(self.player2)
        self.check_net_collision()

        # Check scoring
        self.check_scoring()
        self.check_touch_violation()

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw(self):
        """Draw game state."""
        self.screen.fill(BLACK)

        # Draw floor
        pygame.draw.rect(self.screen, FLOOR_COLOR, (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))

        # Draw net
        net_rect = pygame.Rect(NET_X - NET_WIDTH // 2, FLOOR_Y - NET_HEIGHT, NET_WIDTH, NET_HEIGHT)
        pygame.draw.rect(self.screen, NET_COLOR, net_rect)

        # Draw court lines
        pygame.draw.line(self.screen, (80, 80, 80), (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 2)
        pygame.draw.line(self.screen, (80, 80, 80), (NET_X, FLOOR_Y), (NET_X, FLOOR_Y - NET_HEIGHT), 2)

        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

        # Draw ball
        self.ball.draw(self.screen)

        # Draw scores
        score1_text = self.font.render(str(self.score1), True, PLAYER1_COLOR)
        score2_text = self.font.render(str(self.score2), True, PLAYER2_COLOR)
        self.screen.blit(score1_text, (SCREEN_WIDTH // 4 - 20, 20))
        self.screen.blit(score2_text, (3 * SCREEN_WIDTH // 4 - 20, 20))

        # Draw remaining touches
        if self.touches_left < MAX_TOUCHES:
            touches_text = self.small_font.render(f"P1 Touches: {self.touches_left}", True, (150, 150, 150))
            self.screen.blit(touches_text, (50, 70))
        if self.touches_right < MAX_TOUCHES:
            touches_text = self.small_font.render(f"P2 Touches: {self.touches_right}", True, (150, 150, 150))
            self.screen.blit(touches_text, (SCREEN_WIDTH - 180, 70))

        # Draw message
        if self.message_timer > 0:
            msg_text = self.font.render(self.message, True, WHITE)
            rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, rect)

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            win_text = self.font.render(f"Player {self.winner} Wins!", True, WHITE)
            restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, WHITE)

            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

            self.screen.blit(win_text, win_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()

            # Update and draw
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
