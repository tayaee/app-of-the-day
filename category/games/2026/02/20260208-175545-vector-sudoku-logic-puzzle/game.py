"""Main game loop and rendering."""

import sys
import pygame
from pygame import locals
import config
from entities import GameState, Cell


class SudokuGame:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Sudoku")
        self.clock = pygame.time.Clock()
        self.state = GameState()

        # Fonts
        self.font_large = pygame.font.Font(None, config.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, config.FONT_SIZE_SMALL)

        # Button areas
        self.new_game_btn = pygame.Rect(
            config.WINDOW_WIDTH - 140, 15, 120, 30
        )

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == locals.K_ESCAPE:
                        running = False
                    else:
                        self._handle_keypress(event.key)

            self._render()
            self.clock.tick(config.FPS)

        pygame.quit()
        sys.exit()

    def _handle_mouse_click(self, pos: tuple) -> None:
        """Handle mouse click events."""
        x, y = pos

        # Check new game button
        if self.new_game_btn.collidepoint(x, y):
            self.state.new_game()
            return

        # Check grid click
        cell_pos = self.state.get_cell_at_pos(x, y)
        if cell_pos:
            row, col = cell_pos
            self.state.select_cell(row, col)

    def _handle_keypress(self, key: int) -> None:
        """Handle keyboard input."""
        if not self.state.selected_cell or self.state.is_won:
            return

        # Number keys 1-9
        if locals.K_1 <= key <= locals.K_9:
            value = key - locals.K_0
            self.state.set_cell_value(value)
        elif locals.K_KP1 <= key <= locals.K_KP9:
            value = key - locals.K_KP0
            self.state.set_cell_value(value)
        # Clear cell
        elif key == locals.K_BACKSPACE or key == locals.K_DELETE or key == locals.K_0:
            self.state.clear_selected_cell()

    def _render(self) -> None:
        """Render the game state."""
        self.screen.fill(config.COLOR_BG)

        self._draw_title()
        self._draw_score()
        self._draw_new_game_button()
        self._draw_grid()
        self._draw_cells()
        self._draw_win_message()

        pygame.display.flip()

    def _draw_title(self) -> None:
        """Draw the game title."""
        title = self.font_medium.render("SUDOKU", True, config.COLOR_TEXT)
        self.screen.blit(title, (20, 20))

    def _draw_score(self) -> None:
        """Draw the current score."""
        score_text = self.font_small.render(f"Score: {self.state.score}", True, config.COLOR_TEXT)
        self.screen.blit(score_text, (20, 50))

        moves_text = self.font_small.render(f"Moves: {self.state.moves}", True, config.COLOR_TEXT)
        self.screen.blit(moves_text, (120, 50))

    def _draw_new_game_button(self) -> None:
        """Draw the new game button."""
        mouse_pos = pygame.mouse.get_pos()
        color = config.COLOR_BUTTON_HOVER if self.new_game_btn.collidepoint(mouse_pos) else config.COLOR_BUTTON

        pygame.draw.rect(self.screen, color, self.new_game_btn, border_radius=5)
        pygame.draw.rect(self.screen, config.COLOR_GRID, self.new_game_btn, 1, border_radius=5)

        text = self.font_small.render("New Game", True, config.COLOR_TEXT)
        text_rect = text.get_rect(center=self.new_game_btn.center)
        self.screen.blit(text, text_rect)

    def _draw_grid(self) -> None:
        """Draw the Sudoku grid."""
        grid_rect = pygame.Rect(
            config.GRID_OFFSET_X,
            config.GRID_OFFSET_Y,
            config.GRID_SIZE * config.CELL_SIZE,
            config.GRID_SIZE * config.CELL_SIZE
        )
        pygame.draw.rect(self.screen, config.COLOR_GRID, grid_rect, config.BORDER_THICK)

        # Draw vertical lines
        for i in range(1, config.GRID_SIZE):
            x = config.GRID_OFFSET_X + i * config.CELL_SIZE
            width = config.BORDER_THICK if i % config.BOX_SIZE == 0 else config.BORDER_THIN
            pygame.draw.line(
                self.screen,
                config.COLOR_GRID,
                (x, config.GRID_OFFSET_Y),
                (x, config.GRID_OFFSET_Y + config.GRID_SIZE * config.CELL_SIZE),
                width
            )

        # Draw horizontal lines
        for i in range(1, config.GRID_SIZE):
            y = config.GRID_OFFSET_Y + i * config.CELL_SIZE
            width = config.BORDER_THICK if i % config.BOX_SIZE == 0 else config.BORDER_THIN
            pygame.draw.line(
                self.screen,
                config.COLOR_GRID,
                (config.GRID_OFFSET_X, y),
                (config.GRID_OFFSET_X + config.GRID_SIZE * config.CELL_SIZE, y),
                width
            )

    def _draw_cells(self) -> None:
        """Draw the cell values and highlights."""
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                self._draw_cell(row, col)

    def _draw_cell(self, row: int, col: int) -> None:
        """Draw a single cell."""
        cell = self.state.cells[row][col]
        x = config.GRID_OFFSET_X + col * config.CELL_SIZE
        y = config.GRID_OFFSET_Y + row * config.CELL_SIZE

        # Draw cell background
        if cell.is_selected:
            pygame.draw.rect(
                self.screen,
                config.COLOR_CELL_SELECTED,
                (x + 1, y + 1, config.CELL_SIZE - 2, config.CELL_SIZE - 2)
            )
        elif cell.is_error:
            pygame.draw.rect(
                self.screen,
                config.COLOR_CELL_ERROR,
                (x + 1, y + 1, config.CELL_SIZE - 2, config.CELL_SIZE - 2)
            )
        elif not cell.is_given and cell.value != config.EMPTY_CELL:
            pygame.draw.rect(
                self.screen,
                config.COLOR_CELL_FILL,
                (x + 1, y + 1, config.CELL_SIZE - 2, config.CELL_SIZE - 2)
            )

        # Draw cell value
        if cell.value != config.EMPTY_CELL:
            color = config.COLOR_TEXT_GIVEN if cell.is_given else config.COLOR_TEXT_USER
            text = self.font_large.render(str(cell.value), True, color)
            text_rect = text.get_rect(center=(x + config.CELL_SIZE // 2, y + config.CELL_SIZE // 2))
            self.screen.blit(text, text_rect)

    def _draw_win_message(self) -> None:
        """Draw the win message when the game is won."""
        if self.state.is_won:
            overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))

            win_text = self.font_medium.render("PUZZLE SOLVED!", True, config.COLOR_TEXT)
            win_rect = win_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(win_text, win_rect)

            score_text = self.font_small.render(f"Final Score: {self.state.score}", True, config.COLOR_TEXT)
            score_rect = score_text.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(score_text, score_rect)
