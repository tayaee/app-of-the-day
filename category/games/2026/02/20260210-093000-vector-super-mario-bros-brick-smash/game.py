import pygame
import sys
from entities import Player, Block, Coin
from config import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Brick Smash")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.player = Player(100, GROUND_Y - PLAYER_HEIGHT)
        self.blocks = []
        self.coins = []
        self.score = 0
        self.bricks_smashed = 0
        self.coins_collected = 0
        self.time_left = GAME_DURATION
        self.game_over = False
        self.start_ticks = pygame.time.get_ticks()
        self.create_level()

    def create_level(self):
        # Ground platforms at various heights
        self.platforms = []

        # Main ground
        self.platforms.append((0, GROUND_Y, SCREEN_WIDTH, 40))

        # Floating platforms for block placement
        self.platforms.append((100, 280, 200, 20))
        self.platforms.append((400, 280, 200, 20))
        self.platforms.append((250, 200, 150, 20))
        self.platforms.append((550, 200, 150, 20))
        self.platforms.append((100, 150, 120, 20))
        self.platforms.append((350, 120, 100, 20))
        self.platforms.append((550, 120, 150, 20))

        # Create blocks on platforms
        self.blocks = []

        # Row of bricks on first platform
        for i in range(4):
            self.blocks.append(Block(120 + i * 45, 240, "brick"))

        # Row of bricks on second platform
        for i in range(4):
            self.blocks.append(Block(420 + i * 45, 240, "brick"))

        # Mixed blocks on higher platforms
        for i in range(3):
            self.blocks.append(Block(270 + i * 45, 160, "brick" if i % 2 == 0 else "question"))

        for i in range(3):
            self.blocks.append(Block(570 + i * 45, 160, "question" if i % 2 == 0 else "brick"))

        # Top row blocks
        for i in range(2):
            self.blocks.append(Block(120 + i * 45, 110, "question"))

        self.blocks.append(Block(370, 80, "question"))
        self.blocks.append(Block(570, 80, "brick"))
        self.blocks.append(Block(615, 80, "question"))
        self.blocks.append(Block(660, 80, "brick"))

        # Some ground level bricks
        for i in range(3):
            self.blocks.append(Block(300 + i * 45, GROUND_Y - BLOCK_SIZE, "brick"))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.player.jump()

        # Continuous movement
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            elif keys[pygame.K_RIGHT]:
                self.player.move_right()
            else:
                self.player.stop_horizontal()

        return True

    def check_collisions(self):
        player_rect = self.player.get_rect()
        player_feet = self.player.get_feet_rect()
        player_head = self.player.get_head_rect()

        # Check platform collisions for landing
        self.player.on_ground = False
        for px, py, pw, ph in self.platforms:
            platform_rect = pygame.Rect(px, py, pw, ph)
            if player_feet.colliderect(platform_rect) and self.player.vel_y >= 0:
                if self.player.y + self.player.height <= py + ph:
                    self.player.y = py - self.player.height
                    self.player.vel_y = 0
                    self.player.on_ground = True

        # Keep player on ground level
        if self.player.y + self.player.height >= GROUND_Y:
            self.player.y = GROUND_Y - self.player.height
            self.player.vel_y = 0
            self.player.on_ground = True

        # Check block collisions
        for block in self.blocks[:]:
            if not block.alive:
                self.blocks.remove(block)
                continue

            block_rect = block.get_rect()

            # Check if player head hits block from below
            if player_head.colliderect(block_rect) and self.player.vel_y < 0:
                result = block.hit()
                if result == "smash":
                    self.score += 10
                    self.bricks_smashed += 1
                elif result == "coin":
                    self.score += 50
                    self.coins_collected += 1
                    self.coins.append(Coin(block.x + block.width // 2, block.y))

                # Bounce player down
                self.player.vel_y = 0

            # Check if player lands on top of block
            if player_feet.colliderect(block_rect) and self.player.vel_y >= 0:
                if self.player.y + self.player.height <= block.y + 10:
                    self.player.y = block.y - self.player.height
                    self.player.vel_y = 0
                    self.player.on_ground = True

    def update(self):
        if self.game_over:
            return

        # Update timer
        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        self.time_left = max(0, GAME_DURATION - elapsed)

        if self.time_left <= 0:
            self.game_over = True

        # Update player
        self.player.update()

        # Update blocks
        for block in self.blocks:
            block.update()

        # Update coins
        for coin in self.coins[:]:
            if not coin.update():
                self.coins.remove(coin)

        # Check collisions
        self.check_collisions()

        # Keep player in bounds horizontally
        if self.player.x < 0:
            self.player.x = 0
        elif self.player.x > SCREEN_WIDTH - self.player.width:
            self.player.x = SCREEN_WIDTH - self.player.width

    def draw(self):
        # Draw sky background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw platforms
        for px, py, pw, ph in self.platforms:
            pygame.draw.rect(self.screen, PLATFORM_COLOR, (px, py, pw, ph))
            pygame.draw.rect(self.screen, (0, 0, 0), (px, py, pw, ph), 2)

        # Draw ground pattern
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (0, 100, 0), (i, GROUND_Y), (i + 20, GROUND_Y + 40), 1)

        # Draw blocks
        for block in self.blocks:
            block.draw(self.screen)

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, SCORE_COLOR)
        self.screen.blit(score_text, (10, 10))

        # Timer color changes when low
        timer_color = (255, 0, 0) if self.time_left < 10 else TIMER_COLOR
        timer_text = self.font.render(f"Time: {int(self.time_left)}", True, timer_color)
        self.screen.blit(timer_text, (SCREEN_WIDTH - 120, 10))

        # Stats
        bricks_text = self.small_font.render(f"Bricks: {self.bricks_smashed}", True, TEXT_COLOR)
        coins_text = self.small_font.render(f"Coins: {self.coins_collected}", True, TEXT_COLOR)
        self.screen.blit(bricks_text, (10, 50))
        self.screen.blit(coins_text, (120, 50))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("TIME'S UP!", True, (255, 255, 0))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            stats_text = self.small_font.render(f"Bricks Smashed: {self.bricks_smashed} | Coins: {self.coins_collected}", True, TEXT_COLOR)
            restart_text = self.small_font.render("Press SPACE or R to restart", True, (200, 200, 200))

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
