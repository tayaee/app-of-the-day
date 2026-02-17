# Vector Ball Physics

Navigate a bouncing ball through a minimalist vector maze using momentum and physics.

## Description

This game focuses on physics-based movement and momentum management. It targets players who enjoy skill-based precision games and provides a perfect environment for Reinforcement Learning agents to learn trajectory prediction and continuous control in a constrained 2D space.

The game consists of a circular ball (player) in a rectangular arena with various static and moving vector obstacles. The goal is to reach a green exit portal. The ball has inertia and gravity. When the ball hits a wall, it bounces with a coefficient of restitution. Friction is applied over time to simulate air resistance. Level progression increases obstacle complexity and adds moving hazards that reset the ball to the starting point upon contact.

## Technical Specifications

- **Engine**: Pygame-ce
- **Physics Model**: Euler momentum integration
- **State Space**: Ball position (x, y), velocity (vx, vy), distance to nearest obstacles, target relative position
- **Action Space**: Continuous (force vector in range [-1, 1] for x and y) or Discrete (Up, Down, Left, Right impulses)

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

```bash
./run.sh    # Linux/macOS
run.bat     # Windows
```

## How to Stop

Press ESC key to quit the game.

## How to Play

Use the Arrow Keys or WASD to apply directional force to the ball. Your score increases based on how quickly you reach the exit portal. Collecting yellow vector dots provides bonus points. Avoid red obstacles; hitting them decreases score and resets the level. The ball is subject to constant gravity, so you must pulse the 'Up' key to maintain height.

## Reward Function

| Action | Reward |
|--------|--------|
| Reach goal | +100 |
| Collect dot | +10 |
| Hit hazard | -50 |
| Time penalty | -0.1 per frame |

## Project Structure

```
vector-bolat-ball-physics/
├── main.py
├── run.bat
├── run.sh
└── assets/
    └── screenshots/
```

## How to Cleanup

```bash
rm -rf .venv
```
