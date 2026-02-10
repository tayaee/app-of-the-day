# Vector Super Mario Bros Fireball Target

Master the arc of the legendary fireball to defeat moving targets in this precision timing challenge.

## Description

A single-screen skill game where the player character (Mario) is fixed on a left-side platform. Targets (Goombas, Koopas, or floating blocks) move at varying speeds from right to left. The player can only throw fireballs with fixed bounce physics. The game simulates gravity-affected projectiles that bounce once or twice before disappearing. Difficulty increases as targets become smaller, faster, and follow unpredictable patterns.

## Features

- Fixed-position player with fireball throwing mechanics
- Physics-based projectiles with gravity and ground bounce
- Three enemy types: Goombas (ground walking), Koopas (ground walking with shells), and Floating Blocks (vertical movement)
- Multi-hit bonus: hitting multiple enemies with one fireball grants bonus points
- Progressive difficulty: enemies speed up as score increases
- Win condition at 5000 points, lose after 3 misses

## How to Build

```bash
uv init
uv add pygame
uv lock
```

Or simply:
```bash
uv sync
```

## How to Run

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the game window.

## Controls

- **SPACE**: Throw fireball

## Rules

- Press SPACE to launch a fireball
- Fireball follows a parabolic trajectory affected by gravity
- Fireballs bounce on the ground up to 2 times before disappearing
- Maximum 2 fireballs on screen at once
- Score 100 points per enemy hit
- Score 500 bonus points for multi-hits (one fireball hitting multiple enemies)
- Win condition: Reach 5000 points
- Lose condition: Miss 3 targets (let them pass the left boundary)
- Timing is critical - predict where targets will be when the fireball reaches them

## Examples

Throw a fireball early to catch ground enemies. For floating blocks, time your throw when the block is at the peak of its vertical movement. Try to line up multiple enemies in a row for multi-hit bonuses.

## Technical Specifications

- **Engine**: Pygame
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **State Space**: [target_x, target_y, target_speed, target_type, fireball_x, fireball_y, fireball_velocity_x, fireball_velocity_y]
- **Action Space**: Throw fireball (Spacebar)

## Game Rules Detail

| Setting | Value |
|---------|-------|
| Fireball Velocity | [400, -200] (pixels/second) |
| Gravity | 980 (pixels/second^2) |
| Max Fireballs on Screen | 2 |
| Scoring (Hit) | 100 points |
| Scoring (Multi-hit) | 500 points |
| Win Condition | 5000 points |
| Lose Condition | 3 missed targets |

## How to Cleanup

```bash
rm -rf .venv
rm pyproject.toml
rm uv.lock
```
