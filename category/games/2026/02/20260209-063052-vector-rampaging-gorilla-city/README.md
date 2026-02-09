# Vector Rampaging Gorilla City

Destroy high-rise buildings while dodging defense helicopters in this classic monster rampage simulation.

## Description

A simplified tribute to classic monster rampage games. The player controls a giant gorilla on a 2D side-scrolling city plane. The city consists of procedurally generated buildings of varying heights. The gorilla can move left/right, climb buildings, and punch structures to destroy them. Destruction earns points. However, city defense helicopters spawn periodically and shoot projectiles at the gorilla. The game ends if the health bar reaches zero. High-performance agents will learn to prioritize building destruction while timing punches to intercept helicopters or dodging projectiles.

## Game Mechanics

### Player Actions
- **Move Left/Right**: Arrow keys
- **Climb Up/Down**: Up/Down arrow keys when on a building
- **Punch**: Spacebar
- **Jump**: Up arrow when on ground

### Enemies
- **Defense Helicopters**: Fly across the screen and fire projectiles at the gorilla

### Scoring System
- Building segment destroyed: 10 points
- Helicopter downed: 50 points

### Health System
Health bar (0-100), decreases when hit by projectiles, game over at 0.

## Technical Specifications

- **Resolution**: 800x600
- **Framework**: Pygame
- **State Representation**: Player position (x, y), health, building coordinates, helicopter positions, projectile vectors
- **Action Space**: Move Left, Move Right, Climb Up, Climb Down, Punch

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

Press ESC key or terminate the process (SIGINT).

## How to Play

Use the Left and Right arrow keys to move. Press Up arrow to jump or climb up buildings, Down arrow to climb down. Press Spacebar to punch buildings or helicopters. Avoid red projectiles fired by helicopters to maintain health. Destroy all buildings to advance to the next city with more challenging helicopter patterns.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
.
├── main.py           # Entry point
├── game.py           # Game loop and state management
├── entities.py       # Gorilla, building, helicopter, and projectile classes
└── constants.py      # Game constants and configuration
```
