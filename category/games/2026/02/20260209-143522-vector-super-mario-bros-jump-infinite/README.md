# Vector Super Mario Bros Jump

A precision-based vertical platformer inspired by Super Mario's classic jump physics.

## Description

Climb as high as possible by jumping between procedurally generated platforms. The game features Mario-style jump physics with momentum-based horizontal control. Platforms begin to move horizontally as you progress, increasing the challenge.

## Rationale

This game focuses on the core mechanic of platformers: jump timing and horizontal control. It is designed for reinforcement learning agents to master momentum and collision detection in a dynamic environment. The simple mechanics and clear scoring make it ideal for AI training.

## Details

- **Physics**: Gravity (0.8), jump strength (-15.0), max fall speed (10.0)
- **Platforms**: Varying widths (60-100px), random gaps (70-130px)
- **Progression**: Moving platforms start appearing at 100 points
- **Powerups**: Golden mushrooms grant one super-jump (+33% height)
- **Scrolling**: Camera follows player upward automatically
- **Death**: Falling below the bottom of the screen ends the session

### Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Move horizontally |
| SPACE/UP | Jump |
| ESC | Exit game |

### Scoring

- +10 points per new platform landed on
- Height meter tracks your maximum altitude
- Game over when you fall off the bottom of the screen

## Build

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## Stop

Press ESC or close the window.

## How to Play

1. Press SPACE to start
2. Use LEFT/RIGHT arrows to position your character
3. Press SPACE or UP to jump from platforms
4. Collect golden mushrooms for super-jumps
5. Reach the highest altitude possible
6. Avoid falling below the screen edge

## AI Agent Input

### Observation Space
```
Box(13,) - Normalized float values:
- [0-2]: Player position (x, y)
- [3-4]: Player velocity (vx, vy)
- [5]: Camera height
- [6]: On ground indicator
- [7]: Has super jump indicator
- [8]: Platform count
- [9]: Powerup count
- [10-13]: Nearest platform info (x, y, width, is_moving)
```

### Action Space
```
Discrete(4):
- 0: No action
- 1: Move left
- 2: Move right
- 3: Jump
```

### Reward Structure
- Landing on platform: +1.0
- New height record: +0.5
- Survival per frame: +0.01
- Death: -5.0

## Project Structure

```
category/games/2026/02/20260209-143522-vector-super-mario-bros-jump-infinite/
├── main.py           # Entry point
├── game.py           # Game loop and rendering
├── entities.py       # Player, Platform, GameState classes
├── config.py         # Constants and settings
├── appinfo.json      # App metadata
├── pyproject.toml    # Dependencies
└── README.md         # This file
```

## Technical Specs

- **Language**: Python 3.12+
- **Library**: pygame-ce 2.5+
- **Resolution**: 400x600
- **FPS**: 60
- **Style**: Vector/minimal aesthetic
