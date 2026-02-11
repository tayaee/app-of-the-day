# Vector Mappy: Stolen Item Retrieve

Navigate a multi-story house to retrieve stolen items while outsmarting feline guards.

## Description

This game targets developers and AI agents interested in pathfinding, state-based enemy AI, and vertical platforming logic. It provides a structured environment for reinforcement learning where agents must balance risk and reward in a maze-like layout.

The game is a simplified 2D platformer inspired by the classic Mappy. It features a house with 5 floors connected by trampolines. The player controls a police mouse (Mappy). Stolen items (Radio, TV, Safe) are scattered across floors. Cats (Meowkies) roam the floors following a basic pursuit-style AI. Mappy cannot jump but uses trampolines to move between floors. While in the air on a trampoline, Mappy is invulnerable to cats. Doors can be opened to release a wave that pushes cats back.

## Game Rules

**Scoring:**
- Radio: 100 points
- TV: 200 points
- Safe: 500 points
- Level Complete Bonus: 1000 points
- Clearing all items moves to the next level with increased cat speed

**Trampoline Logic:**
- Consecutive bounces without landing on a floor change the trampoline color
- 4th bounce breaks the trampoline, resulting in a game over if no floor is reached

**Enemy AI:**
- Cats move towards the player's current floor and x-coordinate
- They turn around if they hit a wall or a closed door
- Cats can be temporarily stunned by using doors to release a wave

## Controls

- **LEFT/RIGHT ARROW KEYS** - Move left and right
- **SPACE** - Open/close doors (when near a door)
- **ESC** - Exit game

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

Or simply:
```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press **ESC** or close the window.

## Technical Specifications

- Resolution: 800x600
- FPS: 60
- Language: Python 3.12+
- Library: pygame-ce

## Project Structure

```
vector-mappy-stolen-item-retrieve/
├── main.py       # Entry point
├── game.py       # Main game loop and rendering
├── entities.py   # Game entities (Player, Enemy, Item, etc.)
├── config.py     # Configuration constants
├── pyproject.toml
├── run.bat       # Windows run script
├── run.sh        # Linux/Mac run script
└── README.md
```
