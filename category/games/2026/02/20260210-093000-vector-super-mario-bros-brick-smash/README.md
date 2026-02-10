# Vector Super Mario Bros Brick Smash

Smash bricks and collect hidden power-ups in this precision jumping challenge.

## Description

This game focuses on the core mechanics of environmental interaction and reward systems. You control a character that can move left, right, and jump across multiple platform levels. The primary objective is to break specific blocks by hitting them from directly underneath. There are two types of blocks: standard bricks (breakable, worth 10 points) and question mark blocks (contain coins, worth 50 points). A 60-second timer adds urgency to the challenge.

## Features

- Multi-level platform layout with blocks at various heights
- Two block types: destructible bricks and reward-containing question blocks
- Physics-based jumping with gravity and collision detection
- 60-second time limit for score maximization
- Visual feedback with coin animations and block destruction effects
- Score tracking for bricks smashed and coins collected

## How to Build

```bash
uv venv
uv pip install pygame
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

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Space** or **Up Arrow**: Jump
- **R**: Restart game (when game over)

## Rules

- Score increases by 10 points for every brick smashed
- Score increases by 50 points for hitting a question mark block
- You must time your jumps so that your character's head hits the blocks from directly underneath
- Question mark blocks turn dark after being hit (no more coins)
- The game ends when the 60-second timer expires
- Try to smash as many blocks as possible before time runs out

## Examples

Position yourself under a row of bricks and jump to smash them all in sequence. Look for golden question mark blocks - these contain valuable coins. Jump from platform to platform to reach higher blocks, but be careful with your timing!

## Technical Specifications

- **Engine**: Pygame
- **Resolution**: 800x400
- **Frame Rate**: 60 FPS
- **State Space**: Player position, block coordinates, reward locations, time remaining
- **Action Space**: Left, Right, Jump, Idle

## How to Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
uv cache clean
```
