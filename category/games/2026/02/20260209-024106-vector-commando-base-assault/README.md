# Vector Commando: Base Assault

A simplified top-down tactical shooter inspired by classic arcade games like Commando and Ikari Warriors.

## Description

Control a soldier moving upwards through a scrolling battlefield. Eliminate enemy infantry and turrets, navigate around obstacles, and capture the enemy flag to win.

## Game Mechanics

- **Player Speed**: 5 pixels per frame
- **Bullet Speed**: 10 pixels per frame
- **Scrolling Speed**: 1 (auto-scroll as player moves up)
- **Enemy Types**: Infantry (mobile), Turret (stationary)
- **Scoring**: 100 points per enemy, 500 points for flag capture
- **Lives**: 3 per session

## How to Build

```bash
uv init
uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

Or directly with Python:

```bash
.venv/Scripts/python.exe main.py
```

## How to Play

- **Arrow Keys**: Move in 8 directions
- **Z**: Fire rifle
- **X**: Throw grenade (travels over obstacles)
- **R**: Restart (after game over/victory)
- **Q**: Quit

Avoid contact with enemies and bullets. Use grenades to clear groups of enemies behind cover.

## How to Stop

Press Q or close the window. To force kill:

```bash
kill -9 $(pgrep -f main.py)
```

## How to Cleanup

```bash
rm -rf .venv && rm pyproject.toml && rm uv.lock
```

## Technical Details

- **Language**: Python
- **Framework**: Pygame
- **Dependency Manager**: uv
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
