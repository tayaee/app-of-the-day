"""
Vector Popeye Spinach Rescue
A minimalist platformer where Popeye rescues Olive Oyl while avoiding Brutus.
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
COLOR_BG = (10, 10, 15)
COLOR_PLATFORM = (100, 100, 120)
COLOR_PLATFORM_EDGE = (140, 140, 160)
COLOR_LADDER = (80, 80, 100)
COLOR_POPEYE = (50, 200, 50)
COLOR_POPEYE_INVINCIBLE = (50, 50, 255)
COLOR_BRUTUS = (200, 50, 50)
COLOR_OLIVE = (255, 200, 150)
COLOR_SPINACH = (0, 180, 0)
COLOR_ITEM = (255, 100, 150)
COLOR_TEXT = (255, 255, 255)

# Game physics
GRAVITY = 0.5
PLAYER_SPEED = 4
CLIMB_SPEED = 3

# Platform settings
PLATFORM_HEIGHT = 16
NUM_PLATFORMS = 4
PLATFORM_Y_START = 140
PLATFORM_Y_SPACING = 100


class Platform:
    def __init__(self, y, index):
        self.y = y
        self.height = PLATFORM_HEIGHT
        self.width = 720
        self.x = 40
        self.index = index

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, COLOR_PLATFORM, rect)
        pygame.draw.rect(surface, COLOR_PLATFORM_EDGE, (self.x, self.y, self.width, 3))


class Ladder:
    def __init__(self, x, bottom_y, top_y):
        self.x = x
        self.width = 32
        self.bottom_y = bottom_y
        self.top_y = top_y

    def get_rect(self):
        return pygame.Rect(self.x, self.top_y, self.width, self.bottom_y - self.top_y)

    def draw(self, surface):
        pygame.draw.line(surface, COLOR_LADDER, (self.x, self.top_y), (self.x, self.bottom_y), 4)
        pygame.draw.line(surface, COLOR_LADDER, (self.x + self.width, self.top_y), (self.x + self.width, self.bottom_y), 4)
        for y in range(self.top_y + 12, self.bottom_y, 16):
            pygame.draw.line(surface, COLOR_LADDER, (self.x, y), (self.x + self.width, y), 3)


class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.active = True
        self.vel_y = 2
        self.item_type = random.choice(['heart', 'note'])

    def update(self):
        self.y += self.vel_y
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        if self.item_type == 'heart':
            pygame.draw.circle(surface, COLOR_ITEM, (int(self.x + 8), int(self.y + 6)), 6)
            pygame.draw.circle(surface, COLOR_ITEM, (int(self.x + 14), int(self.y + 6)), 6)
            pygame.draw.polygon(surface, COLOR_ITEM, [(self.x + 2, self.y + 8), (self.x + 22, self.y + 8), (self.x + 12, self.y + 18)])
        else:
            pygame.draw.circle(surface, COLOR_ITEM, (int(self.x + 8), int(self.y + 8)), 8)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 6), int(self.y + 6)), 2)


class Spinach:
    def __init__(self):
        self.width = 24
        self.height = 24
        self.active = False
        self.spawn_timer = 0
        self.x = 0
        self.y = 0

    def spawn(self, platforms):
        self.active = True
        platform = random.choice(platforms)
        self.x = random.randint(platform.x + 50, platform.x + platform.width - 50)
        self.y = platform.y - self.height - 5

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer > 600 and not self.active:
            self.spawn_timer = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        if not self.active:
            return
        pygame.draw.rect(surface, COLOR_SPINACH, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (0, 100, 0), (self.x + 4, self.y - 4, 16, 6))


class Popeye:
    def __init__(self):
        self.width = 28
        self.height = 36
        self.x = 400
        self.y = SCREEN_HEIGHT - 50
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.on_ladder = False
        self.climbing = False
        self.lives = 3
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 300

    def update(self, keys, platforms, ladders):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED

        on_ladder_now = False
        for ladder in ladders:
            ladder_rect = ladder.get_rect()
            player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if ladder_rect.colliderect(player_rect):
                on_ladder_now = True
                break

        self.on_ladder = on_ladder_now

        if self.on_ladder:
            self.climbing = True
            self.vel_y = 0
            if keys[pygame.K_UP]:
                self.vel_y = -CLIMB_SPEED
            elif keys[pygame.K_DOWN]:
                self.vel_y = CLIMB_SPEED
        else:
            self.climbing = False

        if not self.on_ladder and not self.on_ground:
            self.vel_y += GRAVITY

        new_x = self.x + self.vel_x
        new_x = max(10, min(new_x, SCREEN_WIDTH - self.width - 10))
        self.x = new_x

        if self.on_ladder:
            self.y += self.vel_y
            self.on_ground = False
        else:
            new_y = self.y + self.vel_y
            self.on_ground = False
            for platform in platforms:
                platform_rect = platform.get_rect()
                player_rect = pygame.Rect(self.x, new_y, self.width, self.height)
                if platform_rect.colliderect(player_rect) and self.vel_y > 0:
                    if self.y + self.height - 10 <= platform.y:
                        self.y = platform.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                        self.climbing = False
                        break
            if not self.on_ground:
                self.y = new_y

        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

    def make_invincible(self):
        self.invincible = True
        self.invincible_timer = self.invincible_duration

    def draw(self, surface):
        color = COLOR_POPEYE_INVINCIBLE if self.invincible else COLOR_POPEYE
        body_rect = pygame.Rect(self.x, self.y + 12, self.width, self.height - 12)
        pygame.draw.rect(surface, color, body_rect)
        head_rect = pygame.Rect(self.x + 4, self.y, 20, 14)
        pygame.draw.rect(surface, color, head_rect)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 10), int(self.y + 6)), 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 18), int(self.y + 6)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 10), int(self.y + 6)), 1)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 18), int(self.y + 6)), 1)


class Brutus:
    def __init__(self):
        self.width = 32
        self.height = 40
        self.x = 600
        self.y = SCREEN_HEIGHT - 50
        self.vel_x = 2
        self.direction = -1
        self.current_platform = None
        self.target_platform = None
        self.state = 'patrol'
        self.ladder_timer = 0
        self.knocked_off = False
        self.respawn_timer = 0

    def update(self, platforms, ladders, popeye):
        if self.knocked_off:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.knocked_off = False
                self.y = SCREEN_HEIGHT - 50
                self.current_platform = platforms[-1]
            return

        if self.current_platform is None:
            self.current_platform = platforms[-1]

        if self.state == 'patrol':
            self.x += self.vel_x * self.direction

            if self.x <= self.current_platform.x + 10:
                self.direction = 1
            elif self.x >= self.current_platform.x + self.current_platform.width - 10:
                self.direction = -1

            self.ladder_timer += 1
            if self.ladder_timer > 120:
                self.ladder_timer = 0
                if random.random() < 0.4:
                    self.state = 'seek_ladder'

        elif self.state == 'seek_ladder':
            nearest_ladder = None
            min_dist = float('inf')
            for ladder in ladders:
                if abs(ladder.bottom_y - self.current_platform.y) < 20:
                    dist = abs(ladder.x - self.x)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_ladder = ladder

            if nearest_ladder:
                if abs(self.x - nearest_ladder.x) > 5:
                    if self.x < nearest_ladder.x:
                        self.direction = 1
                    else:
                        self.direction = -1
                    self.x += self.vel_x * self.direction
                else:
                    self.state = 'climbing'
                    self.target_ladder = nearest_ladder
            else:
                self.state = 'patrol'

        elif self.state == 'climbing':
            self.x = self.target_ladder.x + 2
            self.y -= CLIMB_SPEED * 0.7

            target_y = self.target_ladder.top_y
            if self.y <= target_y:
                for platform in platforms:
                    if abs(platform.y - target_y) < 30:
                        self.current_platform = platform
                        self.y = platform.y - self.height
                        break
                self.state = 'patrol'
                self.ladder_timer = 0

        dx = popeye.x - self.x
        if abs(dx) > 50:
            if dx > 0:
                self.direction = 1
            else:
                self.direction = -1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def knock_off(self):
        self.knocked_off = True
        self.respawn_timer = 180
        self.y = SCREEN_HEIGHT + 50

    def draw(self, surface):
        if self.knocked_off:
            return
        body_rect = pygame.Rect(self.x, self.y + 14, self.width, self.height - 14)
        pygame.draw.rect(surface, COLOR_BRUTUS, body_rect)
        head_rect = pygame.Rect(self.x + 2, self.y, 28, 16)
        pygame.draw.rect(surface, COLOR_BRUTUS, head_rect)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 10), int(self.y + 7)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 22), int(self.y + 7)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 10), int(self.y + 7)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 22), int(self.y + 7)), 2)


class OliveOyl:
    def __init__(self):
        self.x = 400
        self.y = PLATFORM_Y_START - 60
        self.width = 20
        self.height = 30
        self.drop_timer = 0
        self.drop_rate = 180

    def update(self):
        self.drop_timer += 1

    def should_drop_item(self):
        if self.drop_timer >= self.drop_rate:
            self.drop_timer = 0
            return True
        return False

    def get_drop_position(self):
        offset_x = random.randint(-100, 100)
        return self.x + offset_x, self.y + 30

    def draw(self, surface):
        body_rect = pygame.Rect(self.x, self.y + 10, self.width, self.height - 10)
        pygame.draw.rect(surface, COLOR_OLIVE, body_rect)
        head_rect = pygame.Rect(self.x + 2, self.y, 16, 12)
        pygame.draw.rect(surface, COLOR_OLIVE, head_rect)
        hair_rect = pygame.Rect(self.x, self.y - 4, 20, 8)
        pygame.draw.rect(surface, (200, 150, 100), hair_rect)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Popeye Spinach Rescue")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.popeye = Popeye()
        self.platforms = []
        self.ladders = []
        self.brutus = Brutus()
        self.olive = OliveOyl()
        self.items = []
        self.spinach = Spinach()
        self.game_over = False
        self.victory = False
        self.target_score = 2000
        self.create_level()

    def create_level(self):
        for i in range(NUM_PLATFORMS):
            y = PLATFORM_Y_START + i * PLATFORM_Y_SPACING
            self.platforms.append(Platform(y, i))

        ladder_positions = [150, 400, 650]
        for i in range(NUM_PLATFORMS - 1):
            for x_pos in ladder_positions:
                top_platform = self.platforms[i]
                bottom_platform = self.platforms[i + 1]
                self.ladders.append(Ladder(x_pos, bottom_platform.y, top_platform.y + PLATFORM_HEIGHT))

    def update(self):
        if self.game_over or self.victory:
            return

        keys = pygame.key.get_pressed()
        self.popeye.update(keys, self.platforms, self.ladders)
        self.brutus.update(self.platforms, self.ladders, self.popeye)
        self.olive.update()
        self.spinach.update()

        if self.olive.should_drop_item():
            x, y = self.olive.get_drop_position()
            self.items.append(Item(x, y))

        for item in self.items[:]:
            item.update()
            if not item.active:
                self.items.remove(item)
                continue

            item_rect = item.get_rect()
            popeye_rect = pygame.Rect(self.popeye.x, self.popeye.y, self.popeye.width, self.popeye.height)
            if item_rect.colliderect(popeye_rect):
                self.popeye.score += 100
                self.items.remove(item)

        if self.spinach.active:
            spinach_rect = self.spinach.get_rect()
            popeye_rect = pygame.Rect(self.popeye.x, self.popeye.y, self.popeye.width, self.popeye.height)
            if spinach_rect.colliderect(popeye_rect):
                self.popeye.make_invincible()
                self.spinach.active = False
                self.popeye.score += 500

        if not self.brutus.knocked_off:
            brutus_rect = self.brutus.get_rect()
            popeye_rect = pygame.Rect(self.popeye.x, self.popeye.y, self.popeye.width, self.popeye.height)
            if brutus_rect.colliderect(popeye_rect):
                if self.popeye.invincible:
                    self.brutus.knock_off()
                    self.popeye.score += 500
                else:
                    self.popeye.lives -= 1
                    self.popeye.x = 400
                    self.popeye.y = SCREEN_HEIGHT - 50
                    self.brutus.x = 600
                    self.brutus.y = SCREEN_HEIGHT - 50

        if self.popeye.lives <= 0:
            self.game_over = True

        if self.popeye.score >= self.target_score:
            self.victory = True

    def draw(self):
        self.screen.fill(COLOR_BG)

        for platform in self.platforms:
            platform.draw(self.screen)

        for ladder in self.ladders:
            ladder.draw(self.screen)

        self.olive.draw(self.screen)

        for item in self.items:
            item.draw(self.screen)

        self.spinach.draw(self.screen)
        self.brutus.draw(self.screen)
        self.popeye.draw(self.screen)

        self.draw_hud()

        if self.game_over:
            self.draw_message("GAME OVER", f"Score: {self.popeye.score} - Press R to restart")
        elif self.victory:
            self.draw_message("VICTORY!", f"Score: {self.popeye.score} - Press R to play again")

        pygame.display.flip()

    def draw_hud(self):
        score_text = self.small_font.render(f"Score: {self.popeye.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        lives_text = self.small_font.render(f"Lives: {self.popeye.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (10, 35))

        if self.popeye.invincible:
            inv_text = self.small_font.render("INVINCIBLE!", True, (100, 100, 255))
            self.screen.blit(inv_text, (10, 60))

        target_text = self.small_font.render(f"Target: {self.target_score}", True, COLOR_TEXT)
        self.screen.blit(target_text, (SCREEN_WIDTH - 130, 10))

    def draw_message(self, title, subtitle):
        title_surface = self.font.render(title, True, COLOR_TEXT)
        subtitle_surface = self.small_font.render(subtitle, True, COLOR_TEXT)

        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        bg_rect = pygame.Rect(0, 0, 450, 120)
        bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, bg_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_TEXT, bg_rect, 2)

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
