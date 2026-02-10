# Vector Frogger: Lilypad Hop

Navigate a rhythmic river crossing challenge by hopping on moving lilypads to reach the goal.

## Description

This game provides a simplified yet high-stakes environment for AI agents to learn temporal spatial reasoning and collision avoidance. It targets developers looking for a clean, physics-lite implementation of the classic river crossing mechanic without the complexity of a full traffic system.

## Details

The game consists of a grid-based river environment. The player controls a frog starting at the bottom bank. Multiple rows of lilypads move horizontally at varying speeds and directions (left to right, right to left). The frog must jump onto a lilypad to move across the river. If the frog touches the water (empty space between lilypads) or moves off-screen while on a lilypad, the game ends. The goal is to reach the top bank safely. The game increases in difficulty by increasing lilypad speed and reducing pad density as levels progress.

## Technical Specifications

- **Resolution**: 400x600
- **FPS**: 60
- **Grid Size**: 40
- **Input Type**: Discrete Keyboard
- **State Space**: Pixels or Object Coordinates (Frog_X, Frog_Y, Pad_Positions_X_Y)

## How to Build

```bash
uv run python -m pip install pygame
```

## How to Start

```bash
uv run main.py
```

## How to Stop

- Press `ESC` or close the window
- For CLI termination, use `Ctrl+C`

## How to Play

Score increases by 10 points for every forward hop (Up Arrow) and 100 points for reaching the top bank.

**Controls:**
- `Up`, `Down`, `Left`, `Right` arrows for movement
- The frog moves exactly one grid unit per key press
- The frog inherits the velocity of the lilypad it is currently standing on

## Reward Function

| Event | Reward |
|-------|--------|
| Forward Step | 1.0 |
| Goal Reached | 10.0 |
| Death (Water) | -5.0 |
| Death (Off-screen) | -5.0 |
| Time Penalty | -0.01 |

## How to Cleanup

```bash
rm -rf .venv
```
