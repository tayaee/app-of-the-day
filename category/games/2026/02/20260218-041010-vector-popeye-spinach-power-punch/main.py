"""
Vector Popeye Spinach Power Punch
A fixed-screen defense action game. Punch enemies away from the center to protect Olive Oyl.
"""

import pygame
import sys
import random


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

COLOR_BG = (20, 20, 30)
COLOR_FLOOR = (40, 40, 50)
COLOR_POPEYE = (50, 200, 50)
COLOR_POPEYE_POWER = (50, 100, 255)
COLOR_BRUTUS = (200, 50, 50)
COLOR_OLIVE = (255, 200, 150)
COLOR_SPINACH = (0, 180, 0)
COLOR_PROJECTILE = (150, 150, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_PUNCH = (255, 255, 0)

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
ENEMY_WIDTH = 45
ENEMY_HEIGHT = 50
PROJECTILE_WIDTH = 15
PROJECTILE_HEIGHT = 15
SPINACH_SIZE = 25

PUNCH_RANGE = 80
PUNCH_DURATION = 10
PUNCH_COOLDOWN = 20

ENEMY_SPEED_BASE = 2
ENEMY_SPAWN_RATE_BASE = 120
PROJECTILE_SPEED = 3

SPINACH_SPAWN_RATE = 600
POWER_DURATION = 300

CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT - 120


class Player:
    def __init__(self):
        self.x = CENTER_X - PLAYER_WIDTH // 2
        self.y = CENTER_Y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.lives = 3
        self.score = 0
        self.punching = False
        self.punch_direction = 0
        self.punch_timer = 0
        self.punch_cooldown = 0
        self.power_mode = False
        self.power_timer = 0

    def punch(self, direction):
        if self.punch_cooldown > 0:
            return False

        self.punching = True
        self.punch_direction = direction
        self.punch_timer = PUNCH_DURATION
        self.punch_cooldown = PUNCH_COOLDOWN
        return True

    def get_punch_rect(self):
        if not self.punching:
            return None

        offset = PUNCH_RANGE if self.punch_direction > 0 else -PUNCH_RANGE
        punch_width = PUNCH_RANGE
        punch_height = 40
        punch_x = self.x + self.width // 2 + offset - punch_width // 2 if self.punch_direction > 0 else self.x - offset
        punch_x = self.x - punch_width if self.punch_direction < 0 else self.x + self.width

        if self.punch_direction < 0:
            punch_x = self.x - PUNCH_RANGE
        else:
            punch_x = self.x + self.width

        return pygame.Rect(punch_x, self.y + 10, PUNCH_RANGE, 40)

    def update(self):
        if self.punching:
            self.punch_timer -= 1
            if self.punch_timer <= 0:
                self.punching = False

        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1

        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False

    def activate_power(self):
        self.power_mode = True
        self.power_timer = POWER_DURATION

    def draw(self, surface):
        color = COLOR_POPEYE_POWER if self.power_mode else COLOR_POPEYE

        body_rect = pygame.Rect(self.x, self.y + 15, self.width, self.height - 15)
        pygame.draw.rect(surface, color, body_rect)

        head_rect = pygame.Rect(self.x + 5, self.y, 30, 18)
        pygame.draw.rect(surface, color, head_rect)

        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 14), int(self.y + 8)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 26), int(self.y + 8)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 14), int(self.y + 8)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 26), int(self.y + 8)), 2)

        if self.power_mode:
            pygame.draw.circle(surface, (100, 200, 255), (int(self.x + 20), int(self.y - 8)), 6)

        if self.punching:
            punch_rect = self.get_punch_rect()
            if punch_rect:
                pygame.draw.rect(surface, COLOR_PUNCH, punch_rect)

        arm_rect = pygame.Rect(self.x - 10, self.y + 20, 15, 8)
        pygame.draw.rect(surface, (100, 150, 100), arm_rect)
        arm_rect_right = pygame.Rect(self.x + self.width - 5, self.y + 20, 15, 8)
        pygame.draw.rect(surface, (100, 150, 100), arm_rect_right)


class Enemy:
    def __init__(self, from_right=True):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.speed = ENEMY_SPEED_BASE + random.uniform(-0.5, 0.5)

        if from_right:
            self.x = SCREEN_WIDTH + 10
            self.direction = -1
        else:
            self.x = -self.width - 10
            self.direction = 1

        self.y = CENTER_Y + random.randint(-20, 20)
        self.active = True
        self.hit = False
        self.hit_timer = 0

    def update(self):
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.active = False
            return

        self.x += self.speed * self.direction

        center_limit = 60
        if self.direction < 0 and self.x < CENTER_X - center_limit:
            self.active = False
            return False
        elif self.direction > 0 and self.x > CENTER_X + center_limit:
            self.active = False
            return False

        return True

    def take_hit(self):
        self.hit = True
        self.hit_timer = 15

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        color = (150, 100, 100) if self.hit else COLOR_BRUTUS

        body_rect = pygame.Rect(self.x, self.y + 12, self.width, self.height - 12)
        pygame.draw.rect(surface, color, body_rect)

        head_rect = pygame.Rect(self.x + 3, self.y, 39, 16)
        pygame.draw.rect(surface, color, head_rect)

        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 12), int(self.y + 7)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 33), int(self.y + 7)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 12), int(self.y + 7)), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 33), int(self.y + 7)), 2)


