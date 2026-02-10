# Vector Super Mario Bros Jump Platform

A horizontal platformer where you navigate moving platforms to reach the goal flag.

## Description

Side-scrolling platformer inspired by Super Mario Bros. Navigate from left to right across gaps and moving platforms to reach the flagpole. Features realistic physics with gravity, momentum, and friction.

## Rationale

Focuses on core platformer mechanics: precise jumping, timing, and collision detection. Ideal for AI agents learning platformer physics and momentum management.

## Details

- **Physics**: Gravity (0.5), jump strength (-12), friction (0.8)
- **Level**: 3200px wide with 5 gaps and 13 moving platforms
- **Platform Types**: Static, horizontal moving, vertical moving
- **Time Limit**: 120 seconds
- **Scoring**: Distance + height bonus + time bonus

### Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Move horizontally |
| SPACE | Jump / Start |
| R | Restart (on game over) |
| ESC | Exit |

### Scoring

- Distance traveled: 10 points per meter
- Height bonus: 100 points per meter above ground
- Time bonus: 5 points per second remaining

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
2. Use LEFT/RIGHT arrows to move
3. Press SPACE to jump
4. Time your jumps on moving platforms
5. Reach the flagpole on the far right
6. Complete quickly for bonus points

## AI Agent Input

### Observation Space

```
Dict:
- player: {x, y, vx, vy}
- on_ground: bool
- nearest_platform: {x, y, vx, vy, width}
- flagpole: {x, y}
- camera_x: float
- time_left: float
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

- Distance progress: +0.1 per frame
- Reaching flagpole: +1000
- Falling: -100
- Time bonus on completion: +time_remaining * 5

## Project Structure

```
category/games/2026/02/20260210-043051-vector-super-mario-bros-jump-platform/
├── main.py           # Entry point
├── game.py           # Game loop and rendering
├── entities.py       # Player, Platform, Flagpole, GameState
├── config.py         # Constants and settings
├── appinfo.json      # App metadata
├── pyproject.toml    # Dependencies
└── README.md         # This file
```

## Technical Specs

- **Language**: Python 3.12+
- **Library**: pygame-ce 2.5+
- **Resolution**: 800x600
- **FPS**: 60
- **Physics**: Custom AABB collision with momentum
