# Vector Popeye Spinach Rescue

Rescue Olive Oyl while avoiding Brutus and collecting spinach for a power boost.

## Description

This game implements a multi-tiered platform logic with enemy AI pathfinding and state-based power-up mechanics, making it an excellent environment for reinforcement learning agents to study risk-reward trade-offs.

## Game Details

The game consists of four horizontal platforms connected by ladders. The player (Popeye) starts at the bottom and must collect hearts or musical notes thrown by Olive Oyl from the top floor. Brutus wanders the platforms, moving between levels to intercept Popeye. If Popeye touches Brutus, a life is lost. A spinach can spawn randomly on the map; if Popeye collects it, he enters a temporary 'invincible' state where he can knock Brutus off the screen for bonus points. The game ends when all lives are lost or a target score is reached. Physics includes gravity and ladder-climbing constraints.

## Technical Specs

- Screen Resolution: 800x600
- Frame Rate: 60 FPS
- State Space: Player position, Brutus position, Spinach position, Olive Oyl's dropped items positions, Invincibility timer
- Action Space: Move Left, Move Right, Climb Up, Climb Down, Stay

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

## How to Stop

```bash
kill -9 $(pgrep -f 'python main.py')
```

## How to Play

Use Arrow Keys to move and climb ladders. Collect items dropped from the top to increase score (+100 per item). Avoid Brutus. Collect the green spinach icon to turn blue and gain the ability to hit Brutus (+500 points). The goal is to maximize score without losing all 3 lives.

## How to Cleanup

```bash
rm -rf .venv
```
