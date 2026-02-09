# Vector Pac-Man Maze Classic

Navigate the neon maze, collect all dots, and outsmart the chasing ghosts in this arcade masterpiece.

## Description

This game focuses on pathfinding, spatial reasoning, and real-time decision-making. It is targeted at fans of classic arcade logic and provides an excellent environment for AI agents to learn navigation under threat.

## Details

A top-down grid-based maze game. The player controls a circular agent (Hero) that moves continuously in a set direction until hitting a wall. The maze is filled with small dots (pellets). Four enemy agents (Ghosts) move through the maze with distinct simple behaviors: some move randomly, others follow a shortest-path algorithm toward the Hero. Power pellets in the corners temporarily change the state of Ghosts to "vulnerable", allowing the Hero to consume them for bonus points. The level is cleared when all pellets are collected. Collision with a non-vulnerable ghost ends the game.

**Ghost Behaviors:**
- Blinky (Red): Targets Pacman's current position
- Pinky (Pink): Targets 4 tiles ahead of Pacman
- Inky (Cyan): Uses vector between Blinky and Pacman for targeting
- Clyde (Orange): Moves randomly if too close to Pacman

**Ghost Modes:**
- Chase: Ghosts actively pursue Pacman
- Frightened: Power pellets turn ghosts blue, allowing Pacman to eat them

The maze includes warp tunnels on the left and right edges for strategic escapes.

## Technical Specifications

- Grid Size: 30x40 cells
- Frame Rate: 60 FPS (game logic updates every 8 frames)
- State Space: Coordinate positions of Hero, Ghosts, and Pellet occupancy matrix
- Action Space: Up, Down, Left, Right

## How to Build

```bash
uv sync
```

Note: On Windows without MSYS2, use:
```bash
python -m venv .venv
.venv/Scripts/pip install pygame numpy
```

## How to Start

```bash
uv run main.py
```

Or with local venv:
```bash
.venv/Scripts/python main.py
```

## How to Stop

Press ESC or close the pygame window.

## How to Play

- Use Arrow Keys (Up, Down, Left, Right) to change direction
- Score increases by 10 for each pellet eaten
- 200 points for eating a vulnerable ghost (consecutive captures increase: 400, 800, 1600)
- 50 points for a power pellet
- You have 3 lives
- Press R to restart after game over or winning

## How to Cleanup

```bash
rm -rf .venv
```
