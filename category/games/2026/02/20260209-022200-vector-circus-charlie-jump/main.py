"""
Vector Circus Charlie Jump
A classic circus-themed arcade game where you jump through flaming hoops.
"""

import pygame
import sys
import random
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
GROUND_Y = 320

# Colors
COLOR_BG = (20, 20, 20)
COLOR_GROUND = (40, 40, 40)
COLOR_PLAYER = (255, 255, 255)
COLOR_PLAYER_ACCENT = (220, 220, 220)
COLOR_FIRE = (255, 50, 0)
COLOR_FIRE_GLOW = (255, 150, 0)
COLOR_HOOP = (180, 100, 50)
COLOR_HOOP_FIRE = (255, 80, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0, 150)

# Physics
GRAVITY = 0.5
JUMP_FORCE = -12
SCROLL_SPEED_BASE = 4
MAX_SCROLL_SPEED = 10

# Obstacles
OBSTACLE_SPAWN_INTERVAL = 180  # frames
HOOP_GAP_Y = 140  # Y position of hoop center
HOOP_GAP_HEIGHT = 70  # Size of the opening
HOOP_WIDTH = 15
FIRE_POT_WIDTH = 30
FIRE_POT_HEIGHT = 40

# Scoring
SCORE_HOOP = 10
SCORE_FIRE_POT = 5


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2


class Player:
    def __init__(self):
        self.x = 100
        self.y = GROUND_Y
        self.vy = 0
        self.on_ground = True
        self.width = 40
        self.height = 50
        self.jump_pressed = False
        self.jump_held_frames = 0

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.jump_held_frames = 0

    def update(self):
        # Apply gravity
        self.vy += GRAVITY
        self.y += self.vy

        # Ground collision
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.on_ground = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()

        # Simple vector art lion with rider
        # Body (lion)
        pygame.draw.ellipse(surface, COLOR_PLAYER, (rect.x, rect.y + 20, rect.width, 25))

        # Head (lion)
        pygame.draw.circle(surface, COLOR_PLAYER, (rect.x + 35, rect.y + 15), 12)

        # Mane
        for i in range(4):
            angle = i * 45
            import math
            mane_x = rect.x + 35 + math.cos(math.radians(angle)) * 15
            mane_y = rect.y + 15 + math.sin(math.radians(angle)) * 15
            pygame.draw.circle(surface, COLOR_PLAYER_ACCENT, (int(mane_x), int(mane_y)), 4)

        # Rider
        pygame.draw.ellipse(surface, COLOR_PLAYER_ACCENT, (rect.x + 10, rect.y + 5, 18, 20))

        # Rider head
        pygame.draw.circle(surface, COLOR_PLAYER, (rect.x + 20, rect.y), 8)

        # Legs
        leg_offset = 5 if self.on_ground else -10
        pygame.draw.line(surface, COLOR_PLAYER, (rect.x + 10, rect.y + 40),
                         (rect.x + 5, rect.y + 50 + leg_offset), 3)
        pygame.draw.line(surface, COLOR_PLAYER, (rect.x + 30, rect.y + 40),
                         (rect.x + 35, rect.y + 50 + leg_offset), 3)


