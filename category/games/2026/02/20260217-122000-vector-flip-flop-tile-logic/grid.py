"""Grid class for Lights Out game logic."""

from config import GRID_SIZE
import copy


class Grid:
    """Represents the game grid and handles tile flipping logic."""

    def __init__(self, size=None):
        """Initialize a grid with all tiles off (black)."""
        self.size = size if size is not None else GRID_SIZE
        self.tiles = [[False for _ in range(self.size)] for _ in range(self.size)]

    def is_on(self, row, col):
        """Check if a tile is on (white)."""
        return 0 <= row < self.size and 0 <= col < self.size and self.tiles[row][col]

    def flip(self, row, col):
        """Flip a tile and its adjacent neighbors."""
        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        # Flip the clicked tile
        self._toggle(row, col)

        # Flip adjacent neighbors
        self._toggle(row - 1, col)  # Up
        self._toggle(row + 1, col)  # Down
        self._toggle(row, col - 1)  # Left
        self._toggle(row, col + 1)  # Right

    def _toggle(self, row, col):
        """Toggle a single tile if within bounds."""
        if 0 <= row < self.size and 0 <= col < self.size:
            self.tiles[row][col] = not self.tiles[row][col]

    def is_solved(self):
        """Check if all tiles are off (black)."""
        return all(not tile for row in self.tiles for tile in row)

    def set_from_moves(self, moves):
        """Set the grid state by applying a sequence of moves to a solved grid."""
        self.tiles = [[False for _ in range(self.size)] for _ in range(self.size)]
        for row, col in moves:
            self.flip(row, col)

    def get_state(self):
        """Return the current grid state as a flat list."""
        return [tile for row in self.tiles for tile in row]

    def get_position(self, x, y, tile_size, tile_gap, offset_x, offset_y):
        """Convert screen coordinates to grid position."""
        cell_width = tile_size + tile_gap
        col = (x - offset_x) // cell_width
        row = (y - offset_y) // cell_width

        if 0 <= row < self.size and 0 <= col < self.size:
            # Verify click is within the tile (not in gap)
            tile_x = offset_x + col * cell_width
            tile_y = offset_y + row * cell_width
            if tile_x <= x < tile_x + tile_size and tile_y <= y < tile_y + tile_size:
                return row, col
        return None

    def copy(self):
        """Create a deep copy of the grid."""
        new_grid = Grid(self.size)
        new_grid.tiles = copy.deepcopy(self.tiles)
        return new_grid
