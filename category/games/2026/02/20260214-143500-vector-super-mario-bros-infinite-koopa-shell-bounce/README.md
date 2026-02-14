# Infinite Koopa Shell Bounce

Master the art of infinite shell bouncing to achieve the highest combo score.

## Description

A precision platformer focusing on rhythmic timing and physics-based gameplay. Land on a bouncing Koopa shell repeatedly to build combos and multiply your score. Each successful bounce increases the multiplier, but missing the shell or hitting it from the side ends the game.

## Specifications

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Input**: Keyboard (Arrow keys + Space)

## How to Build

```bash
uv sync
```

## How to Start

**Windows:**
```bash
.\run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
uv run --no-active --python 3.12 python main.py
```

## How to Stop

**Windows:**
```powershell
taskkill /f /im python.exe
```

**Linux/Mac:**
```bash
pkill -f main.py
```

## How to Play

- **Left/Right Arrow**: Move horizontally
- **Space**: Jump / Kick shell (at start)
- **R**: Restart after game over
- **ESC**: Quit

### Objective

Gain points by landing on the moving shell while airborne. Each consecutive bounce without touching the ground increments the Combo counter, which multiplies the base score (10 points x combo multiplier).

### Game Over Conditions

- Touching the shell from the side
- Falling off the platform

## How to Cleanup

```bash
rm -rf .venv && rm uv.lock
```

## Reinforcement Learning

### Action Space
- `Left`: Move left
- `Right`: Move right
- `Jump`: Jump
- `None`: No action

### Observation Space
- `Player_X`, `Player_Y`: Player position
- `Shell_X`, `Shell_Y`: Shell position
- `Shell_Velocity_X`: Shell horizontal velocity
- `Is_Grounded`: Whether player is on the ground

### Reward Function
- `+10` for shell bounce (multiplied by combo)
- `+0.01` per frame survived
- `-100` for game over

## Project Structure

```
20260214-143500-vector-super-mario-bros-infinite-koopa-shell-bounce/
├── main.py           # Entry point
├── game.py           # Game logic
├── config.py         # Configuration
├── pyproject.toml    # Dependencies
├── appinfo.json      # App metadata
├── run.bat           # Windows run script
├── run.sh            # Linux/Mac run script
└── README.md         # This file
```
