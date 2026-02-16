"""
Main game logic for Vector Donkey Kong Jr Climb
"""

import pygame
import random
import sys
from entities import Player, Vine, Platform, Snapjaw, Bird, Fruit, Key, Cage
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_TEXT,
    NUM_VINES, VINE_SPACING, VINE_START_X, VINE_TOP_Y, VINE_BOTTOM_Y,
    NUM_SNAPJAWS, SNAPJAW_SPEED, NUM_BIRDS, BIRD_SPAWN_INTERVAL,
    NUM_PLATFORMS, PLATFORM_HEIGHT, MAX_FRUITS,
    REWARD_ENEMY_AVOIDANCE, REWARD_CLIMB_PROGRESS, REWARD_FRUIT_DROP_HIT,
    REWARD_KEY_COLLECT, PENALTY_COLLISION
)


class Game:
    """Main game class handling the game loop and state."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Donkey Kong Jr Climb")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

        self.reset_game()

    def reset_game(self):
        """Reset all game state to initial values."""
        self.player = Player()
        self.vines = []
        self.platforms = []
        self.snapjaws = []
        self.birds = []
        self.fruits = []
        self.keys = []
        self.cages = []
        self.game_over = False
        self.victory = False
        self.level = 1
        self.bird_spawn_timer = 0
        self.bird_spawn_interval = BIRD_SPAWN_INTERVAL
        self.last_player_y = self.player.y
        self.climb_progress = 0

        self.create_level()

    def create_level(self):
        """Create the level layout with vines, platforms, enemies, and objectives."""
        self.vines.clear()
        self.platforms.clear()
        self.snapjaws.clear()
        self.birds.clear()
        self.fruits.clear()
        self.keys.clear()
        self.cages.clear()

        # Create vines
        for i in range(NUM_VINES):
            x = VINE_START_X + i * VINE_SPACING
            self.vines.append(Vine(x))

        # Create platforms at intervals
        for i in range(NUM_PLATFORMS):
            y = VINE_TOP_Y + 100 + i * (VINE_BOTTOM_Y - VINE_TOP_Y) // (NUM_PLATFORMS + 1)
            width = 300
            self.platforms.append(Platform(y, width))

        # Create keys at top corners
        self.keys.append(Key(50, VINE_TOP_Y - 40))
        self.keys.append(Key(SCREEN_WIDTH - 75, VINE_TOP_Y - 40))

        # Create cage in center at top
        self.cages.append(Cage(SCREEN_WIDTH // 2 - 30, VINE_TOP_Y - 50))

        # Create snapjaws on random vines
        num_snapjaws = min(NUM_SNAPJAWS, len(self.vines))
        vine_indices = random.sample(range(len(self.vines)), num_snapjaws)
        for i, vine_idx in enumerate(vine_indices):
            vine = self.vines[vine_idx]
            start_y = vine.y_bottom - 50 - i * 100
            direction = 1 if i % 2 == 0 else -1
            self.snapjaws.append(Snapjaw(vine, start_y, direction))

        # Spawn some collectible fruits on vines
        for _ in range(MAX_FRUITS):
            vine = random.choice(self.vines)
            fruit_y = random.randint(vine.y_top + 50, vine.y_bottom - 50)
            fruit = Fruit(vine.x, fruit_y)
            fruit.speed = 0  # Stationary collectible
            self.fruits.append(fruit)

    def spawn_bird(self):
        """Spawn a bird flying across the screen."""
        y = random.randint(VINE_TOP_Y + 50, VINE_BOTTOM_Y - 100)
        direction = random.choice([1, -1])
        self.birds.append(Bird(y, direction))

    def check_collisions(self):
        """Check all collision interactions."""
        if not self.player.alive:
            return

        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)

        # Check snapjaw collisions
        for snapjaw in self.snapjaws:
            if snapjaw.get_rect().colliderect(player_rect):
                self.player.alive = False
                self.player.score += PENALTY_COLLISION

        # Check bird collisions
        for bird in self.birds:
            if bird.get_rect().colliderect(player_rect):
                self.player.alive = False
                self.player.score += PENALTY_COLLISION

        # Check fruit collection
        for fruit in self.fruits[:]:
            if fruit.active and fruit.get_rect().colliderect(player_rect):
                fruit.active = False
                self.player.fruits_collected += 1
                self.player.score += 10

        # Check dropped fruit hitting enemies
        for fruit in self.fruits[:]:
            if fruit.active and fruit.speed > 0:  # Only dropped fruits
                fruit_rect = fruit.get_rect()

                # Check against snapjaws
                for snapjaw in self.snapjaws[:]:
                    if snapjaw.active and snapjaw.get_rect().colliderect(fruit_rect):
                        snapjaw.active = False
                        fruit.active = False
                        self.player.score += REWARD_FRUIT_DROP_HIT

                # Check against birds
                for bird in self.birds[:]:
                    if bird.active and bird.get_rect().colliderect(fruit_rect):
                        bird.active = False
                        fruit.active = False
                        self.player.score += REWARD_FRUIT_DROP_HIT

        # Check key collection
        keys_collected = 0
        for key in self.keys:
            if not key.collected and key.get_rect().colliderect(player_rect):
                key.collected = True
                self.player.score += REWARD_KEY_COLLECT
            if key.collected:
                keys_collected += 1

        # Check victory condition (all keys collected)
        if keys_collected >= len(self.keys):
            self.victory = True
            for cage in self.cages:
                cage.locked = False

    def update(self):
        """Update all game objects."""
        if self.game_over or self.victory:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.vines, self.platforms)

        # Track climbing progress
        if self.player.y < self.last_player_y:
            progress = (self.last_player_y - self.player.y) // 10
            self.player.score += progress * REWARD_CLIMB_PROGRESS // 10
        self.last_player_y = self.player.y

        # Update snapjaws
        for snapjaw in self.snapjaws:
            snapjaw.update()

        # Update birds
        for bird in self.birds:
            bird.update()

        # Remove inactive birds
        self.birds = [b for b in self.birds if b.active]

        # Spawn birds
        self.bird_spawn_timer += 1
        spawn_interval = max(180, self.bird_spawn_interval - self.level * 20)
        if self.bird_spawn_timer >= spawn_interval:
            if len(self.birds) < NUM_BIRDS + self.level:
                self.spawn_bird()
            self.bird_spawn_timer = 0

        # Update fruits
        for fruit in self.fruits:
            fruit.update()

        # Remove inactive fruits
        self.fruits = [f for f in self.fruits if f.active]

        # Check collisions
        self.check_collisions()

        # Check game over
        if not self.player.alive:
            self.game_over = True

    def draw(self):
        """Render the game to the screen."""
        self.screen.fill(COLOR_BG)

        # Draw vines
        for vine in self.vines:
            vine.draw(self.screen)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw keys
        for key in self.keys:
            key.draw(self.screen)

        # Draw cage
        for cage in self.cages:
            cage.draw(self.screen)

        # Draw snapjaws
        for snapjaw in self.snapjaws:
            snapjaw.draw(self.screen)

        # Draw birds
        for bird in self.birds:
            bird.draw(self.screen)

        # Draw fruits
        for fruit in self.fruits:
            fruit.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over/victory screen
        if self.game_over:
            self.draw_message("GAME OVER", f"Score: {self.player.score} - Press R to restart")
        elif self.victory:
            self.draw_message("VICTORY!", f"Score: {self.player.score} - Press R for next level")

        pygame.display.flip()

    def draw_hud(self):
        """Draw the heads-up display."""
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (10, 35))

        # Fruits
        fruit_text = self.small_font.render(f"Fruits: {self.player.fruits_collected}", True, COLOR_TEXT)
        self.screen.blit(fruit_text, (10, 60))

        # Keys
        keys_collected = sum(1 for k in self.keys if k.collected)
        keys_text = self.small_font.render(f"Keys: {keys_collected}/{len(self.keys)}", True, COLOR_TEXT)
        self.screen.blit(keys_text, (10, 85))

        # Instructions
        if self.player.on_vines and len(self.player.on_vines) >= 2:
            hint_text = self.tiny_font.render("DOUBLE VINE CLIMBING!", True, (255, 255, 0))
            self.screen.blit(hint_text, (SCREEN_WIDTH - 140, 10))

        if self.player.fruits_collected > 0:
            fruit_hint = self.tiny_font.render("SPACE to drop fruit", True, (200, 200, 200))
            self.screen.blit(fruit_hint, (SCREEN_WIDTH - 160, 30))

    def draw_message(self, title, subtitle):
        """Draw a centered message overlay."""
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
        """Advance to the next level with increased difficulty."""
        self.level += 1
        self.player.x = 50
        self.player.y = SCREEN_HEIGHT - 80
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.fruits_collected = 0
        self.bird_spawn_timer = 0
        self.victory = False
        self.create_level()

    def run(self):
        """Main game loop."""
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
                    elif event.key == pygame.K_SPACE:
                        # Drop fruit
                        dropped_fruit = self.player.drop_fruit()
                        if dropped_fruit:
                            self.fruits.append(dropped_fruit)

            # Update
            self.update()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
