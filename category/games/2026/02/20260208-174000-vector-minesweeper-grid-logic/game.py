"""Main game logic for Vector Minesweeper Grid Logic."""

import pygame
from config import *
from entities import Grid


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Minesweeper Grid Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 48)

        self.grid = Grid()
        self.mouse_pos = (0, 0)
        self.hover_cell = None

    def handle_input(self) -> bool:
        """Handle keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    self.grid.reset()

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                self._update_hover()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_left_click()
                elif event.button == 3:  # Right click
                    self._handle_right_click()

        return True

    def _update_hover(self) -> None:
        """Update the currently hovered cell."""
        col = (self.mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
        row = (self.mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            self.hover_cell = (row, col)
        else:
            self.hover_cell = None

    def _handle_left_click(self) -> None:
        """Handle left mouse click (reveal)."""
        if self.hover_cell and not self.grid.game_over:
            row, col = self.hover_cell
            self.grid.reveal(row, col)

    def _handle_right_click(self) -> None:
        """Handle right mouse click (flag)."""
        if self.hover_cell and not self.grid.game_over:
            row, col = self.hover_cell
            self.grid.toggle_flag(row, col)

    def update(self) -> None:
        """Update game state."""
        pass

    def draw(self) -> None:
        """Render the game."""
        self.screen.fill(COLOR_BG)

        self._draw_ui()
        self._draw_grid()
        self._draw_cells()

        if self.grid.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # UI background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, (22, 22, 26), ui_rect)
        pygame.draw.line(self.screen, COLOR_BORDER, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        # Game info
        mines_left = self.grid.mines - self.grid.flagged_count
        mines_text = self.font.render(f"Mines: {mines_left}", True, COLOR_TEXT)
        self.screen.blit(mines_text, (20, 15))

        # Revealed count
        revealed_text = self.font.render(
            f"Revealed: {self.grid.revealed_count}/{GRID_ROWS * GRID_COLS - self.grid.mines}",
            True, COLOR_TEXT
        )
        self.screen.blit(revealed_text, (20, 45))

        # Reward
        reward_text = self.small_font.render(f"Reward: {self.grid.total_reward:.1f}", True, COLOR_TEXT_DIM)
        self.screen.blit(reward_text, (SCREEN_WIDTH // 2 - reward_text.get_width() // 2, 50))

        # Controls
        controls_text = self.small_font.render("L-Click: Reveal | R-Click: Flag", True, COLOR_TEXT_DIM)
        self.screen.blit(controls_text, (SCREEN_WIDTH - controls_text.get_width() - 20, 20))

        restart_text = self.small_font.render("R: New Game", True, COLOR_TEXT_DIM)
        self.screen.blit(restart_text, (SCREEN_WIDTH - restart_text.get_width() - 20, 45))

    def _draw_grid(self) -> None:
        """Draw the grid background."""
        # Grid border
        grid_width = GRID_COLS * CELL_SIZE
        grid_height = GRID_ROWS * CELL_SIZE
        border_rect = pygame.Rect(GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2, grid_width + 4, grid_height + 4)
        pygame.draw.rect(self.screen, COLOR_BORDER, border_rect, 2)

        # Grid background
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, grid_width, grid_height)
        pygame.draw.rect(self.screen, COLOR_GRID, grid_rect)

    def _draw_cells(self) -> None:
        """Draw all cells."""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self._draw_cell(row, col)

    def _draw_cell(self, row: int, col: int) -> None:
        """Draw a single cell."""
        cell = self.grid.get_cell(row, col)
        if not cell:
            return

        x = GRID_OFFSET_X + col * CELL_SIZE
        y = GRID_OFFSET_Y + row * CELL_SIZE
        rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

        # Determine cell color
        if cell.is_revealed:
            if cell.is_mine:
                color = COLOR_MINE
            else:
                color = COLOR_CELL_REVEALED
        elif self.hover_cell == (row, col):
            color = COLOR_CELL_HOVER
        else:
            color = COLOR_CELL_HIDDEN

        pygame.draw.rect(self.screen, color, rect)

        # Draw cell content
        if cell.is_flagged and not cell.is_revealed:
            self._draw_flag(x, y)
        elif cell.is_revealed:
            if cell.is_mine:
                self._draw_mine(x, y)
            elif cell.neighbor_mines > 0:
                self._draw_number(x, y, cell.neighbor_mines)

    def _draw_number(self, x: int, y: int, number: int) -> None:
        """Draw a number in the cell."""
        color = COLOR_NUMBERS.get(number, COLOR_TEXT)
        text = self.font.render(str(number), True, color)
        text_rect = text.get_rect(
            center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        )
        self.screen.blit(text, text_rect)

    def _draw_mine(self, x: int, y: int) -> None:
        """Draw a mine in the cell."""
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2
        radius = CELL_SIZE // 4

        # Glow effect
        pygame.draw.circle(self.screen, (150, 40, 40), (center_x, center_y), radius + 4)
        pygame.draw.circle(self.screen, COLOR_MINE, (center_x, center_y), radius)

    def _draw_flag(self, x: int, y: int) -> None:
        """Draw a flag in the cell."""
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2

        # Flag pole
        pygame.draw.line(self.screen, COLOR_FLAG, (center_x - 5, center_y + 10), (center_x - 5, center_y - 10), 2)

        # Flag
        flag_points = [
            (center_x - 5, center_y - 10),
            (center_x + 8, center_y - 5),
            (center_x - 5, center_y)
        ]
        pygame.draw.polygon(self.screen, COLOR_FLAG, flag_points)

    def _draw_game_over(self) -> None:
        """Draw game over overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if self.grid.won:
            title_text = self.large_font.render("YOU WIN!", True, (100, 200, 120))
        else:
            title_text = self.large_font.render("GAME OVER", True, COLOR_MINE)

        score_text = self.font.render(
            f"Cells Revealed: {self.grid.revealed_count}",
            True, COLOR_TEXT
        )
        reward_text = self.font.render(
            f"Total Reward: {self.grid.total_reward:.1f}",
            True, COLOR_TEXT
        )
        restart_text = self.small_font.render("Press R or SPACE to play again", True, COLOR_TEXT_DIM)
        quit_text = self.small_font.render("Press ESC to quit", True, COLOR_TEXT_DIM)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 80))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, center_y - 20))
        self.screen.blit(reward_text, (center_x - reward_text.get_width() // 2, center_y + 15))
        self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, center_y + 60))
        self.screen.blit(quit_text, (center_x - quit_text.get_width() // 2, center_y + 90))

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
