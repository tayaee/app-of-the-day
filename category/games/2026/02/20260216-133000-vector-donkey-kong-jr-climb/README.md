# Vector Donkey Kong Jr Climb

Rescue the captured giant by climbing vines and avoiding mechanical traps in this vertical platformer.

## Description

Guide Junior from the bottom of the screen to the top, climbing vertical vines while avoiding mechanical Snapjaws patrolling the vines and birds flying across horizontally. Collect fruit to use as projectiles against enemies. Master the vine climbing mechanics - holding two vines simultaneously allows for faster ascent. Collect both keys at the top to unlock the cage and rescue the captured giant.

## Features

- Vertical climbing on multiple vines with physics-based movement
- Double-vine climbing bonus - overlap vines for faster ascent
- Collectible fruit that can be dropped on enemies
- Snapjaw enemies patrolling vines
- Flying bird enemies crossing the screen
- Key collection objectives at the top of the screen
- Progressive difficulty across levels
- Score tracking with various reward mechanisms

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Close the game window or press Escape.

## Controls

- **Up Arrow**: Climb up vines (faster when holding two vines)
- **Down Arrow**: Climb down vines
- **Left/Right Arrow**: Move horizontally between vines or on platforms
- **Space**: Drop fruit onto enemies below
- **R**: Restart game / Next level
- **Escape**: Quit game

## Rules

- Climb from the bottom to the top of the screen
- Avoid Snapjaws (red mechanical traps on vines) - contact ends the game
- Avoid Birds (blue flying enemies) - contact ends the game
- Falling from too high causes death
- Collect fruit scattered on vines to use as weapons
- Drop fruit (Space) onto enemies below to eliminate them for bonus points
- Collect both keys at the top corners to unlock the cage
- Unlocking the cage advances you to the next level

## Scoring

- Fruit collection: 10 points
- Fruit hit on enemy: 50 points
- Climbing progress: 10 points per vertical unit
- Key collection: 500 points each
- Enemy collision: -100 points

## Tips

- Overlap vines (move to where two vines cross) for double climbing speed
- Time your fruit drops carefully to hit multiple enemies
- Watch bird patterns and wait for gaps
- Snapjaws patrol up and down on their assigned vines
- Progress increases bird frequency and enemy speed

## How to Cleanup

```bash
rm -rf .venv
```