class Obstacle:
    def __init__(self, x, obstacle_type):
        self.x = x
        self.type = obstacle_type  # 'hoop' or 'fire_pot'
        self.passed = False
        self.fire_offset = random.random() * 6.28

        if self.type == 'hoop':
            self.y = HOOP_GAP_Y
            self.width = HOOP_WIDTH
            self.gap_height = HOOP_GAP_HEIGHT
        else:  # fire_pot
            self.y = GROUND_Y
            self.width = FIRE_POT_WIDTH
            self.height = FIRE_POT_HEIGHT

    def update(self, scroll_speed):
        self.x -= scroll_speed
        self.fire_offset += 0.2

    def get_rect(self):
        if self.type == 'hoop':
            # Return collision rect for the hoop frame (top and bottom)
            return pygame.Rect(self.x, self.y - self.gap_height // 2, self.width, self.gap_height)
        else:
            return pygame.Rect(self.x, self.y - self.height, self.width, self.height)

    def get_safe_rect(self):
        """Returns the rect that is safe to pass through (for hoops)"""
        if self.type == 'hoop':
            return pygame.Rect(self.x, self.y - 10, self.width, 20)
        return None

    def draw(self, surface):
        if self.type == 'hoop':
            self.draw_hoop(surface)
        else:
            self.draw_fire_pot(surface)

    def draw_hoop(self, surface):
        # Hoop frame (top and bottom)
        top_y = self.y - self.gap_height // 2
        bottom_y = self.y + self.gap_height // 2

        # Draw hoop rings
        for i in range(2):
            ring_y = top_y if i == 0 else bottom_y
            pygame.draw.ellipse(surface, COLOR_HOOP,
                              (self.x - 10, ring_y - 25, self.width + 20, 50), 4)

        # Draw fire on the hoop
        for i in range(8):
            fire_y = top_y + 10 + i * (self.gap_height - 20) / 7
            if not (self.y - 10 < fire_y < self.y + 10):  # Skip the gap
                fire_height = 8 + random.randint(-3, 3)
                self.draw_flame(surface, self.x + self.width // 2, fire_y, fire_height)

    def draw_fire_pot(self, surface):
        # Pot base
        pygame.draw.rect(surface, (80, 50, 30),
                        (self.x, self.y - self.height + 15, self.width, self.height - 15))
        pygame.draw.rect(surface, (60, 40, 20),
                        (self.x + 3, self.y - self.height + 18, self.width - 6, self.height - 21))

        # Fire coming from pot
        for i in range(5):
            fire_x = self.x + 5 + i * 5
            fire_height = 30 + random.randint(-10, 10)
            self.draw_flame(surface, fire_x, self.y - self.height + 15, fire_height)

    def draw_flame(self, surface, x, y, height):
        # Animated flame effect
        offset = int(self.fire_offset + x * 0.5) % 10
        flame_color = COLOR_FIRE if offset < 5 else COLOR_FIRE_GLOW

        points = [
            (x - 3, y),
            (x + 3, y),
            (x, y - height)
        ]
        pygame.draw.polygon(surface, flame_color, points)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Circus Charlie Jump")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.scroll_speed = SCROLL_SPEED_BASE
        self.spawn_timer = 0
        self.score = 0
        self.state = GameState.MENU
        self.bg_offset = 0

    def spawn_obstacle(self):
        # Determine obstacle type
        if random.random() < 0.6:
            obs_type = 'hoop'
        else:
            obs_type = 'fire_pot'

        obstacle = Obstacle(SCREEN_WIDTH + 50, obs_type)
        self.obstacles.append(obstacle)

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for obstacle in self.obstacles:
            obs_rect = obstacle.get_rect()

            if player_rect.colliderect(obs_rect):
                # For hoops, check if player is in the gap
                if obstacle.type == 'hoop':
                    safe_rect = obstacle.get_safe_rect()
                    if safe_rect and player_rect.colliderect(safe_rect):
                        continue  # Safe passage
                    return True  # Collision with hoop frame
                else:
                    return True  # Collision with fire pot

        return False

    def handle_input(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.PLAYING:
                        self.player.jump()
                    elif self.state == GameState.GAME_OVER:
                        self.reset()
                elif event.key == pygame.K_ESCAPE:
                    return False

        return True

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # Update player
        self.player.update()

        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= OBSTACLE_SPAWN_INTERVAL:
            self.spawn_obstacle()
            self.spawn_timer = 0

        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(self.scroll_speed)

            # Check for scoring
            if not obstacle.passed and obstacle.x + obstacle.width < self.player.x:
                obstacle.passed = True
                if obstacle.type == 'hoop':
                    self.score += SCORE_HOOP
                else:
                    self.score += SCORE_FIRE_POT

                # Increase speed slightly
                self.scroll_speed = min(MAX_SCROLL_SPEED, self.scroll_speed + 0.2)

        # Remove off-screen obstacles
        self.obstacles = [ob for ob in self.obstacles if ob.x > -100]

        # Check collisions
        if self.check_collisions():
            self.state = GameState.GAME_OVER

        # Update background
        self.bg_offset = (self.bg_offset + self.scroll_speed * 0.5) % SCREEN_WIDTH

    def draw_background(self):
        self.screen.fill(COLOR_BG)

        # Draw ground line
        pygame.draw.line(self.screen, COLOR_GROUND, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

        # Draw circus tent pattern in background
        for i in range(5):
            tent_x = (i * 200 - self.bg_offset) % (SCREEN_WIDTH + 200) - 100
            tent_height = 100 + i * 20
            pygame.draw.polygon(self.screen, (30, 30, 30), [
                (tent_x, GROUND_Y),
                (tent_x + 50, GROUND_Y - tent_height),
                (tent_x + 100, GROUND_Y)
            ])

    def draw_hud(self):
        # Score background
        pygame.draw.rect(self.screen, COLOR_HUD_BG, (10, 10, 150, 50), border_radius=5)

        # Score text
        score_text = self.font.render(str(self.score), True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 15))

        # Speed indicator
        speed_percent = int((self.scroll_speed - SCROLL_SPEED_BASE) / (MAX_SCROLL_SPEED - SCROLL_SPEED_BASE) * 100)
        speed_text = self.small_font.render(f"SPD: {speed_percent}%", True, (150, 150, 150))
        self.screen.blit(speed_text, (20, 50))

    def draw_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render("CIRCUS CHARLIE", True, (255, 200, 50))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("JUMP THROUGH FLAMING HOOPS!", True, (200, 150, 50))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle, sub_rect)

        # Instructions
        instructions = [
            "PRESS SPACE TO START",
            "",
            "CONTROLS:",
            "SPACE / UP ARROW - Jump",
            "",
            "Jump through flaming hoops!",
            "Jump over fire pots!",
            "Score increases speed!",
        ]

        y = 200
        for line in instructions:
            if line == "PRESS SPACE TO START":
                color = (255, 255, 255)
                font = self.font
            elif line.startswith("CONTROLS"):
                color = (255, 200, 50)
                font = self.small_font
            else:
                color = (180, 180, 180)
                font = self.small_font

            text = font.render(line, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 30

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over = self.font.render("GAME OVER", True, (255, 50, 50))
        go_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(game_over, go_rect)

        # Final score
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(score_text, score_rect)

        # Restart prompt
        restart = self.small_font.render("PRESS SPACE TO RESTART", True, (255, 200, 50))
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(restart, restart_rect)

    def draw(self):
        self.draw_background()

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw overlays
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
