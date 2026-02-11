"""Main game loop and rendering logic."""

import pygame
import config
from entities import GameState, Player, Floor, Enemy, Item, Door, Wave


class Game:
    """Main game class handling loop, rendering, and input."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vector Mappy: Stolen Item Retrieve")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.state = config.STATE_MENU
        self.game_state = GameState()
        self.game_state.reset()

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == config.KEY_EXIT:
                        running = False
                    elif self.state == config.STATE_MENU:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._start_game()
                    elif self.state == config.STATE_GAMEOVER:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._restart_game()
                    elif self.state == config.STATE_LEVEL_COMPLETE:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._next_level()
                    elif self.state == config.STATE_PLAYING:
                        if event.key == config.KEY_JUMP or event.key == config.KEY_JUMP_ALT:
                            self._use_door()

            # State-specific updates
            if self.state == config.STATE_PLAYING:
                self._update()

            # Rendering
            self._render()
            self.clock.tick(config.FPS)

        pygame.quit()

    def _start_game(self) -> None:
        """Start a new game."""
        self.state = config.STATE_PLAYING
        self.game_state.reset()

    def _restart_game(self) -> None:
        """Restart the game from level 1."""
        self.state = config.STATE_PLAYING
        self.game_state.reset()

    def _next_level(self) -> None:
        """Advance to next level."""
        self.state = config.STATE_PLAYING
        self.game_state.next_level()

    def _use_door(self) -> None:
        """Activate a door near the player."""
        player = self.game_state.player
        if player.door_cooldown > 0:
            return

        # Find nearby door
        for floor in self.game_state.floors:
            if floor.door:
                door = floor.door
                door_rect = pygame.Rect(door.x, door.y, config.DOOR_WIDTH, config.DOOR_HEIGHT)
                player_rect = pygame.Rect(player.x, player.y, config.PLAYER_SIZE, config.PLAYER_SIZE)

                if door_rect.colliderect(player_rect.inflate(20, 20)):
                    direction = 1 if door.facing_right else -1
                    wave = Wave(
                        door.x + (config.DOOR_WIDTH if direction > 0 else -40),
                        door.y,
                        direction
                    )
                    self.game_state.waves.append(wave)
                    door.cooldown = config.DOOR_COOLDOWN
                    door.is_open = True
                    door.open_timer = 15
                    player.door_cooldown = 30
                    return

    def _update(self) -> None:
        """Update game logic."""
        state = self.game_state

        if state.game_over:
            self.state = config.STATE_GAMEOVER
            return

        if state.level_complete:
            self.state = config.STATE_LEVEL_COMPLETE
            return

        # Handle continuous key input
        keys = pygame.key.get_pressed()
        if keys[config.KEY_LEFT]:
            state.player.move_left()
        elif keys[config.KEY_RIGHT]:
            state.player.move_right()
        else:
            state.player.stop_horizontal()

        # Update player
        state.player.update()

        # Update doors
        for floor in state.floors:
            if floor.door:
                if floor.door.cooldown > 0:
                    floor.door.cooldown -= 1
                if floor.door.open_timer > 0:
                    floor.door.open_timer -= 1
                else:
                    floor.door.is_open = False

        # Update waves
        for wave in state.waves[:]:
            if not wave.update():
                state.waves.remove(wave)

        # Floor and trampoline collision
        player_rect = pygame.Rect(state.player.rect)
        player_bottom = state.player.y + config.PLAYER_SIZE

        state.player.on_floor = False
        state.player.on_trampoline = False

        for floor in state.floors:
            floor_rect = pygame.Rect(floor.rect)

            # Check if player is falling onto this floor
            if state.player.vy >= 0:
                if player_rect.colliderect(floor_rect):
                    # Check if landing on trampoline
                    if floor.trampoline and not floor.trampoline.broken:
                        tramp_half_width = config.TRAMPOLINE_WIDTH / 2
                        tramp_x = floor.trampoline.x
                        if tramp_x - tramp_half_width <= state.player.x + config.PLAYER_SIZE / 2 <= tramp_x + tramp_half_width:
                            # Landed on trampoline
                            state.player.y = floor.y - config.PLAYER_SIZE
                            state.player.jump(is_trampoline=True)
                            state.player.on_trampoline = True
                            state.player.current_trampoline = floor.trampoline
                            state.player.consecutive_bounces += 1
                            floor.trampoline.bounce_count += 1

                            # Check if trampoline breaks
                            if floor.trampoline.bounce_count >= config.MAX_BOUNCES:
                                floor.trampoline.broken = True
                                state.player.consecutive_bounces = 0
                            continue

                    # Landed on regular floor
                    state.player.y = floor.y - config.PLAYER_SIZE
                    state.player.vy = 0
                    state.player.on_floor = True
                    state.player.consecutive_bounces = 0

        # Update enemies
        for enemy in state.enemies[:]:
            enemy.update()

            # Reverse at screen edges
            if enemy.x <= 0 or enemy.x >= config.SCREEN_WIDTH - config.ENEMY_SIZE:
                enemy.reverse()

            # Reverse at floor edges
            if 0 <= enemy.floor_index < len(state.floors):
                floor = state.floors[enemy.floor_index]
                if enemy.x <= floor.x or enemy.x >= floor.x + floor.width - config.ENEMY_SIZE:
                    enemy.reverse()

            # Check collision with waves
            for wave in state.waves:
                wave_rect = wave.get_rect()
                enemy_rect = pygame.Rect(enemy.rect)
                if wave_rect.colliderect(enemy_rect):
                    enemy.push(wave.direction * config.WAVE_PUSH_FORCE, 20)

            # Check collision with closed doors
            if 0 <= enemy.floor_index < len(state.floors):
                floor = state.floors[enemy.floor_index]
                if floor.door and not floor.door.is_open:
                    door_rect = pygame.Rect(floor.door.x, floor.door.y, config.DOOR_WIDTH, config.DOOR_HEIGHT)
                    enemy_rect = pygame.Rect(enemy.rect)
                    if enemy_rect.colliderect(door_rect):
                        enemy.reverse()

            # Check collision with player (only on floors, not mid-air)
            if state.player.on_floor and not state.player.on_trampoline:
                enemy_rect = pygame.Rect(enemy.rect)
                player_rect = pygame.Rect(state.player.rect)
                if player_rect.colliderect(enemy_rect):
                    state.lose_life()
                    if state.game_over:
                        return

        # Check item collection
        for floor in state.floors:
            for item in floor.items[:]:
                if not item.collected:
                    item_rect = pygame.Rect(item.rect)
                    player_rect = pygame.Rect(state.player.rect)
                    if player_rect.colliderect(item_rect):
                        item.collected = True
                        floor.items.remove(item)
                        state.score += item.get_points()
                        state.items_collected += 1

        # Check level complete
        if state.items_collected >= state.total_items:
            state.level_complete = True
            state.score += config.POINTS_LEVEL_COMPLETE

        # Check death (fall below screen)
        if state.player.y > config.SCREEN_HEIGHT:
            state.lose_life()
            if state.game_over:
                return

    def _render(self) -> None:
        """Render the current frame."""
        self.screen.fill(config.COLOR_BG)

        if self.state == config.STATE_MENU:
            self._render_menu()
        elif self.state == config.STATE_PLAYING:
            self._render_game()
        elif self.state == config.STATE_GAMEOVER:
            self._render_game()
            self._render_gameover()
        elif self.state == config.STATE_LEVEL_COMPLETE:
            self._render_game()
            self._render_level_complete()

        pygame.display.flip()

    def _render_menu(self) -> None:
        """Render the menu screen."""
        # Title
        title = self.font.render("MAPPY: STOLEN ITEM", True, config.COLOR_PLAYER)
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 160))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("RETRIEVE", True, config.COLOR_PLAYER)
        sub_rect = subtitle.get_rect(center=(config.SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, sub_rect)

        instruction = self.small_font.render("Recover stolen goods from the cats!", True, config.COLOR_UI)
        inst_rect = instruction.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
        self.screen.blit(instruction, inst_rect)

        # Controls
        lines = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "LEFT/RIGHT - Move",
            "SPACE - Open doors (push cats)",
            "",
            "Items:",
            "Yellow: Radio (100pts)",
            "Blue: TV (200pts)",
            "Silver: Safe (500pts)",
            "",
            "Trampolines break after 4 bounces!",
            "Use doors to stun cats temporarily"
        ]

        for i, line in enumerate(lines):
            color = config.COLOR_TEXT if i == 0 else config.COLOR_UI
            text = self.small_font.render(line, True, color)
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, 300 + i * 25))
            self.screen.blit(text, text_rect)

    def _render_game(self) -> None:
        """Render the game world."""
        state = self.game_state

        # Draw floors
        for floor in state.floors:
            pygame.draw.rect(self.screen, config.COLOR_FLOOR,
                           (floor.x, floor.y, floor.width, config.FLOOR_HEIGHT),
                           border_radius=3)
            pygame.draw.rect(self.screen, (100, 110, 130),
                           (floor.x + 2, floor.y + 2, floor.width - 4, 3),
                           border_radius=2)

        # Draw trampolines
        for floor in state.floors:
            if floor.trampoline and not floor.trampoline.broken:
                tramp = floor.trampoline
                color = tramp.get_color()
                half_width = config.TRAMPOLINE_WIDTH / 2
                pygame.draw.rect(self.screen, color,
                               (tramp.x - half_width, tramp.y - config.TRAMPOLINE_HEIGHT,
                                config.TRAMPOLINE_WIDTH, config.TRAMPOLINE_HEIGHT),
                               border_radius=4)
                # Bounce indicator
                bounces_left = config.MAX_BOUNCES - tramp.bounce_count
                for i in range(bounces_left):
                    offset_x = (i - 1.5) * 8
                    pygame.draw.circle(self.screen, (255, 255, 255),
                                     (int(tramp.x + offset_x), int(tramp.y - 4)), 2)

        # Draw doors
        for floor in state.floors:
            if floor.door:
                door = floor.door
                color = config.COLOR_DOOR_HIGHLIGHT if door.is_open else config.COLOR_DOOR
                pygame.draw.rect(self.screen, color,
                               (door.x, door.y, config.DOOR_WIDTH, config.DOOR_HEIGHT),
                               border_radius=3)
                # Door frame
                pygame.draw.rect(self.screen, config.COLOR_WALL,
                               (door.x, door.y, config.DOOR_WIDTH, config.DOOR_HEIGHT),
                               2, border_radius=3)
                # Door handle
                handle_x = door.x + config.DOOR_WIDTH - 8 if door.facing_right else door.x + 5
                pygame.draw.circle(self.screen, (200, 180, 150),
                                 (int(handle_x), int(door.y + config.DOOR_HEIGHT // 2)), 3)

        # Draw waves
        for wave in state.waves:
            wave_rect = wave.get_rect()
            s = pygame.Surface((wave.width, wave.height), pygame.SRCALPHA)
            alpha = int(150 * (wave.lifetime / config.WAVE_DURATION))
            pygame.draw.ellipse(s, (*config.COLOR_WAVE, alpha), (0, 0, wave.width, wave.height))
            self.screen.blit(s, wave_rect)

        # Draw items
        for floor in state.floors:
            for item in floor.items:
                color = item.get_color()
                x, y = item.x, item.y
                size = config.ITEM_SIZE // 2

                if item.item_type == "safe":
                    # Draw safe
                    pygame.draw.rect(self.screen, color,
                                   (x - size//2, y - size//2, size * 2, size * 1.5),
                                   border_radius=3)
                    pygame.draw.circle(self.screen, (150, 150, 160),
                                     (int(x), int(y)), 4)
                    pygame.draw.line(self.screen, (100, 100, 110),
                                    (x - 4, y), (x + 4, y), 2)
                elif item.item_type == "tv":
                    # Draw TV
                    pygame.draw.rect(self.screen, color,
                                   (x - size//2, y - size//2, size * 2, size * 1.5),
                                   border_radius=2)
                    pygame.draw.rect(self.screen, (30, 50, 80),
                                   (x - size//2 + 3, y - size//2 + 3, size * 2 - 6, size))
                    # Antenna
                    pygame.draw.line(self.screen, color,
                                    (x - 3, y - size//2), (x - 5, y - size), 2)
                    pygame.draw.line(self.screen, color,
                                    (x + 3, y - size//2), (x + 5, y - size), 2)
                else:  # radio
                    # Draw radio
                    pygame.draw.rect(self.screen, color,
                                   (x - size//2, y - size//3, size * 2, size * 1.3),
                                   border_radius=3)
                    pygame.draw.circle(self.screen, (180, 180, 90),
                                     (int(x + size//2), int(y)), 3)
                    pygame.draw.line(self.screen, (150, 150, 80),
                                    (x - size//2 + 5, y), (x + size//2 - 5, y), 2)

        # Draw enemies
        for enemy in state.enemies:
            x, y = enemy.x, enemy.y
            size = config.ENEMY_SIZE

            # Body
            body_color = config.COLOR_ENEMY if enemy.stunned <= 0 else (150, 100, 100)
            pygame.draw.ellipse(self.screen, body_color,
                              (x - size//2, y - size//2, size, size * 0.8))
            # Ears
            pygame.draw.polygon(self.screen, body_color,
                              [(x - size//3, y - size//3),
                               (x - size//2, y - size//1.5),
                               (x - size//6, y - size//2)])
            pygame.draw.polygon(self.screen, body_color,
                              [(x + size//3, y - size//3),
                               (x + size//2, y - size//1.5),
                               (x + size//6, y - size//2)])
            # Eyes
            eye_color = (200, 200, 200) if enemy.stunned > 0 else (255, 255, 255)
            pygame.draw.circle(self.screen, eye_color, (int(x - 4), int(y - 2)), 3)
            pygame.draw.circle(self.screen, eye_color, (int(x + 4), int(y - 2)), 3)
            pupil_color = (80, 80, 80) if enemy.stunned > 0 else (0, 0, 0)
            pygame.draw.circle(self.screen, pupil_color, (int(x - 4), int(y - 2)), 1)
            pygame.draw.circle(self.screen, pupil_color, (int(x + 4), int(y - 2)), 1)

        # Draw player (mouse)
        px, py = state.player.x, state.player.y
        pygame.draw.ellipse(self.screen, config.COLOR_PLAYER,
                          (px, py, config.PLAYER_SIZE, config.PLAYER_SIZE * 0.85))
        # Ears
        pygame.draw.circle(self.screen, config.COLOR_PLAYER,
                          (int(px + 4), int(py)), 5)
        pygame.draw.circle(self.screen, config.COLOR_PLAYER,
                          (int(px + config.PLAYER_SIZE - 4), int(py)), 5)
        # Inner ears
        pygame.draw.circle(self.screen, (200, 230, 255),
                          (int(px + 4), int(py)), 2)
        pygame.draw.circle(self.screen, (200, 230, 255),
                          (int(px + config.PLAYER_SIZE - 4), int(py)), 2)
        # Eyes
        eye_offset = 4 if state.player.facing_right else -4
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (int(px + config.PLAYER_SIZE//2 + eye_offset), int(py + 8)), 4)
        pygame.draw.circle(self.screen, (0, 0, 0),
                          (int(px + config.PLAYER_SIZE//2 + eye_offset), int(py + 8)), 2)

        # Draw HUD
        score_text = self.font.render(f"Score: {state.score}", True, config.COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        level_text = self.small_font.render(f"Level: {state.level}", True, config.COLOR_UI)
        self.screen.blit(level_text, (10, 50))

        lives_text = self.small_font.render(f"Lives: {state.lives}", True, config.COLOR_ENEMY)
        self.screen.blit(lives_text, (10, 75))

        items_text = self.small_font.render(f"Items: {state.items_collected}/{state.total_items}",
                                          True, config.COLOR_ITEM_SAFE)
        self.screen.blit(items_text, (10, 100))

        # Bounce warning
        if state.player.consecutive_bounces >= config.MAX_BOUNCES - 1:
            warn_text = self.small_font.render("BREAKING!", True, config.COLOR_TRAMPOLINE_DANGER)
            self.screen.blit(warn_text, (10, 125))

    def _render_gameover(self) -> None:
        """Render game over overlay."""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, config.COLOR_ENEMY)
        game_over_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
        self.screen.blit(game_over_text, game_over_rect)

        final_score = self.small_font.render(f"Final Score: {self.game_state.score}",
                                           True, config.COLOR_TEXT)
        score_rect = final_score.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
        self.screen.blit(final_score, score_rect)

        restart_text = self.small_font.render("Press SPACE to Restart", True, config.COLOR_UI)
        restart_rect = restart_text.get_rect(center=(config.SCREEN_WIDTH // 2, 350))
        self.screen.blit(restart_text, restart_rect)

    def _render_level_complete(self) -> None:
        """Render level complete overlay."""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        level_text = self.font.render("LEVEL COMPLETE!", True, config.COLOR_ITEM_TV)
        level_rect = level_text.get_rect(center=(config.SCREEN_WIDTH // 2, 250))
        self.screen.blit(level_text, level_rect)

        bonus_text = self.small_font.render(f"+{config.POINTS_LEVEL_COMPLETE} Bonus!",
                                          True, config.COLOR_TEXT)
        bonus_rect = bonus_text.get_rect(center=(config.SCREEN_WIDTH // 2, 300))
        self.screen.blit(bonus_text, bonus_rect)

        continue_text = self.small_font.render("Press SPACE for Next Level", True, config.COLOR_UI)
        continue_rect = continue_text.get_rect(center=(config.SCREEN_WIDTH // 2, 350))
        self.screen.blit(continue_text, continue_rect)
