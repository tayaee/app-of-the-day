# Vector Klotski Block Escape

Master the classic sliding block puzzle to guide the main red block to freedom.

## Description

A strategic sliding block puzzle where you navigate a 2x2 "King" block through a crowded 4x5 grid to reach the bottom-center exit. Each move matters in this test of spatial reasoning and long-term planning.

## Game Rules

- **Grid**: 4 columns x 5 rows
- **Goal**: Move the 2x2 red King block to the bottom-center exit position
- **Blocks**: Various sizes (1x1, 1x2, 2x1, 2x2) that slide into empty spaces
- **Constraints**: Blocks cannot overlap or move outside the grid
- **Scoring**: Score = 10000 / total_moves (fewer moves = higher score)

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC in the game window or close the window.

## How to Play

1. **Select a block**: Click on any block to select it (selected blocks have a white border)
2. **Move blocks**: Use Arrow Keys to move the selected block
3. **Reach the exit**: Guide the red 2x2 King block to the bottom-center position marked in green

**Controls**:
- Click: Select/deselect blocks
- Arrow Keys: Move selected block
- R: Reset puzzle
- E: Toggle easy/hard layout

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Details

- **Observation Space**: 4x5 integer matrix representing block IDs and positions
- **Action Space**: Select block + Direction (Up, Down, Left, Right)
- **Framework**: Pygame
- **Python**: 3.12-3.13

## Rationale

This game focuses on spatial reasoning and pathfinding. It is ideal for training AI agents in long-term planning and state-space search algorithms, as every move counts towards an optimal solution.
