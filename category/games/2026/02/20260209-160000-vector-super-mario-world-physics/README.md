# Vector Super Mario World Physics

Master the momentum and physics of a simplified side-scrolling world.

## Description

This game focuses on the core platforming mechanics of momentum, jumping height, and enemy collision. It provides a clean environment for RL agents to learn the relationship between horizontal velocity and jump distance, which is a fundamental challenge in platforming AI.

The game is a 2D side-scrolling platformer. The player controls a character that must navigate a level from left to right. Key features include: physics-based movement with acceleration and friction; variable jump height depending on how long the jump key is held; gravity constants that affect descent speed; enemy entities (Goomba-style) that move back and forth and damage the player on side contact but are defeated when jumped upon; gold coins for scoring; and a goal flag at the end of the level to trigger completion.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Play

Use LEFT and RIGHT arrow keys to move. Press SPACE to jump. Hold SPACE longer for higher jumps. Jump on top of enemies to defeat them. Collect coins for points (+100 each). Defeat enemies for points (+500 each). Reach the flag for bonus points (+1000). Avoid touching enemies from the side or falling into pits.

## How to Stop

Ctrl+C or close the window

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specs

- Resolution: 800x400
- FPS: 60
- Input: Keyboard (Arrow keys, Space)
- State Space: Player position, velocity, enemy positions, nearest platform coordinates
- Action Space: LEFT, RIGHT, JUMP, IDLE
