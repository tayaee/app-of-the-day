"""
Vector Urban Champion: Street Brawl
A simplified 2D street fighting game focused on timing, spacing, and stamina management.
"""

import pygame
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_Y = 320
FPS = 60

# Colors
COLOR_BG = (30, 30, 40)
COLOR_GROUND = (50, 50, 60)
COLOR_PLAYER = (70, 150, 255)
COLOR_ENEMY = (255, 80, 80)
COLOR_HEALTH = (0, 200, 0)
COLOR_STAMINA = (200, 200, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_BLOCK = (100, 100, 200)

# Game constants
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 80
PUNCH_RANGE = 60
PUNCH_DAMAGE = 10
STAMINA_COST = 15
STAMINA_REGEN = 0.3
MAX_STAMINA = 100
MAX_HEALTH = 100
MOVE_SPEED = 4
PUNCH_DURATION = 15
BLOCK_DURATION = 0

# Action states
STATE_IDLE = "idle"
STATE_MOVE = "move"
STATE_PUNCH = "punch"
STATE_BLOCK = "block"


class Fighter:
    """Base fighter class with state management and combat logic."""

    def __init__(self, x, facing_right, color, is_ai=False):
        self.x = x
        self.y = GROUND_Y - PLAYER_HEIGHT
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = color
        self.facing_right = facing_right
        self.is_ai = is_ai

        self.health = MAX_HEALTH
        self.stamina = MAX_STAMINA

        self.state = STATE_IDLE
        self.action_timer = 0
        self.punch_type = None  # 'high' or 'low'
        self.block_type = None   # 'high' or 'low'

        # Hitboxes relative to position
        self.high_hitbox = pygame.Rect(0, 0, 20, 20)
        self.low_hitbox = pygame.Rect(0, 0, 20, 20)
        self.hurtbox = pygame.Rect(0, 0, self.width, self.height)

        self.update_hitboxes()

    def update_hitboxes(self):
        """Update hitbox positions based on current position."""
        # High punch hitbox (head level)
        punch_offset = PUNCH_RANGE if self.facing_right else -PUNCH_RANGE
        self.high_hitbox.x = self.x + self.width // 2 + punch_offset - 10
        self.high_hitbox.y = self.y + 10

        # Low punch hitbox (body level)
        self.low_hitbox.x = self.x + self.width // 2 + punch_offset - 10
        self.low_hitbox.y = self.y + 45

        # Main hurtbox
        self.hurtbox.x = self.x
        self.hurtbox.y = self.y

    def get_punch_rect(self):
        """Return the active punch hitbox."""
        if self.state == STATE_PUNCH and self.action_timer > 5:
            if self.punch_type == 'high':
                return self.high_hitbox
            else:
                return self.low_hitbox
        return None

    def is_blocking_high(self):
        """Check if blocking high attacks."""
        return self.state == STATE_BLOCK and self.block_type == 'high'

    def is_blocking_low(self):
        """Check if blocking low attacks."""
        return self.state == STATE_BLOCK and self.block_type == 'low'

    def take_damage(self, amount, attack_type):
        """Take damage if not blocking the correct direction."""
        if attack_type == 'high' and self.is_blocking_high():
            return False  # Blocked
        if attack_type == 'low' and self.is_blocking_low():
            return False  # Blocked

        self.health = max(0, self.health - amount)
        return True

    def move(self, dx):
        """Move horizontally, constrained to screen bounds."""
        if self.state == STATE_PUNCH:
            return  # Can't move while punching

        new_x = self.x + dx
        new_x = max(0, min(SCREEN_WIDTH - self.width, new_x))
        self.x = new_x

        if dx != 0:
            self.state = STATE_MOVE
            self.facing_right = dx > 0
        else:
            self.state = STATE_IDLE

        self.update_hitboxes()

    def punch(self, punch_type):
        """Start a punch attack."""
        if self.state == STATE_PUNCH:
            return False
        if self.stamina < STAMINA_COST:
            return False

        self.state = STATE_PUNCH
        self.punch_type = punch_type
        self.action_timer = PUNCH_DURATION
        self.stamina -= STAMINA_COST
        self.update_hitboxes()
        return True

    def block(self, block_type):
        """Start blocking."""
        if self.state == STATE_PUNCH:
            return False

        self.state = STATE_BLOCK
        self.block_type = block_type
        self.update_hitboxes()
        return True

    def stop_block(self):
        """Stop blocking."""
        if self.state == STATE_BLOCK:
            self.state = STATE_IDLE

    def update(self):
        """Update fighter state each frame."""
        # Regenerate stamina
        if self.state != STATE_PUNCH and self.stamina < MAX_STAMINA:
            self.stamina = min(MAX_STAMINA, self.stamina + STAMINA_REGEN)

        # Handle punch animation
        if self.state == STATE_PUNCH:
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.state = STATE_IDLE

    def draw(self, surface):
        """Draw the fighter."""
        # Body
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Draw block indicator
        if self.state == STATE_BLOCK:
            pygame.draw.rect(surface, COLOR_BLOCK, body_rect)
        else:
            pygame.draw.rect(surface, self.color, body_rect)

        # Draw direction indicator
        eye_x = self.x + 30 if self.facing_right else self.x + 10
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, self.y + 15), 5)

        # Draw punch indicator
        if self.state == STATE_PUNCH and self.action_timer > 5:
            punch_rect = self.get_punch_rect()
            if punch_rect:
                pygame.draw.rect(surface, (255, 255, 0), punch_rect)

        # Draw guard indicator
        if self.state == STATE_BLOCK:
            guard_y = self.y + 10 if self.block_type == 'high' else self.y + 50
            guard_rect = pygame.Rect(self.x - 5, guard_y, self.width + 10, 25)
            pygame.draw.rect(surface, (150, 150, 255), guard_rect, 3)


