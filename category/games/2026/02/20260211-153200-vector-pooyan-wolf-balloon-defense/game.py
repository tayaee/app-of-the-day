"""Main game loop and rendering."""

import pygame
import random
from config import *
from entities import Player, Arrow, Wolf


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Pooyan: Wolf Balloon Defense")
        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player()
        self.arrows = []
        self.wolves = []
        self.wolves_on_ledge = []

        self.score = 0
        self.game_state = "ready"  # ready, playing, game_over
        self.last_wolf_spawn = 0
        self.spawn_timer = 0

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)
        self.info_font = pygame.font.Font(None, INFO_FONT_SIZE)

    def reset_game(self):
        """Reset game to initial state."""
        self.player = Player()
        self.arrows = []
        self.wolves = []
        self.wolves_on_ledge = []
        self.score = 0
        self.game_state = "ready"
        self.last_wolf_spawn = 0
        self.spawn_timer = 0

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.handle_action()
                elif event.key == pygame.K_UP:
                    if self.game_state == "playing":
                        self.player.moving_up = True
                elif event.key == pygame.K_DOWN:
                    if self.game_state == "playing":
                        self.player.moving_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.moving_up = False
                elif event.key == pygame.K_DOWN:
                    self.player.moving_down = False

    def handle_action(self):
        """Handle shoot/restart action."""
        if self.game_state == "ready":
            self.game_state = "playing"
        elif self.game_state == "playing":
            self.shoot_arrow()
        elif self.game_state == "game_over":
            self.reset_game()

    def shoot_arrow(self):
        """Fire an arrow if under the limit."""
        active_arrows = [a for a in self.arrows if a.active]
        if len(active_arrows) < MAX_ARROWS:
            arrow = Arrow(self.player.x - 30, self.player.get_center_y())
            self.arrows.append(arrow)

    def spawn_wolf(self, current_time):
        """Spawn a new wolf at intervals."""
        if current_time - self.last_wolf_spawn > WOLF_SPAWN_INTERVAL:
            self.last_wolf_spawn = current_time
            # 30% chance for shielded wolf
            shielded = random.random() < 0.3
            self.wolves.append(Wolf(shielded=shielded))

    def update(self):
        """Update game state."""
        if self.game_state == "playing":
            current_time = pygame.time.get_ticks()

            self.player.update()
            self.spawn_wolf(current_time)

            # Update arrows
            for arrow in self.arrows:
                arrow.update()
            self.arrows = [a for a in self.arrows if a.active]

            # Update wolves
            for wolf in self.wolves:
                wolf.update()

            # Check arrow-balloon collisions
            for arrow in self.arrows:
                if not arrow.active:
                    continue
                arrow_rect = arrow.get_rect()
                for wolf in self.wolves:
                    if not wolf.active:
                        continue
                    balloon_rects = wolf.get_balloon_rects()
                    for i, balloon_rect in enumerate(balloon_rects):
                        if arrow_rect.colliderect(balloon_rect):
                            arrow.active = False
                            wolf.hit()
                            if not wolf.active:
                                # Wolf defeated
                                if wolf.shielded:
                                    self.score += SCORE_SHIELDED_WOLF
                                else:
                                    self.score += SCORE_REGULAR_WOLF
                            break

            # Remove inactive wolves and handle ledge arrivals
            for wolf in self.wolves[:]:
                if not wolf.active and wolf.reached_ledge:
                    self.wolves.remove(wolf)
                    if len(self.wolves_on_ledge) < LEDGE_SLOTS:
                        self.wolves_on_ledge.append(wolf)
                        self.score = max(0, self.score - PENALTY_WOLF_REACHED_LEDGE)
                elif not wolf.active:
                    self.wolves.remove(wolf)

            # Check game over
            if len(self.wolves_on_ledge) >= LEDGE_SLOTS:
                self.game_state = "game_over"

    def render(self):
        """Render the game."""
        self.screen.fill(SKY_BLUE)

        # Draw ledge
        ledge_rect = pygame.Rect(50, LEDGE_Y, SCREEN_WIDTH - 100, 25)
        pygame.draw.rect(self.screen, LEDGE_COLOR, ledge_rect)
        pygame.draw.rect(self.screen, (101, 67, 33), ledge_rect, 3)

        # Draw grass on ledge
        pygame.draw.rect(self.screen, GRASS_COLOR, (50, LEDGE_Y - 5, SCREEN_WIDTH - 100, 10))

        # Draw wolves on ledge
        slot_start_x = 70
        for i, wolf in enumerate(self.wolves_on_ledge):
            slot_x = slot_start_x + (i % LEDGE_SLOTS) * SLOT_WIDTH
            # Draw wolf silhouette on ledge
            wolf_x = slot_x + SLOT_WIDTH // 2
            pygame.draw.ellipse(self.screen, WOLF_COLOR,
                              (wolf_x - 15, LEDGE_Y - 20, 30, 25))
            # Ears
            pygame.draw.polygon(self.screen, WOLF_COLOR, [
                (wolf_x - 10, LEDGE_Y - 18),
                (wolf_x - 15, LEDGE_Y - 30),
                (wolf_x - 5, LEDGE_Y - 20)
            ])
            pygame.draw.polygon(self.screen, WOLF_COLOR, [
                (wolf_x + 10, LEDGE_Y - 18),
                (wolf_x + 15, LEDGE_Y - 30),
                (wolf_x + 5, LEDGE_Y - 20)
            ])

        # Draw active wolves
        for wolf in self.wolves:
            wolf.draw(self.screen)

        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw score
        score_text = self.score_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 20))

        # Draw ledge indicator
        ledge_text = self.info_font.render(
            f"Wolves on ledge: {len(self.wolves_on_ledge)}/{LEDGE_SLOTS}",
            True, (200, 50, 50)
        )
        self.screen.blit(ledge_text, (20, 60))

        # Draw messages
        if self.game_state == "ready":
            msg = "Defend the piglet base from wolves!"
            msg_text = self.message_font.render(msg, True, BLACK)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(msg_text, msg_rect)

            msg2 = "Press SPACE to start"
            msg2_text = self.message_font.render(msg2, True, (50, 50, 50))
            msg2_rect = msg2_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(msg2_text, msg2_rect)

            controls = "UP/DOWN: Move | SPACE: Fire"
            controls_text = self.info_font.render(controls, True, (80, 80, 80))
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(controls_text, controls_rect)

        elif self.game_state == "game_over":
            msg = "GAME OVER!"
            msg_text = self.score_font.render(msg, True, (200, 50, 50))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(msg_text, msg_rect)

            final_score = f"Final Score: {self.score}"
            score_text = self.message_font.render(final_score, True, BLACK)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_text, score_rect)

            msg2 = "Press SPACE to restart"
            msg2_text = self.info_font.render(msg2, True, (80, 80, 80))
            msg2_rect = msg2_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(msg2_text, msg2_rect)

        pygame.display.flip()

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0 = stay, 1 = move up, 2 = move down, 3 = shoot

        Returns:
            (observation, reward, done)
        """
        prev_score = self.score
        prev_wolves_on_ledge = len(self.wolves_on_ledge)

        # Reset movement
        self.player.moving_up = False
        self.player.moving_down = False

        if action == 1:
            self.player.moving_up = True
        elif action == 2:
            self.player.moving_down = False
        elif action == 3:
            self.shoot_arrow()

        self.update()

        reward = 0
        done = False

        if self.game_state == "playing":
            reward += REWARD_PER_FRAME
            reward += (self.score - prev_score) / 100.0

            if len(self.wolves_on_ledge) > prev_wolves_on_ledge:
                reward += REWARD_WOLF_LEDGE
        elif self.game_state == "game_over":
            reward = REWARD_GAME_OVER
            done = True

        return self.get_observation(), reward, done

    def get_observation(self):
        """Return current game state for AI."""
        wolf_data = []
        for wolf in self.wolves:
            wolf_data.append({
                "x": wolf.x,
                "y": wolf.y,
                "shielded": wolf.shielded,
                "balloons_popped": wolf.balloons_popped
            })

        arrow_data = []
        for arrow in self.arrows:
            if arrow.active:
                arrow_data.append({"x": arrow.x, "y": arrow.y})

        obs = {
            "player_y": self.player.y,
            "wolves": wolf_data,
            "arrows": arrow_data,
            "wolves_on_ledge": len(self.wolves_on_ledge),
            "score": self.score,
            "game_state": self.game_state
        }
        return obs

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
