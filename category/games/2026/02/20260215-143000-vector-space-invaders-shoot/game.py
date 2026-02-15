import pygame
import random
from entities import Player, Bullet, Alien, Bunker, Particle
from config import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Space Invaders Shoot")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        player_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        player_y = SCREEN_HEIGHT - 50
        self.player = Player(player_x, player_y)
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.won = False
        self.bullets = []
        self.alien_bullets = []
        self.aliens = []
        self.bunkers = []
        self.particles = []
        self.alien_direction = 1
        self.alien_speed = ALIEN_MOVE_SPEED_START
        self.alien_move_timer = 0
        self.alien_move_delay = 30
        self.create_aliens()
        self.create_bunkers()

    def create_aliens(self):
        self.aliens = []
        total_width = ALIEN_COLS * (ALIEN_WIDTH + ALIEN_PADDING) - ALIEN_PADDING
        start_x = (SCREEN_WIDTH - total_width) // 2

        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                x = start_x + col * (ALIEN_WIDTH + ALIEN_PADDING)
                y = ALIEN_START_Y + row * (ALIEN_HEIGHT + ALIEN_PADDING)
                self.aliens.append(Alien(x, y, row))

    def create_bunkers(self):
        self.bunkers = []
        spacing = SCREEN_WIDTH // (NUM_BUNKERS + 1)
        for i in range(NUM_BUNKERS):
            x = spacing * (i + 1) - BUNKER_WIDTH // 2
            y = SCREEN_HEIGHT - 150
            self.bunkers.append(Bunker(x, y))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if not self.game_over and not self.won and self.player.alive:
            if keys[pygame.K_LEFT]:
                self.player.move(-self.player.speed)
            if keys[pygame.K_RIGHT]:
                self.player.move(self.player.speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                elif self.player.alive:
                    if event.key == pygame.K_SPACE:
                        self.shoot()

        return True

    def shoot(self):
        bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
        bullet_y = self.player.y - BULLET_HEIGHT
        self.bullets.append(Bullet(bullet_x, bullet_y, PLAYER_BULLET_SPEED))

    def alien_shoot(self):
        if random.random() < ALIEN_SHOOT_CHANCE * (1 + self.level * 0.2):
            bottom_aliens = self.get_bottom_aliens()
            if bottom_aliens:
                alien = random.choice(bottom_aliens)
                bullet_x = alien.x + alien.width // 2 - BULLET_WIDTH // 2
                bullet_y = alien.y + alien.height
                self.alien_bullets.append(Bullet(bullet_x, bullet_y, ALIEN_BULLET_SPEED, (255, 100, 100)))

    def get_bottom_aliens(self):
        bottom_by_col = {}
        for alien in self.aliens:
            if alien.alive:
                col = alien.x // (ALIEN_WIDTH + ALIEN_PADDING)
                if col not in bottom_by_col or alien.y > bottom_by_col[col].y:
                    bottom_by_col[col] = alien
        return list(bottom_by_col.values())

    def update(self):
        if self.game_over or self.won:
            return

        if not self.player.alive:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                player_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
                self.player = Player(player_x, SCREEN_HEIGHT - 50)
            return

        self.alien_shoot()

        self.alien_move_timer += 1
        if self.alien_move_timer >= self.alien_move_delay:
            self.alien_move_timer = 0
            self.move_aliens()

        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            bullet_rect = bullet.get_rect()

            for alien in self.aliens:
                if alien.alive and bullet_rect.colliderect(alien.get_rect()):
                    alien.alive = False
                    bullet.active = False
                    self.score += alien.get_points()
                    self.create_explosion(alien.x + alien.width // 2, alien.y + alien.height // 2, alien.color)
                    break

            for bunker in self.bunkers:
                if bunker.health > 0 and bullet_rect.colliderect(bunker.get_rect()):
                    bullet.active = False
                    break

            if not bullet.active:
                self.bullets.remove(bullet)

        for bullet in self.alien_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.alien_bullets.remove(bullet)
                continue

            bullet_rect = bullet.get_rect()

            if bullet_rect.colliderect(self.player.get_rect()):
                self.player.alive = False
                bullet.active = False
                self.create_explosion(self.player.x + self.player.width // 2, self.player.y + self.player.height // 2, PLAYER_COLOR)
                self.alien_bullets.remove(bullet)
                continue

            for bunker in self.bunkers:
                if bunker.health > 0 and bullet_rect.colliderect(bunker.get_rect()):
                    if bunker.hit():
                        self.create_explosion(bunker.x + bunker.width // 2, bunker.y + bunker.height // 2, BUNKER_COLOR)
                    bullet.active = False
                    break

            if not bullet.active:
                self.alien_bullets.remove(bullet)

        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        alive_aliens = [a for a in self.aliens if a.alive]
        if not alive_aliens:
            self.level += 1
            self.alien_speed += 0.5
            self.alien_move_delay = max(5, 30 - self.level * 2)
            self.create_aliens()

        for alien in alive_aliens:
            if alien.y + alien.height >= self.player.y:
                self.game_over = True

    def move_aliens(self):
        should_move_down = False
        should_reverse = False

        for alien in self.aliens:
            if not alien.alive:
                continue
            new_x = alien.x + self.alien_direction * self.alien_speed * 10
            if new_x <= 0 or new_x + alien.width >= SCREEN_WIDTH:
                should_reverse = True
                should_move_down = True
                break

        if should_reverse:
            self.alien_direction *= -1

        for alien in self.aliens:
            if alien.alive:
                if should_move_down:
                    alien.y += ALIEN_DROP_DISTANCE
                else:
                    alien.x += self.alien_direction * self.alien_speed * 10

                if alien.y + alien.height >= self.player.y:
                    self.game_over = True

    def create_explosion(self, x, y, color):
        for _ in range(10):
            self.particles.append(Particle(x, y, color))

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        for bunker in self.bunkers:
            if bunker.health > 0:
                bunker.draw(self.screen)

        for alien in self.aliens:
            alien.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for bullet in self.alien_bullets:
            bullet.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        if self.player.alive:
            self.player.draw(self.screen)

        score_text = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        level_text = self.font.render(f"LEVEL: {self.level}", True, TEXT_COLOR)
        lives_text = self.font.render(f"LIVES: {self.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

        controls = self.small_font.render("Arrow Keys: Move | SPACE: Shoot", True, (150, 150, 150))
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 30))

        if self.game_over:
            msg = self.font.render("GAME OVER! Press SPACE to restart", True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2))
        elif self.won:
            msg = self.font.render("YOU WIN! Score: " + str(self.score), True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
