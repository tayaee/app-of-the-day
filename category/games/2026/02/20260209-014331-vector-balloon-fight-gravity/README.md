# Vector Balloon Fight - Gravity

Flap your way to victory by popping enemy balloons in this gravity-based aerial combat simulator.

## Description

This game focuses on buoyancy and momentum physics, providing a unique challenge for AI agents to master precise thrust control and collision detection in a 2D space. It targets fans of classic arcade action and developers interested in physics-based movement.

## Details

The game is a simplified 2D side-scroller. The player controls a character with two balloons attached. Gravity constantly pulls the character down. Pressing the flap key provides upward momentum. Enemies fly around with their own balloons. Colliding with an enemy from above pops their balloon, causing them to fall. If an enemy touches the player from above or the side without the player being higher, the player loses a life. The level contains floating platforms that block movement.

## Physics Engine

Simplified Euler integration for velocity and position updates. Elastic collisions for wall bounces.

## Input Space

Discrete: 0 (No action), 1 (Flap/Thrust).

## Observation Space

Continuous: [player_x, player_y, player_vx, player_vy, enemy_n_x, enemy_n_y, enemy_n_active].

## Reward Structure

Score +100 for popping an enemy, +500 for clearing a wave, -10 per frame spent falling below screen bounds, -1000 for losing a life.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

```bash
killall python
```

## How to Play

Use the UP ARROW or SPACE key to flap and gain altitude. The goal is to land on top of enemies to pop their balloons. Avoid letting enemies touch you from above. Score increases with every enemy defeated and every wave completed.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
