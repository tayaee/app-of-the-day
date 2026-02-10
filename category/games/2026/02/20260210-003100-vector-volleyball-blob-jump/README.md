# Vector Volleyball Blob Jump

Engage in a fast-paced 1-on-1 blob volleyball match with physics-based jumping and spiking.

## Description

This game focuses on simple physics interactions, timing, and spatial awareness. It targets casual gamers and provides an excellent environment for RL agents to learn trajectory prediction and reactive movement.

## Details

The game features two blob-like characters on a 2D side-view court divided by a central net. A ball bounces off the floor, walls, and players. Players can move left/right and jump. The objective is to hit the ball over the net so that it touches the opponent's ground.

Key mechanics:
1. Velocity-based collision where the blob's movement speed affects the ball's trajectory
2. A spike mechanic if the blob hits the ball while at the peak of a jump
3. Boundary detection to prevent players from crossing the net
4. Maximum 3 touches per side before the ball must cross the net

## Rules

- Win condition: First to 11 points
- Point scoring: Ball touches the opponent's floor or opponent exceeds 3 touches
- Max touches: Maximum 3 touches per side before the ball must cross the net

## How to Build

```bash
uv venv
uv pip install pygame
```

Or simply:
```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` key or close the game window.

## How to Play

- Player 1 (Left, Blue): Use `A` and `D` to move, `W` to jump
- Player 2 (Right, Red): Use `LEFT` and `RIGHT` arrow keys to move, `UP` to jump
- `SPACE`: Restart when game over
- `ESC`: Quit

Score points by making the ball land on the opponent's side of the court. Gravity and momentum dictate the ball's path, so time your jumps to intercept the ball at the highest point for a powerful spike.

## Technical Specs

- Engine: Pygame
- Physics: Semi-rigid body circles with velocity-based collision
- Resolution: 800x400
- FPS: 60

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
