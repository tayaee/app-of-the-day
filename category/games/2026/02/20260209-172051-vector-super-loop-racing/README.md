# Vector Super Loop Racing

High-speed 2D racing game where you maintain momentum through complex loops and sharp turns.

## Description

This game focuses on physics-based speed management and precise steering. It targets players who enjoy classic arcade racers like Super Hang-On or F-Zero but simplified for grid-based or vector environments. It is ideal for testing AI agents on continuous control and path optimization.

## Features

- Momentum-based acceleration and centrifugal force on curves
- Circular track with inner and outer boundaries
- Speed boosters (green zones) and oil slicks (blue zones)
- Health system with wall collision penalties
- Lap counting and distance-based scoring
- 120-second time limit

## How to Build

```bash
uv init
uv add pygame-ce
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

Press the `ESC` key or close the game window.

## How to Play

- `UP` / `W`: Accelerate
- `DOWN` / `S`: Brake
- `LEFT` / `A`: Steer left
- `RIGHT` / `D`: Steer right
- `SPACE`: Restart (when game over)
- `ESC`: Quit

Score increases based on distance traveled and speed maintained. Crossing the finish line adds bonus points and heals damage. Avoid hitting the red track borders.

## Technical Specs

- Engine: Pygame
- Resolution: 800x600
- Physics: Momentum-based acceleration and centrifugal force
- Input: Discrete or continuous keyboard events

## Cleanup

```bash
rm -rf .venv && rm pyproject.toml
```
