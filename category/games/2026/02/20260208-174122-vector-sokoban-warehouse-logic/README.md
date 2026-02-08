# Vector Sokoban Warehouse Logic

A minimalist puzzle game where you push boxes to designated storage locations in a crowded warehouse.

## Description

A classic Sokoban implementation featuring 5 progressively challenging levels. The player controls a warehouse worker who must push boxes onto target locations. The game features a clean vector aesthetic with professional colors and smooth movement. Boxes change color when placed on targets, providing clear visual feedback.

## Rationale

Sokoban is a classic transport puzzle that challenges spatial reasoning and path planning. It provides a perfect environment for AI agents to practice reinforcement learning in discrete state spaces with irreversible moves. The NP-complete nature of Sokoban makes it an excellent benchmark for planning algorithms and heuristic search methods.

## Details

The game consists of a 2D grid containing walls, empty spaces, boxes, and storage targets. The player controls a warehouse worker who can push boxes but cannot pull them. Each level presents a unique configuration that requires strategic thinking to solve without creating deadlocks.

**Key Rules:**
1. The worker can move up, down, left, and right to empty squares
2. The worker can push a single box into an empty square or onto a target square
3. The worker cannot pull boxes
4. Boxes cannot be pushed into walls or other boxes
5. The level is cleared when all boxes are positioned on target squares

## Build

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## Stop

Press `ESC` or close the window.

## How to Play

- **Arrow Keys / WASD** - Move the worker
- **R** - Restart the current level
- **N** - Advance to the next level (after completing current level)
- **ESC** - Quit

**Scoring:**
- +100 reward for each box placed on a target
- -1 penalty per move (encourages efficiency)
- +500 bonus for completing a level
- -0.5 penalty for invalid moves

**Goal:** Push all boxes onto the target circles (marked with hollow circles). Avoid pushing boxes into corners where they cannot be retrieved.

## AI Agent Input

For RL agent control:

**State Space:**
- 2D grid array with values:
  - 0: Floor
  - 1: Wall
  - 2: Target
  - 3: Box
  - 4: Worker
  - 5: Box on Target

**Action Space:**
- Discrete(4): Up, Down, Left, Right

**Reward Structure:**
- Box on target: +100.0
- Level complete: +500.0
- Move penalty: -1.0
- Invalid move: -0.5

**Deadlock Detection:**
The game automatically detects when a box is pushed into a position where it can no longer reach a target (cornered by walls or other boxes).

## Project Structure

```
category/games/2026/02/20260208-174122-vector-sokoban-warehouse-logic/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── entities.py      - GameState class with movement logic
├── config.py        - Game constants, colors, and level layouts
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x640
- **Grid Size**: Variable (up to 12x10 tiles, 50px each)
- **Levels**: 5 progressive difficulty levels
- **Frame Rate**: 60 FPS
- **Game Engine**: Pygame 2.0+
