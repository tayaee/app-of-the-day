"""Main game logic for Vector Sokoban Warehouse Logic."""

import pygame
from config import *
from entities import GameState


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Sokoban Warehouse Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 48)

        self.game_state = GameState()

    def handle_input(self) -> bool:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_r:
                    self.game_state.reset_level()

                if event.key == pygame.K_n and self.game_state.level_complete:
                    self.game_state.next_level()

                # Movement
                dx, dy = 0, 0
                if event.key in (pygame.K_UP, pygame.K_w):
                    dx = -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    dx = 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dy = -1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dy = 1

                if dx != 0 or dy != 0:
                    self.game_state.move(dx, dy)

        return True

    def update(self) -> None:
        """Update game state."""
        pass

    def draw(self) -> None:
        """Render the game."""
        self.screen.fill(COLOR_BG)

        self._draw_ui()
        self._draw_grid()
        self._draw_game_elements()

        if self.game_state.game_won:
            self._draw_game_won()
        elif self.game_state.level_complete:
            self._draw_level_complete()
        elif self.game_state.deadlocked:
            self._draw_deadlock()

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # UI background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, ui_rect)
        pygame.draw.line(self.screen, COLOR_BORDER, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Level info
        level_text = self.font.render(f"Level: {self.game_state.level_index + 1}/{len(LEVELS)}", True, COLOR_TEXT)
        self.screen.blit(level_text, (20, 15))

        # Box progress
        boxes_on_targets = self.game_state.get_boxes_on_targets()
        total_boxes = len(self.game_state.boxes)
        boxes_text = self.font.render(f"Boxes: {boxes_on_targets}/{total_boxes}", True, COLOR_TEXT)
        self.screen.blit(boxes_text, (20, 45))

        # Move count
        moves_text = self.font.render(f"Moves: {self.game_state.move_count}", True, COLOR_TEXT)
        self.screen.blit(moves_text, (200, 15))

        # Reward
        reward_text = self.small_font.render(f"Reward: {self.game_state.total_reward:.1f}", True, COLOR_TEXT_DIM)
        self.screen.blit(reward_text, (SCREEN_WIDTH // 2 - reward_text.get_width() // 2, 50))

        # Controls
        controls_text = self.small_font.render("Arrow Keys / WASD: Move", True, COLOR_TEXT_DIM)
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 20, 15))

        restart_text = self.small_font.render("R: Restart | N: Next Level", True, COLOR_TEXT_DIM)
        self.screen.blit(restart_text, (SCREEN_WIDTH - restart_text.get_width() - 20, 40))

    def _draw_grid(self) -> None:
        """Draw the game grid."""
        state = self.game_state.get_state()
        rows = len(state)
        cols = len(state[0]) if rows > 0 else 0

        for row in range(rows):
            for col in range(cols):
                x = GRID_OFFSET_X + col * TILE_SIZE
                y = GRID_OFFSET_Y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                cell_state = state[row][col]

                # Draw floor
                pygame.draw.rect(self.screen, COLOR_FLOOR, rect)

                # Draw wall
                if cell_state == STATE_WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, COLOR_WALL_OUTLINE, rect, 2)

                # Draw target (hollow circle)
                if (row, col) in self.game_state.targets:
                    center_x = x + TILE_SIZE // 2
                    center_y = y + TILE_SIZE // 2
                    radius = TILE_SIZE // 5
                    pygame.draw.circle(self.screen, COLOR_TARGET, (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, COLOR_TARGET_OUTLINE, (center_x, center_y), radius, 2)

                # Draw grid border
                pygame.draw.rect(self.screen, (40, 40, 45), rect, 1)

    def _draw_game_elements(self) -> None:
        """Draw boxes and worker."""
        state = self.game_state.get_state()
        rows = len(state)
        cols = len(state[0]) if rows > 0 else 0

        for row in range(rows):
            for col in range(cols):
                x = GRID_OFFSET_X + col * TILE_SIZE
                y = GRID_OFFSET_Y + row * TILE_SIZE
                cell_state = state[row][col]

                # Draw box
                if cell_state == STATE_BOX:
                    self._draw_box(x, y, COLOR_BOX, COLOR_BOX_OUTLINE, False)
                elif cell_state == STATE_BOX_ON_TARGET:
                    self._draw_box(x, y, COLOR_BOX_ON_TARGET, COLOR_BOX_ON_TARGET_OUTLINE, True)

        # Draw worker
        wx, wy = self.game_state.worker_pos
        wx = GRID_OFFSET_X + wy * TILE_SIZE
        wy = GRID_OFFSET_Y + wx * TILE_SIZE
        self._draw_worker(wx, wy)

    def _draw_box(self, x: int, y: int, color: tuple, outline: tuple, on_target: bool) -> None:
        """Draw a box at the given position."""
        box_rect = pygame.Rect(x + 6, y + 6, TILE_SIZE - 12, TILE_SIZE - 12)
        pygame.draw.rect(self.screen, color, box_rect)
        pygame.draw.rect(self.screen, outline, box_rect, 3)

        # Draw box inner detail
        inner_rect = pygame.Rect(x + 12, y + 12, TILE_SIZE - 24, TILE_SIZE - 24)
        pygame.draw.rect(self.screen, outline, inner_rect, 1)

        # Draw checkmark if on target
        if on_target:
            center_x = x + TILE_SIZE // 2
            center_y = y + TILE_SIZE // 2
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 4)

    def _draw_worker(self, x: int, y: int) -> None:
        """Draw the worker at the given position."""
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        radius = TILE_SIZE // 3

        # Worker body
        pygame.draw.circle(self.screen, COLOR_WORKER, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, COLOR_WORKER_OUTLINE, (center_x, center_y), radius, 2)

        # Direction indicator
        pygame.draw.circle(self.screen, (200, 160, 100), (center_x, center_y), 4)

    def _draw_level_complete(self) -> None:
        """Draw level complete overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("LEVEL COMPLETE!", True, (100, 200, 120))
        score_text = self.font.render(f"Moves: {self.game_state.move_count}", True, COLOR_TEXT)
        reward_text = self.font.render(f"Reward: {self.game_state.total_reward:.1f}", True, COLOR_TEXT)
        next_text = self.small_font.render("Press N for next level", True, COLOR_TEXT_DIM)
        restart_text = self.small_font.render("Press R to restart level", True, COLOR_TEXT_DIM)
        quit_text = self.small_font.render("Press ESC to quit", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 80))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y - 20))
        self.screen.blit(reward_text, (center_x - reward_text.get_width() // 2, center_y + 15))
        self.screen.blit(next_text, (center_x - next_text.get_width() // 2, center_y + 60))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 90))
        self.screen.blit(quit_text, (center_x - quit_text.get_width() // 2, center_y + 120))

    def _draw_game_won(self) -> None:
        """Draw game won overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("ALL LEVELS COMPLETE!", True, (100, 180, 255))
        score_text = self.font.render(f"Total Moves: {self.game_state.move_count}", True, COLOR_TEXT)
        reward_text = self.font.render(f"Total Reward: {self.game_state.total_reward:.1f}", True, COLOR_TEXT)
        restart_text = self.small_font.render("Press R to play again", True, COLOR_TEXT_DIM)
        quit_text = self.small_font.render("Press ESC to quit", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 60))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y))
        self.screen.blit(reward_text, (center_x - reward_text.get_width() // 2, center_y + 35))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 80))
        self.screen.blit(quit_text, (center_x - quit_text.get_width() // 2, center_y + 110))

    def _draw_deadlock(self) -> None:
        """Draw deadlock warning overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((200, 50, 50, 50))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("DEADLOCK!", True, (200, 100, 100))
        subtitle_text = self.font.render("A box is stuck. Press R to restart.", True, COLOR_TEXT)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 30))
        self.screen.blit(subtitle_text, (center_x - subtitle_text.get_width() // 2, center_y + 20))

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
