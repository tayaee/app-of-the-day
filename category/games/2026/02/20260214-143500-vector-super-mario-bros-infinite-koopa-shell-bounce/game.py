"""Main game logic for Infinite Koopa Shell Bounce."""

import pygame
import config as cfg


class Player:
    """Player character (Mario-style)."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = cfg.PLAYER_WIDTH
        self.height = cfg.PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.alive = True
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move_left(self):
        self.vel_x = -cfg.PLAYER_SPEED

    def move_right(self):
        self.vel_x = cfg.PLAYER_SPEED

    def stop_horizontal(self):
        self.vel_x = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -cfg.PLAYER_JUMP_POWER
            self.on_ground = False

    def update(self):
        # Apply gravity
        self.vel_y += cfg.GRAVITY
        if self.vel_y > cfg.PLAYER_MAX_FALL_SPEED:
            self.vel_y = cfg.PLAYER_MAX_FALL_SPEED

        # Apply friction
        self.vel_x *= cfg.FRICTION

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Platform collision
        if self.y + self.height >= cfg.PLATFORM_Y_LEVEL:
            self.y = cfg.PLATFORM_Y_LEVEL - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > cfg.SCREEN_WIDTH:
            self.x = cfg.SCREEN_WIDTH - self.width

        # Fall off screen
        if self.y > cfg.SCREEN_HEIGHT:
            self.alive = False

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface):
        # Body (red)
        body_rect = pygame.Rect(
            int(self.x + 4), int(self.y + 8),
            self.width - 8, self.height - 12
        )
        pygame.draw.rect(surface, cfg.RED, body_rect)

        # Head (skin color)
        head_rect = pygame.Rect(
            int(self.x + 6), int(self.y),
            self.width - 12, 12
        )
        pygame.draw.rect(surface, (255, 200, 180), head_rect)

        # Hat (red)
        hat_rect = pygame.Rect(
            int(self.x + 4), int(self.y - 4),
            self.width - 8, 8
        )
        pygame.draw.rect(surface, cfg.RED, hat_rect)

        # Eyes
        pygame.draw.circle(surface, cfg.BLACK, (int(self.x + 12), int(self.y + 6)), 2)
        pygame.draw.circle(surface, cfg.BLACK, (int(self.x + 20), int(self.y + 6)), 2)

    def get_observation(self):
        return {
            "player_x": self.x,
            "player_y": self.y,
            "is_grounded": self.on_ground,
        }


class Shell:
    """Koopa shell that bounces around."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = cfg.SHELL_WIDTH
        self.height = cfg.SHELL_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.active = False
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def kick(self, direction):
        self.active = True
        self.vel_x = cfg.SHELL_SPEED * direction

    def update(self):
        if not self.active:
            return

        # Apply gravity
        self.vel_y += cfg.GRAVITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Platform collision
        if self.y + self.height >= cfg.PLATFORM_Y_LEVEL:
            self.y = cfg.PLATFORM_Y_LEVEL - self.height
            self.vel_y = -self.vel_y * 0.7  # Bounce with energy loss
            if abs(self.vel_y) < 1:
                self.vel_y = 0
        else:
            self.vel_y *= cfg.AIR_RESISTANCE

        # Wall bouncing
        if self.x <= 0:
            self.x = 0
            self.vel_x = -self.vel_x
        elif self.x + self.width >= cfg.SCREEN_WIDTH:
            self.x = cfg.SCREEN_WIDTH - self.width
            self.vel_x = -self.vel_x

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface):
        if not self.active:
            return

        # Shell body (green)
        shell_rect = pygame.Rect(
            int(self.x), int(self.y + 4),
            self.width, self.height - 4
        )
        pygame.draw.rect(surface, cfg.GREEN, shell_rect)

        # Shell spiral (yellow)
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        pygame.draw.circle(surface, cfg.YELLOW, (center_x, center_y), 6)
        pygame.draw.circle(surface, cfg.GREEN, (center_x, center_y), 4)

        # Shell rim
        pygame.draw.rect(surface, (30, 150, 30), shell_rect, 2)

    def get_observation(self):
        return {
            "shell_x": self.x,
            "shell_y": self.y,
            "shell_velocity_x": self.vel_x,
            "shell_velocity_y": self.vel_y,
        }


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Infinite Koopa Shell Bounce")
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset()

    def reset(self):
        self.player = Player(100, cfg.PLATFORM_Y_LEVEL - cfg.PLAYER_HEIGHT)
        self.shell = Shell(400, cfg.PLATFORM_Y_LEVEL - cfg.SHELL_HEIGHT - 50)
        self.score = 0
        self.combo = 0
        self.game_over = False
        self.waiting_to_kick = True
        self.last_bounce_time = 0
        self.total_time = 0

    def check_collisions(self):
        if not self.shell.active:
            return

        player_rect = self.player.rect
        shell_rect = self.shell.rect

        if player_rect.colliderect(shell_rect):
            # Player lands on shell (from above)
            if (self.player.vel_y > 0 and
                self.player.y + self.player.height - 5 < self.shell.y + self.shell.height / 2):

                # Bounce off shell
                self.player.vel_y = -cfg.PLAYER_JUMP_POWER * 0.8
                self.combo += 1
                self.score += cfg.POINTS_PER_BOUNCE * self.combo
                self.last_bounce_time = self.total_time

                # Speed up shell slightly
                if self.shell.vel_x > 0:
                    self.shell.vel_x += cfg.SHELL_BOUNCE_ACCEL
                else:
                    self.shell.vel_x -= cfg.SHELL_BOUNCE_ACCEL

                # Limit shell speed
                self.shell.vel_x = max(-cfg.SHELL_SPEED * 2, min(cfg.SHELL_SPEED * 2, self.shell.vel_x))

            # Side collision (death)
            else:
                self.player.alive = False
                self.game_over = True

    def draw_platform(self):
        # Main platform
        platform_rect = pygame.Rect(0, cfg.PLATFORM_Y_LEVEL, cfg.SCREEN_WIDTH, cfg.PLATFORM_HEIGHT)
        pygame.draw.rect(self.screen, cfg.BROWN, platform_rect)

        # Platform top (grass)
        top_rect = pygame.Rect(0, cfg.PLATFORM_Y_LEVEL, cfg.SCREEN_WIDTH, 10)
        pygame.draw.rect(self.screen, cfg.GREEN, top_rect)

        # Brick pattern
        for x in range(0, cfg.SCREEN_WIDTH, 40):
            for y in range(cfg.PLATFORM_Y_LEVEL + 15, cfg.SCREEN_HEIGHT, 20):
                brick_rect = pygame.Rect(x + 2, y, 36, 15)
                pygame.draw.rect(self.screen, (120, 80, 40), brick_rect, 1)

    def draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {int(self.score)}", True, cfg.WHITE)
        self.screen.blit(score_text, (10, 10))

        # Combo
        if self.combo > 0:
            combo_color = cfg.YELLOW if self.combo >= 5 else cfg.WHITE
            combo_text = self.font.render(f"Combo: x{self.combo}", True, combo_color)
            self.screen.blit(combo_text, (10, 50))

        # Instructions
        if self.waiting_to_kick:
            instr_text = self.small_font.render("Press SPACE to kick the shell!", True, cfg.YELLOW)
            text_rect = instr_text.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2))
            self.screen.blit(instr_text, text_rect)

        # Game over
        if self.game_over:
            go_text = self.font.render("GAME OVER", True, cfg.RED)
            go_rect = go_text.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(go_text, go_rect)

            final_text = self.small_font.render(f"Final Score: {int(self.score)} | Max Combo: {self.combo}",
                                               True, cfg.WHITE)
            final_rect = final_text.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(final_text, final_rect)

            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, cfg.GRAY)
            restart_rect = restart_text.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        if event.key == pygame.K_SPACE:
                            if self.waiting_to_kick:
                                # Kick the shell
                                direction = 1 if self.player.x < self.shell.x else -1
                                self.shell.kick(direction)
                                self.waiting_to_kick = False
                            else:
                                self.player.jump()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            # Input handling
            if not self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.player.move_left()
                elif keys[pygame.K_RIGHT]:
                    self.player.move_right()
                else:
                    self.player.stop_horizontal()

            # Update
            if not self.game_over:
                self.player.update()
                self.shell.update()
                self.check_collisions()

                # Combo timeout
                if self.combo > 0 and self.total_time - self.last_bounce_time > cfg.MAX_COMBO_TIME_SECONDS:
                    self.combo = 0

                # Survival points
                self.score += cfg.POINTS_PER_FRAME
                self.total_time += 1 / cfg.FPS

            # Draw
            self.screen.fill(cfg.SKY_BLUE)
            self.draw_platform()
            self.shell.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_hud()

            pygame.display.flip()
            self.clock.tick(cfg.FPS)

        pygame.quit()

    def get_observation(self):
        """Return current game state for RL agents."""
        obs = {}
        obs.update(self.player.get_observation())
        obs.update(self.shell.get_observation())
        return obs

    def get_action_space(self):
        """Return available actions for RL agents."""
        return ["LEFT", "RIGHT", "JUMP", "NONE"]

    def step(self, action):
        """Step function for RL agents."""
        if action == "LEFT":
            self.player.move_left()
        elif action == "RIGHT":
            self.player.move_right()
        elif action == "JUMP":
            self.player.jump()

        self.player.update()
        self.shell.update()
        self.check_collisions()

        reward = cfg.POINTS_PER_FRAME
        done = self.game_over

        if done:
            reward = cfg.GAME_OVER_PENALTY

        return self.get_observation(), reward, done, {"score": self.score, "combo": self.combo}
