"""
Vector Donkey Kong Climb
A minimalist platformer inspired by the arcade classic.
"""

import pygame
import sys
import random
from pathlib import Path

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (20, 20, 30)
COLOR_PLATFORM = (139, 90, 43)
COLOR_PLATFORM_EDGE = (160, 110, 60)
COLOR_LADDER = (100, 100, 100)
COLOR_PLAYER = (255, 50, 50)
COLOR_BARREL = (139, 69, 19)
COLOR_BARREL_HIGHLIGHT = (205, 127, 50)
COLOR_TARGET = (255, 200, 200)
COLOR_ANTAGONIST = (50, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0, 150)

# Game physics
GRAVITY = 0.6
PLAYER_SPEED = 4
CLIMB_SPEED = 3
JUMP_FORCE = -12
BARREL_SPEED = 3
BARREL_FALL_SPEED = 4

# Platform settings
PLATFORM_HEIGHT = 20
NUM_PLATFORMS = 5
PLATFORM_Y_START = 150
PLATFORM_Y_SPACING = 90


class Platform:
    def __init__(self, y, incline_direction):
        self.y = y
        self.height = PLATFORM_HEIGHT
        self.width = 700
        self.x_offset = 50
        self.incline_direction = incline_direction  # 1 for up-right, -1 for down-right

    def get_y_at_x(self, x):
        """Get platform Y position at a given X coordinate (for incline effect)."""
        incline_offset = (x - self.x_offset) * 0.02 * self.incline_direction
        return self.y + incline_offset

    def get_rect(self):
        """Get platform bounding rect."""
        return pygame.Rect(self.x_offset, self.y - 5, self.width, self.height + 10)

    def draw(self, surface):
        # Main platform body
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_PLATFORM, rect)

        # Top edge
        edge_rect = pygame.Rect(self.x_offset, self.y - 5, self.width, 5)
        pygame.draw.rect(surface, COLOR_PLATFORM_EDGE, edge_rect)

        # Girder pattern
        for i in range(self.x_offset, self.x_offset + self.width, 50):
            pygame.draw.line(surface, (100, 70, 30), (i, self.y - 5), (i + 25, self.y + self.height), 2)


class Ladder:
    def __init__(self, x, bottom_y, top_y):
        self.x = x
        self.width = 30
        self.bottom_y = bottom_y
        self.top_y = top_y

    def get_rect(self):
        return pygame.Rect(self.x, self.top_y, self.width, self.bottom_y - self.top_y)

    def draw(self, surface):
        # Side rails
        pygame.draw.line(surface, COLOR_LADDER, (self.x, self.top_y), (self.x, self.bottom_y), 4)
        pygame.draw.line(surface, COLOR_LADDER, (self.x + self.width, self.top_y), (self.x + self.width, self.bottom_y), 4)

        # Rungs
        for y in range(self.top_y + 10, self.bottom_y, 15):
            pygame.draw.line(surface, COLOR_LADDER, (self.x, y), (self.x + self.width, y), 3)


class Barrel:
    def __init__(self, x, y, platform, direction):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.platform = platform
        self.direction = direction  # 1 for right, -1 for left
        self.falling = False
        self.on_ladder = False
        self.ladder_progress = 0
        self.active = True
        self.jump_over_cooldown = 0
        self.was_jumped = False

    def update(self, ladders, all_platforms):
        if not self.active:
            return

        if self.falling:
            # Falling down ladder
            self.y += BARREL_FALL_SPEED
            self.ladder_progress += BARREL_FALL_SPEED

            # Check if reached next platform
            for platform in all_platforms:
                if abs(self.y - platform.y) < 15:
                    self.y = platform.y - self.height
                    self.falling = False
                    self.on_ladder = False
                    self.platform = platform
                    # Random direction when landing
                    self.direction = random.choice([-1, 1])
                    break

            # Remove if fell off screen
            if self.y > SCREEN_HEIGHT:
                self.active = False
        elif self.on_ladder:
            # On ladder, start falling
            self.falling = True
        else:
            # Rolling on platform
            self.x += BARREL_SPEED * self.direction

            # Apply incline effect to Y
            platform_y = self.platform.get_y_at_x(self.x)
            self.y = platform_y - self.height

            # Bounce off edges
            if self.x <= self.platform.x_offset + 10:
                self.direction = 1
            elif self.x >= self.platform.x_offset + self.platform.width - 10:
                self.direction = -1

            # Check for ladder at end of platform
            for ladder in ladders:
                if (abs(self.x - ladder.x - ladder.width) < 20 or
                    abs(self.x - ladder.x) < 20):
                    if random.random() < 0.3:  # 30% chance to fall down ladder
                        self.on_ladder = True
                        break

        # Update cooldown
        if self.jump_over_cooldown > 0:
            self.jump_over_cooldown -= 1

    def check_collision(self, player):
        if not self.active:
            return False

        barrel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

        if barrel_rect.colliderect(player_rect):
            # Check if player jumped over
            if player.vel_y < 0 and player.y > self.y + self.height:
                return "jumped"
            return "hit"
        return False

    def draw(self, surface):
        if not self.active:
            return

        # Barrel body
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(surface, COLOR_BARREL, rect)

        # Highlight
        highlight_rect = pygame.Rect(self.x + 4, self.y + 4, 8, self.height - 8)
        pygame.draw.ellipse(surface, COLOR_BARREL_HIGHLIGHT, highlight_rect)

        # Bands
        pygame.draw.line(surface, (100, 50, 10), (self.x, self.y + 6), (self.x + self.width, self.y + 6), 2)
        pygame.draw.line(surface, (100, 50, 10), (self.x, self.y + 18), (self.x + self.width, self.y + 18), 2)