class AIController:
    """Simple AI opponent with reactive behavior."""

    def __init__(self, fighter):
        self.fighter = fighter
        self.decision_cooldown = 0
        self.reaction_delay = 15

    def update(self, player):
        """Update AI decision making."""
        self.decision_cooldown -= 1
        if self.decision_cooldown > 0:
            return

        self.decision_cooldown = self.reaction_delay

        # Calculate distance
        distance = abs(player.x - self.fighter.x)

        # Decision logic
        if distance > PUNCH_RANGE:
            # Move towards player
            if player.x < self.fighter.x:
                self.fighter.move(-MOVE_SPEED)
            else:
                self.fighter.move(MOVE_SPEED)
        else:
            # In combat range
            if player.state == STATE_PUNCH and self.fighter.stamina > 20:
                # Try to block incoming attack
                punch_type = player.punch_type
                self.fighter.block(punch_type)
            elif self.fighter.stamina >= STAMINA_COST and player.state != STATE_BLOCK:
                # Attack randomly
                import random
                punch_type = random.choice(['high', 'low'])
                self.fighter.punch(punch_type)
            else:
                self.fighter.stop_block()

        # Update facing direction
        self.fighter.facing_right = player.x > self.fighter.x


class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Urban Champion: Street Brawl")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)

        self.reset_game()

    def reset_game(self):
        """Reset the game state."""
        self.player = Fighter(100, True, COLOR_PLAYER)
        self.enemy = Fighter(600, False, COLOR_ENEMY, is_ai=True)
        self.ai = AIController(self.enemy)

        self.score = 0
        self.game_over = False
        self.winner = None

    def check_combat(self):
        """Check and resolve combat interactions."""
        # Player attacking enemy
        if self.player.state == STATE_PUNCH and self.player.action_timer == 8:
            punch_rect = self.player.get_punch_rect()
            if punch_rect and punch_rect.colliderect(self.enemy.hurtbox):
                if self.enemy.take_damage(PUNCH_DAMAGE, self.player.punch_type):
                    self.score += 100

        # Enemy attacking player
        if self.enemy.state == STATE_PUNCH and self.enemy.action_timer == 8:
            punch_rect = self.enemy.get_punch_rect()
            if punch_rect and punch_rect.colliderect(self.player.hurtbox):
                self.player.take_damage(PUNCH_DAMAGE, self.enemy.punch_type)

    def check_out_of_bounds(self):
        """Check if fighter is pushed out of bounds."""
        if self.player.x <= 0 or self.player.x >= SCREEN_WIDTH - self.player.width:
            self.game_over = True
            self.winner = "Enemy"

        if self.enemy.x <= 0 or self.enemy.x >= SCREEN_WIDTH - self.enemy.width:
            self.game_over = True
            self.winner = "Player"
            self.score += 500

    def check_knockout(self):
        """Check for KO condition."""
        if self.player.health <= 0:
            self.game_over = True
            self.winner = "Enemy"

        if self.enemy.health <= 0:
            self.game_over = True
            self.winner = "Player"

    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()

        # Movement
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            dx = MOVE_SPEED

        if dx != 0:
            self.player.move(dx)

        # Actions - only process once per press
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.punch('high')
                elif event.key == pygame.K_z:
                    self.player.punch('low')
                elif event.key == pygame.K_s:
                    self.player.block('high')
                elif event.key == pygame.K_x:
                    self.player.block('low')
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_s, pygame.K_x):
                    self.player.stop_block()

        return True

    def draw_ui(self):
        """Draw the user interface."""
        # Health bars
        pygame.draw.rect(self.screen, (100, 0, 0), (20, 20, 200, 20))
        player_health_width = (self.player.health / MAX_HEALTH) * 200
        pygame.draw.rect(self.screen, COLOR_HEALTH, (20, 20, player_health_width, 20))

        pygame.draw.rect(self.screen, (100, 0, 0), (SCREEN_WIDTH - 220, 20, 200, 20))
        enemy_health_width = (self.enemy.health / MAX_HEALTH) * 200
        pygame.draw.rect(self.screen, COLOR_HEALTH, (SCREEN_WIDTH - 220, 20, enemy_health_width, 20))

        # Stamina bars
        pygame.draw.rect(self.screen, (100, 100, 0), (20, 45, 200, 10))
        player_stamina_width = (self.player.stamina / MAX_STAMINA) * 200
        pygame.draw.rect(self.screen, COLOR_STAMINA, (20, 45, player_stamina_width, 10))

        pygame.draw.rect(self.screen, (100, 100, 0), (SCREEN_WIDTH - 220, 45, 200, 10))
        enemy_stamina_width = (self.enemy.stamina / MAX_STAMINA) * 200
        pygame.draw.rect(self.screen, COLOR_STAMINA, (SCREEN_WIDTH - 220, 45, enemy_stamina_width, 10))

        # Labels
        player_label = self.font.render("PLAYER", True, COLOR_TEXT)
        enemy_label = self.font.render("ENEMY", True, COLOR_TEXT)
        self.screen.blit(player_label, (20, 5))
        self.screen.blit(enemy_label, (SCREEN_WIDTH - 220, 5))

        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, 20))

        # Controls hint
        controls = "Arrows: Move | A: High Punch | Z: Low Punch | S: High Block | X: Low Block"
        controls_text = self.font.render(controls, True, (150, 150, 150))
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 25))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "Player":
            text = "YOU WIN!"
            color = (0, 255, 0)
        else:
            text = "YOU LOSE!"
            color = (255, 0, 0)

        game_over_text = self.big_font.render(text, True, color)
        restart_text = self.font.render("Press R to restart", True, COLOR_TEXT)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def run(self):
        """Main game loop."""
        running = True

        while running:
            # Handle input
            running = self.handle_input()

            if not self.game_over:
                # Update
                self.player.update()
                self.enemy.update()
                self.ai.update(self.player)

                # Check combat
                self.check_combat()

                # Check win conditions
                self.check_out_of_bounds()
                self.check_knockout()

            # Draw
            self.screen.fill(COLOR_BG)

            # Draw ground
            pygame.draw.rect(self.screen, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
            pygame.draw.line(self.screen, (80, 80, 90), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

            # Draw fighters
            self.player.draw(self.screen)
            self.enemy.draw(self.screen)

            # Draw UI
            self.draw_ui()

            # Draw game over if needed
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
