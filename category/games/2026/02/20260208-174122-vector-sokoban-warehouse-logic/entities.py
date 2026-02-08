"""Game entities for Sokoban."""

from typing import List, Tuple, Optional, Set
from config import *


class GameState:
    """Represents the current state of the Sokoban game."""

    def __init__(self, level_index: int = 0):
        self.level_index = level_index
        self.grid: List[List[int]] = []
        self.worker_pos: Tuple[int, int] = (0, 0)
        self.boxes: Set[Tuple[int, int]] = set()
        self.targets: Set[Tuple[int, int]] = set()
        self.rows = 0
        self.cols = 0
        self.total_reward = 0.0
        self.move_count = 0
        self.level_complete = False
        self.game_won = False
        self.deadlocked = False

        self._load_level(level_index)

    def _load_level(self, level_index: int) -> None:
        """Load a level from the predefined levels."""
        if level_index >= len(LEVELS):
            self.game_won = True
            self.level_complete = True
            return

        level_layout = LEVELS[level_index]
        self.rows = len(level_layout)
        self.cols = len(level_layout[0])

        self.grid = []
        self.boxes = set()
        self.targets = set()

        for row_idx, row in enumerate(level_layout):
            grid_row = []
            for col_idx, char in enumerate(row):
                if char == '#':
                    grid_row.append(STATE_WALL)
                elif char == '.':
                    grid_row.append(STATE_FLOOR)
                elif char == '*':
                    grid_row.append(STATE_TARGET)
                    self.targets.add((row_idx, col_idx))
                elif char == '$':
                    grid_row.append(STATE_FLOOR)
                    self.boxes.add((row_idx, col_idx))
                elif char == '@':
                    grid_row.append(STATE_FLOOR)
                    self.worker_pos = (row_idx, col_idx)
                elif char == '+':
                    grid_row.append(STATE_TARGET)
                    self.targets.add((row_idx, col_idx))
                    self.worker_pos = (row_idx, col_idx)
                elif char == '%':
                    grid_row.append(STATE_TARGET)
                    self.targets.add((row_idx, col_idx))
                    self.boxes.add((row_idx, col_idx))
                else:
                    grid_row.append(STATE_FLOOR)
            self.grid.append(grid_row)

    def move(self, dx: int, dy: int) -> bool:
        """Attempt to move the worker. Returns True if move was successful."""
        if self.level_complete or self.deadlocked:
            return False

        new_x = self.worker_pos[0] + dx
        new_y = self.worker_pos[1] + dy

        # Check bounds
        if not (0 <= new_x < self.rows and 0 <= new_y < self.cols):
            self.total_reward += PENALTY_INVALID
            return False

        # Check wall
        if self.grid[new_x][new_y] == STATE_WALL:
            self.total_reward += PENALTY_INVALID
            return False

        # Check if there's a box
        if (new_x, new_y) in self.boxes:
            box_new_x = new_x + dx
            box_new_y = new_y + dy

            # Check if box can be pushed
            if not (0 <= box_new_x < self.rows and 0 <= box_new_y < self.cols):
                self.total_reward += PENALTY_INVALID
                return False

            if self.grid[box_new_x][box_new_y] == STATE_WALL:
                self.total_reward += PENALTY_INVALID
                return False

            if (box_new_x, box_new_y) in self.boxes:
                self.total_reward += PENALTY_INVALID
                return False

            # Move the box
            was_on_target = (new_x, new_y) in self.targets
            self.boxes.remove((new_x, new_y))
            self.boxes.add((box_new_x, box_new_y))

            is_on_target = (box_new_x, box_new_y) in self.targets
            if is_on_target and not was_on_target:
                self.total_reward += REWARD_BOX_ON_TARGET

            # Check for deadlock after box push
            self._check_deadlock()

        # Move the worker
        self.worker_pos = (new_x, new_y)
        self.move_count += 1
        self.total_reward += PENALTY_MOVE

        # Check win condition
        self._check_win_condition()

        return True

    def _check_win_condition(self) -> None:
        """Check if all boxes are on targets."""
        for box in self.boxes:
            if box not in self.targets:
                return

        self.level_complete = True
        if self.level_index >= len(LEVELS) - 1:
            self.game_won = True
        self.total_reward += REWARD_LEVEL_COMPLETE

    def _check_deadlock(self) -> None:
        """Check if any box is in a deadlock position (cannot be moved to a target)."""
        for box in self.boxes:
            if box in self.targets:
                continue

            x, y = box
            # A box is deadlocked if it's in a corner and not on a target
            # Check if adjacent cells are walls
            walls = 0
            if x > 0 and self.grid[x - 1][y] == STATE_WALL:
                walls += 1
            if x < self.rows - 1 and self.grid[x + 1][y] == STATE_WALL:
                walls += 1
            if y > 0 and self.grid[x][y - 1] == STATE_WALL:
                walls += 1
            if y < self.cols - 1 and self.grid[x][y + 1] == STATE_WALL:
                walls += 1

            # Check if boxed in by other boxes
            boxes = 0
            if (x - 1, y) in self.boxes:
                boxes += 1
            if (x + 1, y) in self.boxes:
                boxes += 1
            if (x, y - 1) in self.boxes:
                boxes += 1
            if (x, y + 1) in self.boxes:
                boxes += 1

            obstacles = walls + boxes
            if obstacles >= 2:
                # Check if it's a corner deadlock
                horizontal_blocked = (x > 0 and self.grid[x - 1][y] == STATE_WALL) or \
                                    (x < self.rows - 1 and self.grid[x + 1][y] == STATE_WALL) or \
                                    ((x - 1, y) in self.boxes) or ((x + 1, y) in self.boxes)
                vertical_blocked = (y > 0 and self.grid[x][y - 1] == STATE_WALL) or \
                                  (y < self.cols - 1 and self.grid[x][y + 1] == STATE_WALL) or \
                                  ((x, y - 1) in self.boxes) or ((x, y + 1) in self.boxes)

                if horizontal_blocked and vertical_blocked:
                    self.deadlocked = True

    def next_level(self) -> None:
        """Advance to the next level."""
        if self.level_index < len(LEVELS) - 1:
            self.level_index += 1
            self._reset_level()

    def reset_level(self) -> None:
        """Reset the current level."""
        self._reset_level()

    def _reset_level(self) -> None:
        """Reset to the initial state of the current level."""
        self.total_reward = 0.0
        self.move_count = 0
        self.level_complete = False
        self.deadlocked = False
        self._load_level(self.level_index)

    def get_state(self) -> List[List[int]]:
        """Get the current grid state for AI agents."""
        state = [row[:] for row in self.grid]

        # Place boxes
        for box in self.boxes:
            x, y = box
            if (x, y) in self.targets:
                state[x][y] = STATE_BOX_ON_TARGET
            else:
                state[x][y] = STATE_BOX

        # Place worker
        wx, wy = self.worker_pos
        if state[wx][wy] == STATE_BOX:
            state[wx][wy] = STATE_BOX
        elif state[wx][wy] == STATE_BOX_ON_TARGET:
            state[wx][wy] = STATE_BOX_ON_TARGET
        else:
            state[wx][wy] = STATE_WORKER

        return state

    def get_boxes_on_targets(self) -> int:
        """Count how many boxes are on targets."""
        count = 0
        for box in self.boxes:
            if box in self.targets:
                count += 1
        return count

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is valid for movement."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        return self.grid[row][col] != STATE_WALL
