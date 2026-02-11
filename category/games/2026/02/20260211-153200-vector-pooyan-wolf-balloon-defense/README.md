# Vector Pooyan: Wolf Balloon Defense

**Category:** Games

**Description:** Defend the piglet base from rising wolves by popping their balloons with arrows.

## Rationale

This game provides a simplified implementation of a fixed-axis shooter with gravity and projectile physics. It is ideal for training reinforcement learning agents to understand lead-target shooting and vertical timing against varied enemy movement patterns.

## Details

The game is a simplified 2D arcade defense game inspired by Pooyan. The player controls a piglet in a gondola that moves vertically along the right side of the screen. Wolves spawn at the bottom-left and float upward using balloons. The player's objective is to shoot arrows horizontally to pop the wolves' balloons before they reach the top ledge. If a wolf reaches the top, it occupies a slot on the ledge; if four wolves reach the top, the game is over. Projectiles move at a constant velocity, requiring the player to time shots based on the wolf's vertical position and the arrow's travel time.

## Technical Specifications

- **Resolution:** 800x600
- **FPS:** 60
- **Input:** Keyboard
- **Dependencies:** pygame, numpy

## Game Rules

- **Player Movement:** Vertical movement only (Y-axis)
- **Projectile Limit:** Maximum 2 arrows on screen at once
- **Enemy Types:** Regular wolves (1 hit) and shielded wolves (2 hits)
- **Game Over:** 4 wolves successfully reaching the top ledge

## How to Build

```bash
uv run python -m pip install pygame numpy
```

## How to Run

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press ESC or close the game window.

## How to Play

- **UP/DOWN Arrow Keys:** Move the gondola vertically
- **SPACE:** Fire an arrow
- **ESC:** Quit the game

**Scoring:**
- Regular wolf popped: 100 points
- Shielded wolf popped: 200 points
- Wolf reaches ledge: -50 points

The goal is to maximize your score before 4 wolves reach the top ledge.

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state
- `step_ai(action)`: Execute an action and receive (observation, reward, done)

### Reward Structure

- Per frame alive: +0.01
- Regular wolf hit: +1.0
- Shielded wolf hit (first balloon): +0.5
- Wolf reaches ledge: -1.0
- Game over: -10.0

### Observation Space

```python
{
    "player_y": float,              # Player Y position
    "wolves": [                     # Array of active wolves
        {
            "x": float,
            "y": float,
            "shielded": bool,
            "balloons_popped": int
        },
        ...
    ],
    "arrows": [                     # Array of active arrows
        {"x": float, "y": float},
        ...
    ],
    "wolves_on_ledge": int,         # Count of wolves on ledge
    "score": int,
    "game_state": str
}
```

### Action Space

- 0: Stay
- 1: Move Up
- 2: Move Down
- 3: Shoot

## How to Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```
