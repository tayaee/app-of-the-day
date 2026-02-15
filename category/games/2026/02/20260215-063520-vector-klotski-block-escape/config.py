"""Configuration for Vector Klotski Block Escape."""

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600
GRID_OFFSET_X = 180
GRID_OFFSET_Y = 80

# Grid configuration (4 columns x 5 rows)
GRID_COLS = 4
GRID_ROWS = 5
CELL_SIZE = 80

# Colors (R, G, B)
COLOR_BG = (15, 15, 25)
COLOR_GRID = (50, 50, 70)
COLOR_KING_BLOCK = (220, 60, 60)
COLOR_KING_BORDER = (180, 30, 30)
COLOR_VERTICAL_BLOCK = (60, 120, 220)
COLOR_VERTICAL_BORDER = (30, 90, 180)
COLOR_HORIZONTAL_BLOCK = (60, 180, 120)
COLOR_HORIZONTAL_BORDER = (30, 150, 90)
COLOR_SMALL_BLOCK = (180, 180, 60)
COLOR_SMALL_BORDER = (150, 150, 30)
COLOR_EMPTY = (25, 25, 35)
COLOR_EXIT = (40, 100, 40)
COLOR_EXIT_BORDER = (60, 140, 60)
COLOR_TEXT = (220, 220, 220)
COLOR_PANEL = (25, 25, 35)
COLOR_HIGHLIGHT = (255, 255, 100)
COLOR_SELECTED = (255, 255, 255)

# Block types
EMPTY = 0
KING_2x2 = 1      # The main 2x2 block to escape
VERTICAL_1x2 = 2   # 1x2 vertical block
HORIZONTAL_2x1 = 3  # 2x1 horizontal block
SMALL_1x1 = 4      # 1x1 small block

# Directions (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Font sizes
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 16

# Animation
MOVE_SPEED = 8  # pixels per frame

# Classic Klotski starting layout
# Grid: 4x5, King at top center, various obstacles
STARTING_LAYOUT = [
    [VERTICAL_1x2, KING_2x2, KING_2x2, VERTICAL_1x2],
    [VERTICAL_1x2, KING_2x2, KING_2x2, VERTICAL_1x2],
    [VERTICAL_1x2, HORIZONTAL_2x1, HORIZONTAL_2x1, VERTICAL_1x2],
    [VERTICAL_1x2, SMALL_1x1, SMALL_1x1, VERTICAL_1x2],
    [EMPTY, EMPTY, EMPTY, EMPTY],
]

# Alternative easier layout for testing
EASY_LAYOUT = [
    [EMPTY, KING_2x2, KING_2x2, EMPTY],
    [EMPTY, KING_2x2, KING_2x2, EMPTY],
    [VERTICAL_1x2, EMPTY, EMPTY, VERTICAL_1x2],
    [VERTICAL_1x2, SMALL_1x1, SMALL_1x1, VERTICAL_1x2],
    [EMPTY, EMPTY, EMPTY, EMPTY],
]