class Projectile:
    def __init__(self, from_right=True):
        self.width = PROJECTILE_WIDTH
        self.height = PROJECTILE_HEIGHT

        if from_right:
            self.x = SCREEN_WIDTH + 5
            self.direction = -1
        else:
            self.x = -self.width - 5
            self.direction = 1

        self.y = CENTER_Y + random.randint(-30, 30)
        self.speed = PROJECTILE_SPEED
        self.active = True
        self.type = random.choice(['bottle', 'anchor'])

    def update(self):
        self.x += self.speed * self.direction

        center_limit = 50
        if self.direction < 0 and self.x < CENTER_X - center_limit:
            self.active = False
            return False
        elif self.direction > 0 and self.x > CENTER_X + center_limit:
            self.active = False
            return False

        return True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        if self.type == 'bottle':
            pygame.draw.rect(surface, (100, 150, 200), (self.x, self.y + 5, self.width, self.height - 10))
            pygame.draw.rect(surface, (200, 200, 200), (self.x + 5, self.y, self.width - 10, 5))
        else:
            pygame.draw.polygon(surface, COLOR_PROJECTILE, [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height),
                (self.x + self.width, self.y + self.height // 2)
            ])


class Spinach:
    def __init__(self):
        self.width = SPINACH_SIZE
        self.height = SPINACH_SIZE
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = -50
        self.speed = 3
        self.active = True
        self.timer = 0
        self.visible = False

    def update(self):
        if not self.visible:
            self.timer += 1
            if self.timer > 30:
                self.visible = True
        else:
            self.y += self.speed

            if self.y > SCREEN_HEIGHT:
                self.active = False

    def get_rect(self):
        if not self.visible:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        if not self.visible:
            return

        pygame.draw.rect(surface, COLOR_SPINACH, (self.x, self.y + 5, self.width, self.height - 5))
        pygame.draw.rect(surface, (0, 100, 0), (self.x + 5, self.y, self.width - 10, 8))


class OliveOyl:
    def __init__(self):
        self.x = CENTER_X - 15
        self.y = CENTER_Y - 50
        self.width = 30
        self.height = 40

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        body_rect = pygame.Rect(self.x, self.y + 12, self.width, self.height - 12)
        pygame.draw.rect(surface, COLOR_OLIVE, body_rect)

        head_rect = pygame.Rect(self.x + 3, self.y, 24, 14)
        pygame.draw.rect(surface, COLOR_OLIVE, head_rect)

        hair_rect = pygame.Rect(self.x + 2, self.y - 5, 26, 6)
        pygame.draw.rect(surface, (200, 150, 100), hair_rect)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Popeye Spinach Power Punch")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.projectiles = []
        self.spinach = None
        self.olive = OliveOyl()
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_rate = ENEMY_SPAWN_RATE_BASE
        self.spinach_spawn_timer = 0
        self.difficulty_timer = 0
        self.wave = 1

    def spawn_enemy(self):
        from_right = random.choice([True, False])
        self.enemies.append(Enemy(from_right))

    def spawn_projectile(self):
        from_right = random.choice([True, False])
        self.projectiles.append(Projectile(from_right))

    def update(self):
        if self.game_over:
            return

        self.player.update()

        self.difficulty_timer += 1
        if self.difficulty_timer > 600:
            self.difficulty_timer = 0
            self.spawn_rate = max(40, self.spawn_rate - 10)
            self.wave += 1

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            roll = random.random()
            if roll < 0.7:
                self.spawn_enemy()
            else:
                self.spawn_projectile()

        self.spinach_spawn_timer += 1
        if self.spinach_spawn_timer >= SPINACH_SPAWN_RATE and self.spinach is None:
            self.spinach_spawn_timer = 0
            self.spinach = Spinach()

        if self.spinach:
            self.spinach.update()
            if not self.spinach.active:
                self.spinach = None
            elif self.spinach.visible:
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                if self.spinach.get_rect().colliderect(player_rect):
                    self.player.activate_power()
                    self.player.score += 200
                    self.spinach = None

        for enemy in self.enemies[:]:
            reached_center = not enemy.update()

            if not enemy.active:
                self.enemies.remove(enemy)
                continue

            if reached_center and not enemy.hit:
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
                self.enemies.remove(enemy)
                continue

        for projectile in self.projectiles[:]:
            reached_center = not projectile.update()

            if not projectile.active:
                self.projectiles.remove(projectile)
                continue

            if reached_center:
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True
                self.projectiles.remove(projectile)
                continue

        punch_rect = self.player.get_punch_rect()
        if punch_rect:
            for enemy in self.enemies:
                if not enemy.hit and punch_rect.colliderect(enemy.get_rect()):
                    enemy.take_hit()
                    points = 200 if self.player.power_mode else 100
                    self.player.score += points

            for projectile in self.projectiles[:]:
                if punch_rect.colliderect(projectile.get_rect()):
                    points = 100 if self.player.power_mode else 50
                    self.player.score += points
                    self.projectiles.remove(projectile)

    def draw(self):
        self.screen.fill(COLOR_BG)

        pygame.draw.rect(self.screen, COLOR_FLOOR, (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))

        olive_rect = self.olive.get_rect()
        pygame.draw.rect(self.screen, (30, 30, 40), (olive_rect.x - 10, olive_rect.y - 10, olive_rect.width + 20, olive_rect.height + 20))

        self.olive.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.spinach:
            self.spinach.draw(self.screen)

        self.player.draw(self.screen)

        self.draw_hud()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (10, 35))

        wave_text = self.small_font.render(f"Wave: {self.wave}", True, COLOR_TEXT)
        self.screen.blit(wave_text, (10, 60))

        if self.player.power_mode:
            power_text = self.small_font.render("POWER MODE!", True, COLOR_POPEYE_POWER)
            self.screen.blit(power_text, (SCREEN_WIDTH // 2 - 50, 10))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_LEFT:
                        self.player.punch(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.player.punch(1)

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_input()
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
