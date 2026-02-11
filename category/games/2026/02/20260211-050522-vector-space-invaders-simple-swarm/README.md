# Vector Space Invaders - Simple Swarm

Defend the Earth from rhythmic descending alien swarms in this vector-style arcade shooter.

## Description

A classic Space Invaders clone featuring vector-style graphics where you control a tank at the bottom of the screen. Aliens move in a grid formation, shifting horizontally and dropping down when hitting screen edges. Destroy all aliens before they reach your position or you run out of lives.

## Rationale

This classic shooter provides a perfect environment for AI agents to learn spatial awareness, timing, and threat prioritization. It targets fans of retro arcade games and developers interested in swarm logic and collision detection.

## Game Rules

| Setting | Value |
|---------|-------|
| Player Speed | 5 |
| Bullet Speed | 7 |
| Alien Horizontal Speed | 2 |
| Alien Vertical Drop | 20 |
| Alien Fire Rate | 1% probability per frame |
| Grid Size | 5x8 aliens |

### Scoring
- Bottom row aliens: 10 points
- Middle row aliens: 20 points
- Top row aliens: 30 points

## Technical Stack

- **Language**: Python 3.12+
- **Package Manager**: uv
- **Graphics Library**: pygame-ce

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press `ESC` or close the window.

## How to Play

- **LEFT/RIGHT Arrow Keys**: Move tank
- **SPACE**: Fire bullet
- **R**: Restart after game over

The game ends if:
- You are hit by an alien bullet
- An alien touches your line
- You lose all 3 lives

## How to Cleanup

```bash
rm -rf .venv __pycache__
```

## AI Agent Info

For training AI agents:

| Aspect | Details |
|--------|---------|
| **Observation Space** | Player X position, Alien grid bounding box, Nearest bullet coordinates |
| **Action Space** | 0: Stay, 1: Left, 2: Right, 3: Shoot |
| **Reward Function** | +1 per alien hit, -10 per life lost, +50 for wave clear |

## Project Structure

```
category/games/2026/02/20260211-050522-vector-space-invaders-simple-swarm/
    main.py           # Game entry point with all game logic
    pyproject.toml    # Project configuration
    run.bat           # Windows launch script
    run.sh            # Linux/Mac launch script
    README.md         # This file
```
