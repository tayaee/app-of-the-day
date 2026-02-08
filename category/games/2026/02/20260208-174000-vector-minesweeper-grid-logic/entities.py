"""Grid and Cell entities for Minesweeper."""

import random
from typing import List, Tuple, Optional
from config import *


class Cell:
    """Represents a single cell in the minesweeper grid."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0

    def reveal(self) -> bool:
        """Reveal the cell. Returns True if safe, False if mine."""
        if self.is_revealed or self.is_flagged:
            return True

        self.is_revealed = True
        return not self.is_mine

    def toggle_flag(self) -> None:
        """Toggle the flag state of the cell."""
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged

    def get_state(self) -> int:
        """Get the state representation for AI agents."""
        if self.is_flagged:
            return CELL_FLAGGED
        if not self.is_revealed:
            return CELL_HIDDEN
        return self.neighbor_mines


class Grid:
    """Represents the minesweeper game grid."""

    def __init__(self):
        self.rows = GRID_ROWS
        self.cols = GRID_COLS
        self.mines = TOTAL_MINES
        self.cells: List[List[Cell]] = []
        self.game_over = False
        self.won = False
        self.revealed_count = 0
        self.flagged_count = 0
        self.total_reward = 0.0

        self._initialize_cells()
        self._place_mines()
        self._calculate_neighbors()

    def _initialize_cells(self) -> None:
        """Initialize all cells in the grid."""
        self.cells = [
            [Cell(row, col) for col in range(self.cols)]
            for row in range(self.rows)
        ]

    def _place_mines(self) -> None:
        """Randomly place mines in the grid."""
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        mine_positions = random.sample(positions, self.mines)

        for row, col in mine_positions:
            self.cells[row][col].is_mine = True

    def _calculate_neighbors(self) -> None:
        """Calculate mine count for each cell."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.cells[row][col].is_mine:
                    continue
                self.cells[row][col].neighbor_mines = self._count_adjacent_mines(row, col)

    def _count_adjacent_mines(self, row: int, col: int) -> int:
        """Count mines in adjacent cells."""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.cells[nr][nc].is_mine:
                        count += 1
        return count

    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Get a cell at the given position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None

    def reveal(self, row: int, col: int) -> bool:
        """Reveal a cell. Returns True if safe, False if mine."""
        if self.game_over:
            return True

        cell = self.get_cell(row, col)
        if not cell or cell.is_revealed or cell.is_flagged:
            self.total_reward += PENALTY_INVALID
            return True

        if not cell.reveal():
            self._game_over(won=False)
            return False

        self.revealed_count += 1
        self.total_reward += REWARD_SAFE_REVEAL

        # Auto-reveal empty cells
        if cell.neighbor_mines == 0:
            self._reveal_adjacent(row, col)

        # Check win condition
        safe_cells = self.rows * self.cols - self.mines
        if self.revealed_count == safe_cells:
            self._game_over(won=True)

        return True

    def _reveal_adjacent(self, row: int, col: int) -> None:
        """Reveal adjacent cells recursively."""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    cell = self.cells[nr][nc]
                    if not cell.is_revealed and not cell.is_flagged:
                        self.reveal(nr, nc)

    def toggle_flag(self, row: int, col: int) -> None:
        """Toggle flag on a cell."""
        if self.game_over:
            return

        cell = self.get_cell(row, col)
        if cell and not cell.is_revealed:
            cell.toggle_flag()
            if cell.is_flagged:
                self.flagged_count += 1
            else:
                self.flagged_count -= 1

    def _game_over(self, won: bool) -> None:
        """Handle game over state."""
        self.game_over = True
        self.won = won

        if won:
            self.total_reward += REWARD_WIN
        else:
            self.total_reward += PENALTY_MINE
            # Reveal all mines
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.cells[row][col].is_mine:
                        self.cells[row][col].is_revealed = True

    def reset(self) -> None:
        """Reset the grid for a new game."""
        self.cells = []
        self.game_over = False
        self.won = False
        self.revealed_count = 0
        self.flagged_count = 0
        self.total_reward = 0.0

        self._initialize_cells()
        self._place_mines()
        self._calculate_neighbors()

    def get_state(self) -> List[List[int]]:
        """Get the current grid state for AI agents."""
        return [
            [cell.get_state() for cell in row]
            for row in self.cells
        ]

    def get_adjacent_hidden(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get list of adjacent hidden cell positions."""
        hidden = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    cell = self.cells[nr][nc]
                    if not cell.is_revealed and not cell.is_flagged:
                        hidden.append((nr, nc))
        return hidden

    def get_adjacent_flags(self, row: int, col: int) -> int:
        """Count flagged cells adjacent to position."""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.cells[nr][nc].is_flagged:
                        count += 1
        return count
