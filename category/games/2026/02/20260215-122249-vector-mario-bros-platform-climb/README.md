# Vector Mario Bros Platform Climb

A precision platforming challenge where you climb shifting tiers to reach the top.

## Description

Navigate through 5 vertical tiers to reach the golden goal area. Each tier features moving fireball obstacles that increase in speed as you progress. Use ladders to climb between tiers or time your jumps onto the moving elevator. The game focuses on timing, vertical navigation, and obstacle avoidance.

## Features

- 5 vertical tiers with platforms at different heights
- Horizontal fireball obstacles with varying speeds
- Ladder zones for vertical climbing
- Moving elevator platform on tier 3
- Progressive difficulty - obstacle speed increases with each tier climbed
- Score system: +100 points per tier, +1000 for reaching the goal
- Game over on obstacle collision or falling off screen

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press ESC key or close the game window.

## Controls

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Space**: Jump
- **Up Arrow**: Climb up ladders (when positioned on a ladder)
- **Down Arrow**: Climb down ladders (when positioned on a ladder)

## Rules

- Avoid red circular fireball obstacles - touching one ends the game
- Climb ladders to reach higher tiers using UP/DOWN arrow keys
- Jump between platforms or ride the moving elevator
- Reach the golden GOAL zone at the very top to score 1000 points
- Each new tier climbed increases obstacle speed
- Falling off the bottom of the screen ends the game

## How to Cleanup

```bash
rm -rf .venv __pycache__
```

## Technical Details

- Framework: Pygame
- Resolution: 800x600
- FPS: 60
- Python: 3.12+
