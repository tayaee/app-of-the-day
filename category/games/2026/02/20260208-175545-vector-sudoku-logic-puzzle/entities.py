"""Game entities and logic."""

import random
from typing import List, Tuple, Set
import config


class Cell:
    """Represents a single cell in the Sudoku grid."""

    def __init__(self, row: int, col: int, value: int = 0, is_given: bool = False):
        self.row = row
        self.col = col
        self.value = value
        self.is_given = is_given
        self.is_error = False
        self.is_selected = False

    def set_value(self, value: int) -> None:
        """Set the cell value."""
        if not self.is_given:
            self.value = value

    def clear(self) -> None:
        """Clear the cell value if not given."""
        if not self.is_given:
            self.value = config.EMPTY_CELL
            self.is_error = False


class SudokuBoard:
    """Manages the Sudoku puzzle generation and validation."""

    def __init__(self, seed: int = None):
        self.grid: List[List[int]] = [[config.EMPTY_CELL for _ in range(config.GRID_SIZE)]
                                       for _ in range(config.GRID_SIZE)]
        self.solution: List[List[int]] = [[config.EMPTY_CELL for _ in range(config.GRID_SIZE)]
                                           for _ in range(config.GRID_SIZE)]
        self.given_cells: Set[Tuple[int, int]] = set()
        self.seed = seed or random.randint(1, 999999)
        random.seed(self.seed)

    def generate_puzzle(self, num_clues: int = 32) -> None:
        """Generate a new Sudoku puzzle with the specified number of clues."""
        # Generate a complete valid solution
        self._generate_solution()

        # Copy solution to grid
        self.grid = [row[:] for row in self.solution]

        # Remove numbers to create the puzzle
        cells_to_remove = config.GRID_SIZE * config.GRID_SIZE - num_clues
        self._remove_numbers(cells_to_remove)

        # Mark given cells
        self.given_cells.clear()
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                if self.grid[row][col] != config.EMPTY_CELL:
                    self.given_cells.add((row, col))

    def _generate_solution(self) -> None:
        """Generate a complete valid Sudoku solution using backtracking."""
        self.solution = [[config.EMPTY_CELL for _ in range(config.GRID_SIZE)]
                         for _ in range(config.GRID_SIZE)]
        self._fill_grid(self.solution)

    def _fill_grid(self, grid: List[List[int]]) -> bool:
        """Fill the grid using backtracking algorithm."""
        empty_cell = self._find_empty(grid)
        if not empty_cell:
            return True

        row, col = empty_cell
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for num in numbers:
            if self._is_valid_placement(grid, row, col, num):
                grid[row][col] = num
                if self._fill_grid(grid):
                    return True
                grid[row][col] = config.EMPTY_CELL

        return False

    def _find_empty(self, grid: List[List[int]]) -> Tuple[int, int] | None:
        """Find an empty cell in the grid."""
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                if grid[row][col] == config.EMPTY_CELL:
                    return (row, col)
        return None

    def _is_valid_placement(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing a number at a position is valid."""
        # Check row
        if num in grid[row]:
            return False

        # Check column
        for r in range(config.GRID_SIZE):
            if grid[r][col] == num:
                return False

        # Check 3x3 box
        box_row = (row // config.BOX_SIZE) * config.BOX_SIZE
        box_col = (col // config.BOX_SIZE) * config.BOX_SIZE
        for r in range(box_row, box_row + config.BOX_SIZE):
            for c in range(box_col, box_col + config.BOX_SIZE):
                if grid[r][c] == num:
                    return False

        return True

    def _remove_numbers(self, count: int) -> None:
        """Remove numbers from the grid to create the puzzle."""
        positions = [(r, c) for r in range(config.GRID_SIZE)
                     for c in range(config.GRID_SIZE)]
        random.shuffle(positions)

        for row, col in positions[:count]:
            self.grid[row][col] = config.EMPTY_CELL

    def is_given(self, row: int, col: int) -> bool:
        """Check if a cell is a given clue."""
        return (row, col) in self.given_cells

    def check_solution(self, grid: List[List[Cell]]) -> bool:
        """Check if the current grid state matches the solution."""
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                if grid[row][col].value != self.solution[row][col]:
                    return False
        return True

    def validate_placement(self, row: int, col: int, value: int) -> bool:
        """Validate if a value can be placed at a position."""
        if value == config.EMPTY_CELL:
            return True

        # Check row
        for c in range(config.GRID_SIZE):
            if c != col and self.solution[row][c] == value:
                return False

        # Check column
        for r in range(config.GRID_SIZE):
            if r != row and self.solution[r][col] == value:
                return False

        # Check 3x3 box
        box_row = (row // config.BOX_SIZE) * config.BOX_SIZE
        box_col = (col // config.BOX_SIZE) * config.BOX_SIZE
        for r in range(box_row, box_row + config.BOX_SIZE):
            for c in range(box_col, box_col + config.BOX_SIZE):
                if (r != row or c != col) and self.solution[r][c] == value:
                    return False

        return True

    def has_conflict(self, row: int, col: int, value: int, current_grid: List[List[Cell]]) -> bool:
        """Check if placing a value causes a conflict with current grid state."""
        if value == config.EMPTY_CELL:
            return False

        # Check row
        for c in range(config.GRID_SIZE):
            if c != col and current_grid[row][c].value == value:
                return True

        # Check column
        for r in range(config.GRID_SIZE):
            if r != row and current_grid[r][col].value == value:
                return True

        # Check 3x3 box
        box_row = (row // config.BOX_SIZE) * config.BOX_SIZE
        box_col = (col // config.BOX_SIZE) * config.BOX_SIZE
        for r in range(box_row, box_row + config.BOX_SIZE):
            for c in range(box_col, box_col + config.BOX_SIZE):
                if (r != row or c != col) and current_grid[r][c].value == value:
                    return True

        return False

    def is_complete(self, grid: List[List[Cell]]) -> bool:
        """Check if the grid is completely filled."""
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                if grid[row][col].value == config.EMPTY_CELL:
                    return False
        return True


class GameState:
    """Manages the overall game state."""

    def __init__(self):
        self.board = SudokuBoard()
        self.cells: List[List[Cell]] = []
        self.selected_cell: Tuple[int, int] | None = None
        self.score = 0
        self.is_won = False
        self.moves = 0
        self.new_game()

    def new_game(self) -> None:
        """Start a new game."""
        self.board = SudokuBoard()
        self.board.generate_puzzle(random.randint(config.MIN_CLUES, config.MAX_CLUES))
        self._initialize_cells()
        self.selected_cell = None
        self.score = 0
        self.is_won = False
        self.moves = 0

    def _initialize_cells(self) -> None:
        """Initialize the cell grid from the board."""
        self.cells = []
        for row in range(config.GRID_SIZE):
            cell_row = []
            for col in range(config.GRID_SIZE):
                value = self.board.grid[row][col]
                is_given = self.board.is_given(row, col)
                cell_row.append(Cell(row, col, value, is_given))
            self.cells.append(cell_row)

    def select_cell(self, row: int, col: int) -> None:
        """Select a cell."""
        # Deselect previous cell
        if self.selected_cell:
            prev_row, prev_col = self.selected_cell
            self.cells[prev_row][prev_col].is_selected = False

        # Select new cell
        self.selected_cell = (row, col)
        self.cells[row][col].is_selected = True

    def set_cell_value(self, value: int) -> Tuple[bool, int]:
        """Set the value of the selected cell. Returns (is_correct, score_change)."""
        if not self.selected_cell or self.is_won:
            return (False, 0)

        row, col = self.selected_cell
        cell = self.cells[row][col]

        if cell.is_given:
            return (False, 0)

        old_value = cell.value
        cell.set_value(value)

        self.moves += 1

        # Check if the placement is correct
        if value == config.EMPTY_CELL:
            cell.is_error = False
            return (True, 0)
        elif value == self.board.solution[row][col]:
            cell.is_error = False
            self.score += config.SCORE_CORRECT

            # Check for win condition
            if self.board.is_complete(self.cells):
                self.is_won = self.board.check_solution(self.cells)

            return (True, config.SCORE_CORRECT)
        else:
            cell.is_error = True
            self.score += config.SCORE_INCORRECT
            return (False, config.SCORE_INCORRECT)

    def clear_selected_cell(self) -> None:
        """Clear the selected cell value."""
        if self.selected_cell and not self.is_won:
            row, col = self.selected_cell
            self.cells[row][col].clear()

    def get_cell_at_pos(self, x: int, y: int) -> Tuple[int, int] | None:
        """Get the cell at the given screen position."""
        if x < config.GRID_OFFSET_X or x > config.GRID_OFFSET_X + config.GRID_SIZE * config.CELL_SIZE:
            return None
        if y < config.GRID_OFFSET_Y or y > config.GRID_OFFSET_Y + config.GRID_SIZE * config.CELL_SIZE:
            return None

        col = (x - config.GRID_OFFSET_X) // config.CELL_SIZE
        row = (y - config.GRID_OFFSET_Y) // config.CELL_SIZE

        if 0 <= row < config.GRID_SIZE and 0 <= col < config.GRID_SIZE:
            return (row, col)
        return None

    def update_errors(self) -> None:
        """Update error states for all user-filled cells."""
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                cell = self.cells[row][col]
                if not cell.is_given and cell.value != config.EMPTY_CELL:
                    cell.is_error = self.board.has_conflict(row, col, cell.value, self.cells)
                elif cell.value == config.EMPTY_CELL:
                    cell.is_error = False
