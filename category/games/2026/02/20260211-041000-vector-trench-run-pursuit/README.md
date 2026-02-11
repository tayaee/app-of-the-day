# Vector Trench Run: Pursuit

Navigate a high-speed narrow corridor while dodging barriers and destroying enemy nodes.

## Description

This game challenges spatial awareness and reaction time. It targets fans of retro sci-fi flight simulators and provides a structured environment for RL agents to learn obstacle avoidance and precision targeting in a 2D pseudo-3D perspective.

The player controls a starfighter at the bottom of the screen. The game simulates a high-speed chase through a vertical trench. Barriers appear at the top and move downward, increasing in speed over time. Some barriers have a 'core node' that can be shot to clear a path. The game ends if the player collides with a wall or a barrier. The graphics use clean, single-color vector lines (white on black) to maintain a professional, minimalist aesthetic.

## Technical Specs

- **Framework**: Pygame
- **Resolution**: 800x600
- **Color Palette**: Black (#000000), White (#FFFFFF), Green (#00FF00)

## State Space

Player X position, list of active barrier Y/X coordinates, core node status

## Action Space

- Move Left
- Move Right
- Fire Weapon

## Build

```bash
uv venv
uv pip install pygame
```

## Run

```bash
uv run main.py
```

Or use the provided scripts:

- Windows: `run.bat`
- Linux/Mac: `./run.sh`

These scripts use Python 3.12 for Pygame compatibility.

## Stop

Press `ESC` or close the window.

## How to Play

- Use the **Left** and **Right Arrow** keys to navigate the ship horizontally.
- Press **Spacebar** to fire lasers at green core nodes.
- Score 10 points for every second survived.
- Score 50 points for every core node destroyed.
- Avoid white barriers at all costs.
- Press **R** to restart after game over.

## Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
```
