# Vector Mappy Trampoline Bounce

Master the art of trampoline physics to recover stolen items while dodging pursuing cats.

## Description

A vertical platformer inspired by the classic arcade game Mappy. Control a mouse navigating a multi-story house, using trampolines to bounce between floors and collect stolen treasures. Each consecutive bounce on a trampoline sends you higher, but beware - bounce too many times and the trampoline breaks!

## Rationale

This game focuses on rhythmic timing and vertical navigation logic. It targets players who enjoy classic arcade physics and serves as an excellent environment for RL agents to learn momentum-based movement and risk assessment. The trampoline mechanic creates an interesting trade-off between speed and safety.

## Details

### Game Mechanics

- **Trampolines**: Auto-bounce when landing on them. Each consecutive bounce increases height
- **Safety Limit**: Trampolines break after 4 consecutive bounces
- **Items**: Diamond-shaped treasures placed on floors (100 points each)
- **Enemies**: Cats patrol floors and chase the player
- **Safety**: Players are invulnerable while mid-air on trampolines

### Physics
- Gravity: 0.5
- Base Jump Strength: -12.0
- Trampoline Boost: +2.0 per consecutive bounce
- Maximum capped velocity prevents endless acceleration

### Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Move horizontally |
| ESC | Exit game |

### Scoring

- 100 points per item collected
- 1000 bonus points for completing a level
- Game over when caught by a cat or trampoline breaks while you're on it

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

## Stop

Press ESC or close the window.

## How to Play

1. Press SPACE to start
2. Use LEFT/RIGHT arrows to move your mouse character
3. Land on trampolines to bounce automatically to higher floors
4. Collect all diamond items on each floor
5. Avoid cats patrolling the floors (you're safe while mid-air!)
6. Don't bounce more than 4 times on the same trampoline
7. Collect all items to advance to the next level

## AI Agent Input

### Observation Space
```
Box(16,) - Normalized float values:
- [0-1]: Player position (x, y)
- [2-3]: Player velocity (vx, vy)
- [4]: Consecutive bounces ratio
- [5]: On floor indicator
- [6]: On trampoline indicator
- [7]: Enemy count ratio
- [8]: Items collected ratio
- [9]: Current level ratio
- [10-11]: Nearest enemy relative position (dx, dy)
- [12-14]: Nearest trampoline info (dx, dy, bounces_left)
```

### Action Space
```
Discrete(3):
- 0: No action
- 1: Move left
- 2: Move right
```

### Reward Structure
- Survival per frame: +0.01
- Item collected: +2.0
- Level complete: +10.0
- Trampoline breaks: -2.0
- Death: -5.0

## Project Structure

```
category/games/2026/02/20260209-151000-vector-mappy-trampoline-bounce/
├── main.py           # Entry point
├── game.py           # Game loop and rendering
├── entities.py       # Player, Floor, Enemy, Item, GameState classes
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
