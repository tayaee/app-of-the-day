# Vector Minesweeper Grid Logic

A minimalist logic puzzle game where you uncover safe zones while avoiding hidden mines.

## Description

A classic Minesweeper implementation on a 10x10 grid with 10 hidden mines. Each cell displays the count of adjacent mines when revealed, requiring deductive reasoning to identify safe paths. The game features a clean vector aesthetic with professional gray and blue tones.

## Rationale

Minesweeper is a timeless classic that tests deductive reasoning and pattern recognition. It provides a perfect environment for AI agents to learn decision-making under uncertainty and grid-based state estimation. The game's constraint propagation logic makes it ideal for testing logical inference algorithms.

## Details

The game consists of a 10x10 grid containing 10 randomly placed hidden mines. Each cell is initially covered. When a user reveals a cell, it either contains a mine (game over) or a number representing the count of mines in the 8 adjacent cells. If the number is 0, the surrounding cells are automatically revealed. The game is won when all 90 non-mine cells are uncovered.

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

- **Left Click** - Reveal a cell
- **Right Click** - Place/remove a flag on suspected mines
- **R / SPACE** - Start a new game
- **ESC** - Quit

**Scoring:**
- +1.0 reward per safe cell revealed
- +100.0 bonus for winning
- -100.0 penalty for hitting a mine
- -0.1 penalty for invalid moves

**Goal:** Reveal all 90 safe cells without triggering any mines.

## AI Agent Input

For RL agent control:

**State Space:**
- 10x10 grid with values:
  - -1: Hidden cell
  - -2: Flagged cell
  - 0-8: Revealed cell with adjacent mine count

**Action Space:**
- Reveal cell at (row, col)
- Flag cell at (row, col)

**Reward Structure:**
- Safe reveal: +1.0
- Win game: +100.0
- Hit mine: -100.0
- Invalid move: -0.1

**Observation Format:**
The game state can be represented as a 10x10 numpy array where each cell contains its state value. Agents should use the revealed numbers to calculate probabilities and identify safe moves through constraint satisfaction.

## Project Structure

```
category/games/2026/02/20260208-174000-vector-minesweeper-grid-logic/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── entities.py      - Grid and Cell classes
├── config.py        - Game constants and colors
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x600
- **Grid Size**: 10 cols x 10 rows (50px cells)
- **Total Mines**: 10
- **Frame Rate**: 60 FPS
- **Game Engine**: Pygame 2.0+
