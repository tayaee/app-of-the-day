# Vector Super Mario Bros Jump and Squash

**Category:** Games

**Description:** Master the art of precision jumping to defeat rhythmic waves of Goombas.

## Rationale

This game targets developers and AI agents interested in platformer physics and collision detection. It focuses on the core "stomp" mechanic of Super Mario Bros, providing a clear reward signal for reinforcement learning through enemy elimination and survival timing.

## Details

The game is a single-screen survival platformer. The player controls a character that can move left/right and jump. Enemies (Goombas) spawn from the screen edges and move toward the center at varying speeds. The player must jump on top of enemies to squash them. If an enemy touches the player from the side, the game ends. Gravity and acceleration follow classic 2D platformer constants to ensure a professional feel. The background is a clean, single-color dark grey with white vector platforms to minimize visual noise.

## Technical Specifications

- **Engine:** Pygame
- **Resolution:** 800x600
- **Gravity:** 0.8
- **Jump Force:** -15
- **Enemy Spawn Rate:** Initial 2.0s, decreases over time

## How to Build

```bash
uv run python -m pip install pygame && uv lock
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC key or close the game window.

## How to Play

Use LEFT/RIGHT arrow keys to move and SPACE to jump. Score 100 points for every enemy squashed by landing on their top half. Score 10 points per second survived. Game Over occurs if player hitbox overlaps with enemy hitbox while not in a downward falling state above the enemy.

## How to Cleanup

```bash
rm -rf .venv && rm uv.lock
```

## AI Integration

AI agents can interact with the game through the `Game` class:

### Observation Space

```python
{
    "player_x": float,           # Player X position
    "player_y": float,           # Player Y position
    "player_vx": float,          # Player X velocity
    "player_vy": float,          # Player Y velocity
    "on_ground": bool,           # Whether player is on ground
    "enemies": [                 # List of active enemies
        {
            "x": float,
            "y": float,
            "vx": float,
            "squashed": bool
        },
        ...
    ],
    "score": int,
    "survival_time": float,
    "game_over": bool
}
```

### Action Space

- 0: Stay (do nothing)
- 1: Left
- 2: Right
- 3: Jump

### Reward Structure

- Per enemy squashed: +100
- Per second survived: +10
- Game over: -100

### Example AI Usage

```python
from game import Game

game = Game()
observation = game.reset_for_ai()

while not observation["game_over"]:
    # Your AI logic here to choose action
    action = choose_action(observation)  # 0, 1, 2, or 3
    observation, reward, done = game.step_ai(action)
```

### Methods

- `reset_for_ai()`: Reset game and return initial observation
- `get_observation()`: Get current game state
- `step_ai(action)`: Execute action and return (observation, reward, done)
