import pygame
import random
from entities import Player, Platform, Ladder, Obstacle, Elevator
from config import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Mario Bros Platform Climb")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        start_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        start_y = SCREEN_HEIGHT - 60
        self.player = Player(start_x, start_y)
        self.score = 0
        self.game_over = False
        self.won = False
        self.obstacles = []
        self.elevators = []
        self.current_tier_speed = BASE_OBSTACLE_SPEED
        self.tiers = self.create_tiers()

    def create_tiers(self):
        tiers = []
        for i in range(NUM_TIERS):
            y = SCREEN_HEIGHT - 60 - (i + 1) * TIER_HEIGHT

            platforms = []
            main_plat_x = (SCREEN_WIDTH - PLATFORM_WIDTH) // 2
            platforms.append(Platform(main_plat_x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

            ladders = []
            ladder_x = main_plat_x + PLATFORM_WIDTH // 2 - LADDER_WIDTH // 2
            if i < NUM_TIERS - 1:
                ladders.append(Ladder(ladder_x, y - TIER_HEIGHT, LADDER_WIDTH, TIER_HEIGHT))

            tiers.append({
                'y': y,
                'platforms': platforms,
                'ladders': ladders,
                'num': i + 1
            })

            if i == 2:
                elev_y = y - TIER_HEIGHT // 2
                self.elevators.append(Elevator(100, elev_y, elev_y - 60, 80, 16))

        return tiers

    def spawn_obstacle(self):
        if not self.obstacles or random.random() < 0.02:
            tier = random.randint(0, NUM_TIERS - 1)
            tier_y = self.tiers[tier]['y'] - 20
            direction = random.choice([-1, 1])
            speed = self.current_tier_speed * (1 + tier * 0.1)
            x = 0 if direction > 0 else SCREEN_WIDTH
            self.obstacles.append(Obstacle(x, tier_y, tier, speed * direction))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if not self.game_over and not self.won:
            if keys[pygame.K_LEFT]:
                self.player.move(-PLAYER_SPEED, 0)
            if keys[pygame.K_RIGHT]:
                self.player.move(PLAYER_SPEED, 0)

            if self.player.climbing:
                if keys[pygame.K_UP]:
                    self.player.move(0, -PLAYER_SPEED)
                if keys[pygame.K_DOWN]:
                    self.player.move(0, PLAYER_SPEED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_UP and self.can_climb():
                        self.player.climbing = True
                if event.key == pygame.K_UP and not self.can_climb():
                    self.player.climbing = False

        return True

    def can_climb(self):
        player_rect = self.player.get_rect()
        for tier in self.tiers:
            for ladder in tier['ladders']:
                if player_rect.colliderect(ladder.get_rect()):
                    return True
        return False

    def update(self):
        if self.game_over or self.won:
            return

        self.spawn_obstacle()

        if not self.player.climbing:
            self.player.vel_y += GRAVITY
            self.player.y += self.player.vel_y
        else:
            self.player.vel_y = 0

        self.player.x = max(0, min(SCREEN_WIDTH - self.player.width, self.player.x))

        if not self.player.climbing:
            self.player.on_ground = False
            player_rect = self.player.get_rect()

            for tier in self.tiers:
                for platform in tier['platforms']:
                    if player_rect.colliderect(platform.get_rect()):
                        if self.player.vel_y > 0:
                            self.player.y = platform.y - self.player.height
                            self.player.vel_y = 0
                            self.player.on_ground = True

            for elev in self.elevators:
                if player_rect.colliderect(elev.get_rect()):
                    if self.player.vel_y > 0:
                        self.player.y = elev.y - self.player.height
                        self.player.vel_y = 0
                        self.player.on_ground = True
                        self.player.y += elev.speed * (-1 if elev.moving_up else 1)

        player_rect = self.player.get_rect()

        for tier in self.tiers:
            tier_y = tier['y']
            if self.player.y < tier_y and tier['num'] not in self.player.tier_reached:
                self.player.tier_reached.add(tier['num'])
                self.score += TIER_SCORE
                self.current_tier_speed += OBSTACLE_SPEED_INCREMENT

        goal_y = self.tiers[-1]['y'] - TIER_HEIGHT
        if self.player.y < goal_y + 20:
            self.won = True
            self.score += GOAL_SCORE

        if self.player.y > SCREEN_HEIGHT:
            self.game_over = True

        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.is_off_screen(SCREEN_WIDTH):
                self.obstacles.remove(obstacle)
            elif player_rect.colliderect(obstacle.get_rect()):
                self.game_over = True

        for elev in self.elevators:
            elev.update()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        for tier in self.tiers:
            for ladder in tier['ladders']:
                ladder.draw(self.screen)

        for elev in self.elevators:
            elev.draw(self.screen)

        for tier in self.tiers:
            for platform in tier['platforms']:
                platform.draw(self.screen)

        goal_y = self.tiers[-1]['y'] - TIER_HEIGHT
        pygame.draw.rect(self.screen, GOAL_COLOR,
                        (0, goal_y, SCREEN_WIDTH, 40))
        goal_text = self.small_font.render("GOAL - 1000 PTS", True, (50, 50, 50))
        self.screen.blit(goal_text, (SCREEN_WIDTH // 2 - 80, goal_y + 8))

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        self.player.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        tier_text = self.font.render(f"Tier: {len(self.player.tier_reached)}/{NUM_TIERS}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(tier_text, (10, 50))

        controls = self.small_font.render("Arrows: Move/Jump on Ladder | SPACE: Jump", True, (150, 150, 150))
        self.screen.blit(controls, (10, SCREEN_HEIGHT - 30))

        if self.game_over:
            msg = self.font.render("GAME OVER! Press SPACE to restart", True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2))
        elif self.won:
            msg = self.font.render("GOAL REACHED! Score: " + str(self.score), True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
            sub = self.small_font.render("Press SPACE to play again", True, TEXT_COLOR)
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
