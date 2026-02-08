"""Game configuration and constants."""

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
UI_HEIGHT = 80

# Grid
TILE_SIZE = 50
GRID_OFFSET_X = (SCREEN_WIDTH - 12 * TILE_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - 10 * TILE_SIZE) // 2 + 20

# Game state representation for AI
STATE_FLOOR = 0
STATE_WALL = 1
STATE_TARGET = 2
STATE_BOX = 3
STATE_WORKER = 4
STATE_BOX_ON_TARGET = 5

# Colors (professional vector style)
COLOR_BG = (18, 18, 22)
COLOR_UI_BG = (22, 22, 26)
COLOR_BORDER = (60, 60, 70)
COLOR_TEXT = (220, 220, 220)
COLOR_TEXT_DIM = (150, 150, 150)

# Tile colors
COLOR_FLOOR = (35, 35, 40)
COLOR_WALL = (50, 50, 55)
COLOR_WALL_OUTLINE = (70, 70, 80)
COLOR_TARGET = (80, 80, 90)
COLOR_TARGET_OUTLINE = (100, 100, 110)
COLOR_BOX = (60, 100, 140)
COLOR_BOX_OUTLINE = (80, 120, 160)
COLOR_BOX_ON_TARGET = (80, 160, 100)
COLOR_BOX_ON_TARGET_OUTLINE = (100, 180, 120)
COLOR_WORKER = (180, 120, 60)
COLOR_WORKER_OUTLINE = (200, 140, 80)

# Game state rewards
REWARD_BOX_ON_TARGET = 100.0
REWARD_LEVEL_COMPLETE = 500.0
PENALTY_MOVE = -1.0
PENALTY_INVALID = -0.5

# Frame rate
FPS = 60

# Level layouts (# = wall, . = floor, @ = worker, $ = box, * = target, + = worker on target, % = box on target)
LEVELS = [
    [
        "##########",
        "#........#",
        "#.*.$.*..#",
        "#...$....#",
        "#.@......#",
        "##########",
    ],
    [
        "##########",
        "#.*......#",
        "#...$$...#",
        "#...$$...#",
        "#.*...@..#",
        "##########",
    ],
    [
        "############",
        "#..........#",
        "#.*.*.$.$..#",
        "#...$......#",
        "#...$...@..#",
        "############",
    ],
    [
        "############",
        "#..........#",
        "#.*.*.*.*..#",
        "#.$.$.$.$..#",
        "#....@.....#",
        "############",
    ],
    [
        "##############",
        "#............#",
        "#.*.*.$.$.*..#",
        "#...$...$....#",
        "#...$...$...@#",
        "##############",
    ],
]
