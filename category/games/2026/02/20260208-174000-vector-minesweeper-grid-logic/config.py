"""Game configuration and constants."""

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
UI_HEIGHT = 80

# Grid
GRID_COLS = 10
GRID_ROWS = 10
CELL_SIZE = 50
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_COLS * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_ROWS * CELL_SIZE) // 2 + 20

# Mines
TOTAL_MINES = 10

# Colors (professional gray and blue tones)
COLOR_BG = (18, 18, 22)
COLOR_GRID = (35, 35, 40)
COLOR_BORDER = (60, 60, 70)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_DIM = (150, 150, 150)

# Cell states
CELL_HIDDEN = -1
CELL_FLAGGED = -2

# Cell colors
COLOR_CELL_HIDDEN = (45, 45, 52)
COLOR_CELL_REVEALED = (25, 25, 30)
COLOR_CELL_HOVER = (55, 55, 65)
COLOR_MINE = (200, 60, 60)
COLOR_FLAG = (220, 180, 60)

# Number colors
COLOR_NUMBERS = {
    0: (80, 80, 90),
    1: (100, 150, 220),
    2: (80, 170, 120),
    3: (220, 90, 90),
    4: (100, 90, 180),
    5: (180, 100, 60),
    6: (80, 180, 180),
    7: (150, 150, 150),
    8: (100, 100, 100),
}

# Game state rewards
REWARD_SAFE_REVEAL = 1.0
REWARD_WIN = 100.0
PENALTY_MINE = -100.0
PENALTY_INVALID = -0.1

# Frame rate
FPS = 60