class Player:
    def __init__(self):
        self.width = 30
        self.height = 40
        self.x = 100
        self.y = SCREEN_HEIGHT - 60
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.on_ladder = False
        self.climbing = False
        self.alive = True
        self.score = 0
        self.barrels_jumped = 0
        self.level = 1
        self.can_jump = True
        self.jump_cooldown = 0

    def update(self, keys, platforms, ladders):
        if not self.alive:
            return

        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        else:
            self.can_jump = True

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED

        # Check if on ladder
        on_ladder_now = False
        for ladder in ladders:
            ladder_rect = ladder.get_rect()
            player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if ladder_rect.colliderect(player_rect):
                on_ladder_now = True
                break

        self.on_ladder = on_ladder_now

        # Climbing
        if self.on_ladder:
            self.climbing = True
            self.vel_y = 0

            if keys[pygame.K_UP]:
                self.vel_y = -CLIMB_SPEED
            elif keys[pygame.K_DOWN]:
                self.vel_y = CLIMB_SPEED
            else:
                # Check if should stop at platform
                for platform in platforms:
                    if (abs(self.y + self.height - platform.y) < 10 and
                        self.vel_y < 0):
                        self.vel_y = 0
                        break
        else:
            self.climbing = False

        # Jumping (only when on ground, not on ladder)
        if self.can_jump and not self.on_ladder and self.on_ground:
            if keys[pygame.K_SPACE]:
                self.vel_y = JUMP_FORCE
                self.on_ground = False
                self.can_jump = False
                self.jump_cooldown = 15

        # Gravity
        if not self.on_ladder and not self.on_ground:
            self.vel_y += GRAVITY

        # Apply horizontal movement
        new_x = self.x + self.vel_x

        # Screen boundaries
        new_x = max(10, min(new_x, SCREEN_WIDTH - self.width - 10))
        self.x = new_x

        # Apply vertical movement
        if self.on_ladder:
            self.y += self.vel_y
            self.on_ground = False
        else:
            new_y = self.y + self.vel_y

            # Platform collision
            self.on_ground = False
            for platform in platforms:
                platform_rect = platform.get_rect()
                player_rect = pygame.Rect(self.x, new_y, self.width, self.height)

                # Check if landing on platform
                if (platform_rect.colliderect(player_rect) and
                    self.vel_y > 0 and
                    self.y + self.height - 10 <= platform.y):
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.climbing = False
                    break

            if not self.on_ground:
                self.y = new_y

        # Prevent going through bottom
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

    def draw(self, surface):
        # Body
        body_rect = pygame.Rect(self.x, self.y + 15, self.width, self.height - 15)
        pygame.draw.rect(surface, COLOR_PLAYER, body_rect)

        # Head
        head_rect = pygame.Rect(self.x + 5, self.y, 20, 18)
        pygame.draw.rect(surface, COLOR_PLAYER, head_rect)

        # Eyes
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 10), int(self.y + 7)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 20), int(self.y + 7)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 10), int(self.y + 7)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 20), int(self.y + 7)), 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Donkey Kong Climb")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.platforms = []
        self.ladders = []
        self.barrels = []
        self.barrel_spawn_timer = 0
        self.barrel_spawn_rate = 120  # Frames between spawns
        self.game_over = False
        self.victory = False
        self.message_timer = 0

        self.create_level()

    def create_level(self):
        # Create platforms with alternating inclines
        for i in range(NUM_PLATFORMS):
            y = PLATFORM_Y_START + i * PLATFORM_Y_SPACING
            incline = 1 if i % 2 == 0 else -1
            self.platforms.append(Platform(y, incline))

        # Create ladders connecting platforms
        ladder_positions = [150, 350, 550]
        for i in range(NUM_PLATFORMS - 1):
            for x_pos in ladder_positions:
                top_platform = self.platforms[i]
                bottom_platform = self.platforms[i + 1]
                self.ladders.append(Ladder(x_pos, bottom_platform.y, top_platform.y + PLATFORM_HEIGHT))

        # Starting platform at bottom
        self.platforms.append(Platform(SCREEN_HEIGHT - 60, 0))

    def spawn_barrel(self):
        # Spawn from top platform
        top_platform = self.platforms[0]
        x = top_platform.x_offset + 50
        y = top_platform.y - 30
        direction = random.choice([-1, 1])
        self.barrels.append(Barrel(x, y, top_platform, direction))

    def check_win(self):
        # Check if player reached the top platform
        if self.player.y < PLATFORM_Y_START + 30:
            self.victory = True
            self.player.score += 1000

    def update(self):
        if self.game_over or self.victory:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, self.ladders)

        # Spawn barrels
        self.barrel_spawn_timer += 1
        spawn_rate = max(60, self.barrel_spawn_rate - (self.player.level - 1) * 10)
        if self.barrel_spawn_timer >= spawn_rate:
            self.spawn_barrel()
            self.barrel_spawn_timer = 0

        # Update barrels
        for barrel in self.barrels:
            barrel.update(self.ladders, self.platforms)

            # Check collision with player
            collision = barrel.check_collision(self.player)
            if collision == "hit":
                self.game_over = True
            elif collision == "jumped" and not barrel.was_jumped:
                barrel.was_jumped = True
                self.player.score += 100
                self.player.barrels_jumped += 1

        # Remove inactive barrels
        self.barrels = [b for b in self.barrels if b.active]

        # Check win condition
        self.check_win()

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw ladders
        for ladder in self.ladders:
            ladder.draw(self.screen)

        # Draw barrels
        for barrel in self.barrels:
            barrel.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw antagonist (at top)
        antagonist_x = SCREEN_WIDTH - 100
        antagonist_y = PLATFORM_Y_START - 50
        pygame.draw.circle(self.screen, COLOR_ANTAGONIST, (antagonist_x, antagonist_y), 25)
        # Eyes
        pygame.draw.circle(self.screen, (255, 255, 0), (antagonist_x - 8, antagonist_y - 5), 5)
        pygame.draw.circle(self.screen, (255, 255, 0), (antagonist_x + 8, antagonist_y - 5), 5)

        # Draw rescue target (at top platform)
        target_x = 100
        target_y = PLATFORM_Y_START - 40
        pygame.draw.circle(self.screen, COLOR_TARGET, (target_x, target_y), 15)
        # "Help" text
        help_text = self.small_font.render("HELP!", True, (200, 0, 0))
        self.screen.blit(help_text, (target_x - 20, target_y - 35))

        # Draw HUD
        self.draw_hud()

        # Draw game over/victory screen
        if self.game_over:
            self.draw_message("GAME OVER", f"Score: {self.player.score} - Press R to restart")
        elif self.victory:
            self.draw_message("VICTORY!", f"Score: {self.player.score} - Press R for next level")

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.small_font.render(f"Level: {self.player.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (10, 35))

        # Barrels jumped
        barrel_text = self.small_font.render(f"Barrels Jumped: {self.player.barrels_jumped}", True, COLOR_TEXT)
        self.screen.blit(barrel_text, (10, 60))

    def draw_message(self, title, subtitle):
        title_surface = self.font.render(title, True, COLOR_TEXT)
        subtitle_surface = self.small_font.render(subtitle, True, COLOR_TEXT)

        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        # Semi-transparent background
        bg_rect = pygame.Rect(0, 0, 450, 120)
        bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, bg_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_TEXT, bg_rect, 2)

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)

    def next_level(self):
        self.player.level += 1
        self.player.x = 100
        self.player.y = SCREEN_HEIGHT - 60
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.barrels.clear()
        self.barrel_spawn_timer = 0
        self.victory = False

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
                    elif event.key == pygame.K_r:
                        if self.victory:
                            self.next_level()
                        else:
                            self.reset_game()

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
