# Vector Dig Dug Rock Trap Logic

**Category:** Games

**Description:** Outsmart monsters by strategically dropping rocks in this classic underground tactical puzzle.

## Rationale

This game focuses on environmental interaction and timing rather than just combat. It is designed for researchers testing AI pathfinding and hazard anticipation in a destructible grid environment.

## Details

The game consists of a 2D grid representing underground soil. The player controls a character that can move in four directions, digging tunnels as they move. Two types of enemies (Pookas and Fygars) chase the player through tunnels. The core mechanic is the Rock: rocks are located in the soil and will fall if the soil beneath them is removed. A falling rock crushes anything in its path, including the player. Enemies are eliminated by being crushed by rocks or by being inflated using the player's pump (though rock traps yield higher scores). The level is cleared when all enemies are defeated.

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

Or use the provided scripts:
```bash
./run.sh    # Linux/Mac
run.bat     # Windows
```

## Controls

- **Arrow Keys**: Move and dig tunnels
- **Space**: Fire pump at enemies in facing direction
- **R**: Restart game (when game over)
- **Escape**: Quit

## How to Play

Use ARROW KEYS to move and dig. Press SPACE to fire the pump at enemies to stun or inflate them. To use a rock trap, dig a tunnel directly underneath a rock when an enemy is following you, then move out of the way before the rock falls. High scores are achieved by crushing multiple enemies with a single rock.

## Game Rules

- **Grid Size**: 20x15 cells
- **Entities**: Player, Pooka, Fygar, Rock
- **Physics**: Gravity affects rocks only when the cell directly below is an empty tunnel
- **Scoring**:
  - Dig soil: 10 points
  - Pump kill: 200 points
  - Rock kill (1 enemy): 1000 points
  - Rock kill (2+ enemies): 2500 points
  - Level clear bonus: 500 points

## Features

- Destructible grid environment
- Rock physics with wobble delay and falling
- Two enemy types with different behaviors:
  - Pooka: Basic chaser, can enter ghost mode to move through soil
  - Fygar: Slower but can breathe fire horizontally
- Pump weapon to inflate and pop enemies
- Strategic rock traps for high scores
- Level progression with respawn

## AI Integration

AI agents can interact with the game through the `Game` class:

```python
game = Game()
observation = game.get_observation()
observation, reward, done = game.step_ai(action)
```

### Action Space

- 0: Move up
- 1: Move down
- 2: Move left
- 3: Move right
- 4: Use pump
- 5: Do nothing

### Observation Space

```python
{
    "grid": [[0, 1, ...], ...],  # 0=soil, 1=tunnel
    "player_pos": (x, y),
    "player_pump_active": bool,
    "enemies": [
        {
            "type": "pooka" | "fygar",
            "pos": (x, y),
            "inflation": int,
            "alive": bool
        },
        ...
    ],
    "rocks": [
        {
            "pos": (x, y),
            "state": "stable" | "wobbling" | "falling",
            "alive": bool
        },
        ...
    ],
    "score": int,
    "lives": int,
    "game_state": str
}
```

### Reward Structure

- Digging soil: +10
- Inflating enemy: +10 per pump
- Killing with pump: +200
- Crushing with rock: +1000 (single), +2500 (multiple)
- Clearing level: +500
- Death: Respawn with life lost

## How to Stop

Press ESC key or close the game window. For automation, send SIGINT (Ctrl+C).

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specifications

- **Language:** Python 3.12+
- **Library:** pygame-ce (pygame)
- **Resolution:** 960x720
- **Input Mode:** Discrete (grid-based)
- **State Representation:** Multi-dimensional array (grid) + entity coordinates
