# Vector Space Invaders Shoot

Classic space invaders where you defend Earth from descending alien waves.

## Description

A faithful recreation of the classic arcade shooter. Control your ship at the bottom of the screen to destroy waves of descending aliens. Aliens move in formation and shoot back while gradually approaching your position. Use bunkers for cover but watch out - they degrade with each hit.

## Features

- 5x11 grid of aliens with different point values by row
- Four destructible bunkers for cover (4 hits each)
- Progressive difficulty - aliens speed up each level
- Particle explosion effects when aliens are destroyed
- 3 lives to start
- Aliens shoot back with increasing frequency

## How to Play

1. Press SPACE to start
2. Use LEFT/RIGHT arrow keys to move your ship
3. Press SPACE to fire upward
4. Destroy all aliens to advance to the next level
5. Use bunkers for cover from alien fire
6. Don't let aliens reach your level

## Controls

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Space**: Shoot

## Scoring

- Top row (red): 30 points
- Middle rows (orange): 20 points
- Bottom rows (purple): 10 points

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

## Rules

- Avoid alien bullets - each hit costs a life
- Destroy all aliens to advance to the next level
- Aliens descend when reaching screen edges
- Game over if all lives are lost or aliens reach your level
- Each level increases alien speed and fire rate

## How to Cleanup

```bash
rm -rf .venv __pycache__
```

## Technical Details

- Framework: Pygame
- Resolution: 800x600
- FPS: 60
- Python: 3.12+
