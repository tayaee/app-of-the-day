# Vector Super Mario Bros Power Up Logic

Master the strategic sequence of Mario's growth and power-up transformations.

## Description

This app focuses on the core progression mechanic of Super Mario Bros: the hierarchical power-up system. It provides a controlled environment for AI agents to learn state-based decision making and strategic resource acquisition.

## Details

A single-screen logic platformer where the player starts as "Small Mario". The goal is to reach the exit gate, which is blocked by a physical barrier that only "Super Mario" or "Fire Mario" can break. The player must navigate a small grid-based map to find a Mushroom to grow, and optionally a Fire Flower to gain offensive capabilities.

Enemies roam the floor, and touching them reverts the player's state or causes game over if in the smallest state. Power-ups appear in specific blocks when struck from below.

## State Machine

- **Small Mario (0)**: Initial state. Dies on contact with enemies.
- **Super Mario (1)**: Becomes Small Mario on contact with enemies. Can break bricks and barriers.
- **Fire Mario (2)**: Becomes Super Mario on contact with enemies. Can shoot fireballs to destroy enemies.

## Technical Specs

- Engine: Pygame
- Resolution: 800x600
- Grid Size: 40x40
- Physics: Simple gravity and horizontal momentum

## State Space

- player_state: int (0: Small, 1: Super, 2: Fire)
- player_pos: float tuple (x, y)
- enemies: list of enemy positions
- powerups: list of power-up positions and types

## Action Space (Discrete 5)

- MOVE_LEFT: Move left
- MOVE_RIGHT: Move right
- JUMP: Vertical jump
- SHOOT: Fire fireball (Fire Mario only)
- IDLE: No action

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:

```bash
./run.sh    # Linux/Mac
run.bat     # Windows
```

## How to Stop

Press ESC or close the window. For agents: sys.exit() on terminal signal.

## How to Play

- Left/Right arrow keys for movement
- Space to jump
- S key to shoot fireballs (only in Fire Mario state)
- Hit blocks from below to release power-ups
- Avoiding enemies is crucial to maintain power-up status

## Scoring

- Mushroom: +100 points
- Fire Flower: +200 points
- Breaking target bricks: +50 points
- Stomping enemies: +50 points
- Reaching exit gate: +1000 points

## Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```
