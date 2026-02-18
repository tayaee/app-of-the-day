# Vector Popeye Spinach Power Punch

Defend Olive Oyl by punching away approaching obstacles and Brutus with spinach-powered timing.

## Description

A fixed-screen defense action game where you control Popeye in the center of the screen. Enemies (Brutus) and projectiles (bottles/anchors) approach from the left and right edges. Punch them away before they reach Olive Oyl in the center. Spinach cans appear randomly - collect them for temporary invincibility and double points. Difficulty increases as spawn rates accelerate over time.

## Features

- Center-positioned defense gameplay with left/right punch controls
- Two enemy types: Brutus enemies (100 points) and projectiles (50 points)
- Spinach power-ups that grant temporary power mode (200 points on pickup, double damage)
- Progressive difficulty with increasing spawn rates
- Three lives system with game over on defeat
- Wave counter tracking difficulty progression

## How to Build

```bash
uv run python -m pip install pygame
```

## How to Run

```bash
uv run main.py
```

## How to Stop

Press ESC or close the game window.

## Controls

- Left Arrow: Punch left
- Right Arrow: Punch right
- R: Restart after game over
- ESC: Quit game

## Rules

- Punch enemies and projectiles before they reach the center
- Hit Brutus for 100 points (200 in power mode)
- Hit projectiles for 50 points (100 in power mode)
- Collect spinach cans to activate power mode (double points, 200 bonus)
- Power mode lasts for 5 seconds
- Each enemy or projectile that reaches Olive Oyl costs one life
- Game over when all three lives are lost
- Spawn rate increases every 10 seconds

## Examples

Wait for Brutus to approach from the left, then press Left Arrow just as he enters punch range. Time your punches carefully - punching too early or too late results in a miss. When a spinach can appears, move Popeye to catch it and unleash devastating double-power punches against incoming threats.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
