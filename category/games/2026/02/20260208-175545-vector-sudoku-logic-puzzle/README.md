# Vector Sudoku Logic Puzzle

Challenge your mind with the ultimate logic-based number placement classic.

## Overview

Sudoku is a globally recognized puzzle that sharpens logical thinking and pattern recognition. This implementation features a minimalist UI with monochromatic styling and a seed-based puzzle generator for reproducible boards.

## Game Rules

- **Grid**: 9x9 grid divided into nine 3x3 subgrids (boxes)
- **Objective**: Fill all empty cells with digits 1-9
- **Constraints**:
  - Each row must contain all digits 1-9 without repetition
  - Each column must contain all digits 1-9 without repetition
  - Each 3x3 box must contain all digits 1-9 without repetition
- **Win Condition**: All cells filled correctly according to Sudoku rules

## How to Play

1. Click on an empty cell to select it
2. Press numeric keys (1-9) to input a number
3. Press Backspace, Delete, or 0 to clear a cell
4. Conflicting entries are highlighted in red
5. Press ESC to quit

## Scoring

- +10 points for each correct number placed
- -5 points for each incorrect placement
- Maximum score: 810 points (81 cells x 10 points)

## Build and Run

```bash
# Create virtual environment and install dependencies
uv venv && uv sync

# Start the game
uv run main.py
```

## Project Structure

```
vector-sudoku-logic-puzzle/
├── main.py          # Entry point
├── game.py          # Game loop and rendering
├── entities.py      # Game logic and state classes
├── config.py        # Constants and configuration
├── appinfo.json     # App metadata
├── pyproject.toml   # Dependencies
└── README.md        # This file
```

## Technical Details

- **Language**: Python 3.12+
- **Library**: Pygame
- **Algorithm**: Backtracking with randomization for puzzle generation
- **UI**: Minimalist monochromatic design
