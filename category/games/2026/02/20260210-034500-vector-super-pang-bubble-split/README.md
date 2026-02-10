# Vector Super Pang - Bubble Split

Clear the screen by shooting and splitting bouncing bubbles into smaller pieces.

## Description

A timing-based arcade shooter inspired by the classic Pang game. Large bubbles bounce around the screen following physics-based trajectories. Fire vertical wire shots to split bubbles into smaller pieces until they disappear completely. Avoid contact with bubbles at all costs. Clear all bubbles within the time limit to advance to the next level with more challenging bubble configurations.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

**Goal**: Eliminate all bubbles to score points and advance to the next level.

- **LEFT/RIGHT Arrow Keys**: Move the player horizontally
- **SPACEBAR**: Fire the vertical wire shot upward
- **ESC**: Quit the game

**Scoring**:
- Large bubble (Red) split: 100 points
- Medium bubble (Green) split: 200 points
- Small bubble (Blue) pop: 500 points

**Game Rules**:
- Bubbles follow parabolic trajectories with gravity physics
- When hit, large bubbles split into two medium bubbles
- Medium bubbles split into two small bubbles
- Small bubbles disappear when hit
- The game ends if a bubble touches the player or the timer reaches zero

**Tips**: Time your shots carefully. The wire travels vertically, so position yourself directly beneath bubbles. Larger bubbles bounce higher, making them harder to hit but more rewarding.

## Technical Details

- **Engine**: Pygame
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **State Space**: player_x, bubble_positions, bubble_velocities, wire_active, time_remaining
