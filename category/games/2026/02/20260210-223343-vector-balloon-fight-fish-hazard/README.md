# Vector Balloon Fight: Fish Hazard

Master the art of buoyancy and avoid the giant fish from the deep in this gravity-defying duel.

## Description

This game targets users interested in physics-based combat and precise movement control. It provides a unique challenge for RL agents to manage momentum, flap frequency, and spatial awareness of hazards both above and below the water line.

A simplified tribute to Balloon Fight's water stage. Players control a character with two balloons. Gravity is constantly pulling the player down. Flapping (upward thrust) must be timed to stay airborne. The stage consists of platforms and a body of water at the bottom. A giant fish lurks in the water and will jump to eat the player if they fly too low. Enemy agents also fly around, and the player must pop their balloons by colliding from above. If the player's balloons are popped or they are eaten by the fish, the game ends. The physics engine handles inertia, drag, and gravity.

## State Space

- `player_pos`: [x, y] - Player coordinates
- `player_velocity`: [vx, vy] - Player velocity vector
- `balloons_remaining`: integer (0-2) - Number of intact balloons
- `enemy_positions`: list of [x, y] - Enemy coordinates
- `fish_state`: active/idle - Current fish state
- `fish_pos_x`: float - Fish horizontal position

## Action Space

- `flap`: boolean - Apply upward thrust
- `move_left`: boolean - Move left
- `move_right`: boolean - Move right

## Reward Function

- `enemy_popped`: +100 points per balloon
- `survival_per_frame`: +0.1 points
- `balloon_lost`: -50 points
- `game_over_fish`: -200 points
- `game_over_fall`: -200 points
- `wave_bonus`: +500 points

## Controls

- **UP / SPACE** - Flap to gain altitude
- **LEFT / RIGHT** - Move horizontally
- **ESC** - Exit game

## How to Build

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
vector-balloon-fight-fish-hazard/
├── main.py       # Entry point
├── game.py       # Main game loop and rendering
├── entities.py   # Game entities (Player, Enemy, Fish, Balloon, Platform)
├── config.py     # Configuration constants
├── pyproject.toml
├── appinfo.json  # Metadata
├── run.bat       # Windows run script
├── run.sh        # Linux/Mac run script
└── README.md
```
