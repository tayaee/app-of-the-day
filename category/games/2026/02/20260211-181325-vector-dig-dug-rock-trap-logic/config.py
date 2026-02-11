"""Configuration constants for Dig Dug Rock Trap Logic."""

# Window settings
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
FPS = 60

# Grid settings
GRID_COLS = 20
GRID_ROWS = 15
CELL_SIZE = 48

# Colors
COLOR_BG = (20, 10, 5)  # Dark soil background
COLOR_SOIL = (139, 69, 19)  # Brown soil
COLOR_TUNNEL = (30, 15, 10)  # Dark tunnel
COLOR_ROCK = (128, 128, 128)  # Gray rock
COLOR_PLAYER = (0, 255, 0)  # Green player
COLOR_POOKA = (255, 100, 0)  # Orange Pooka
COLOR_FYGAR = (255, 0, 100)  # Red/magenta Fygar
COLOR_PUMP = (255, 255, 0)  # Yellow pump wire
COLOR_TEXT = (255, 255, 255)  # White text
COLOR_HUD = (50, 50, 50)  # Dark HUD background

# Game settings
PLAYER_MOVE_DELAY = 8  # Frames between player moves
PUMP_RANGE = 3  # Range of pump in cells
PUMP_DURATION = 30  # Frames pump stays active
INFLATION_REQUIRED = 3  # Pump hits needed to kill enemy
INFLATION_DECAY = 60  # Frames before enemy deflates

# Enemy settings
POOKA_MOVE_DELAY = 15  # Frames between Pooka moves
FYGAR_MOVE_DELAY = 18  # Frames between Fygar moves
FYGAR_BREATH_RANGE = 4  # Range of Fygar fire breath
FYGAR_BREATH_COOLDOWN = 180  # Frames between fire breaths

# Rock settings
FALL_DELAY = 30  # Frames before rock starts falling
FALL_SPEED = 4  # Frames per cell when falling

# Scoring
SCORE_DIG_SOIL = 10
SCORE_PUMP_KILL = 200
SCORE_ROCK_KILL_1 = 1000
SCORE_ROCK_KILL_2 = 2500
SCORE_ENEMY_PASS = 500  # Bonus for clearing all enemies

# Direction vectors
DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0)
}

# Cell types
CELL_SOIL = 0
CELL_TUNNEL = 1
