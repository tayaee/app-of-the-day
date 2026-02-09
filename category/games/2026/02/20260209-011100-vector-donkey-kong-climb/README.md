# Vector Donkey Kong Climb

A minimalist platformer inspired by the arcade classic, featuring vertical navigation, rolling barrels, and ladder-based climbing.

## Description

Platforming is a fundamental genre for testing spatial reasoning and timing in AI agents. This app provides a clean, vector-based environment for reinforcement learning agents to master vertical navigation, timing-based obstacle avoidance, and pathfinding in a multi-level grid structure.

## Details

The game consists of a multi-tiered construction scaffold with inclined platforms. The player controls a rectangular agent that must navigate from the bottom to the top platform where a rescue target is located. An antagonist at the top periodically releases barrels that roll down platforms and occasionally fall down ladders. The player can move horizontally, jump over barrels, and climb ladders to reach higher platforms. The game ends if the player touches a barrel. The game engine uses a 2D coordinate system for all entities with collision detection for platforms, ladders, and barrels.

## Technical Specifications

| Property | Value |
|----------|-------|
| Engine | Pygame |
| Resolution | 800x600 |
| Frame Rate | 60 |
| Input Type | Keyboard |
| State Space | Discrete grid / Continuous coordinates |
| Reward Structure | Jump barrel: +100, Reach top: +1000, Collision: -500 |

## How to Build

```bash
uv init --app
uv add pygame
```

## How to Start

```bash
uv run python main.py
```

Or using python directly:

```bash
python main.py
```

## How to Stop

Press `ESC` to quit, or close the game window.

## How to Play

**Goal:** Reach the top platform to rescue the target.

**Controls:**
- `Left` / `Right` Arrow keys: Horizontal movement
- `Up` / `Down` Arrow keys: Climb ladders (when positioned over them)
- `Spacebar`: Jump over barrels

**Scoring:**
- 100 points per barrel jumped over
- 1000 points for reaching the top platform

**Progression:** Each successful rescue advances to the next level with increased barrel spawn frequency.

**Avoid:** Touching barrels (instant game over).

## Project Structure

```
vector-donkey-kong-climb/
+-- main.py        # Main game entry point with all game logic
+-- pyproject.toml # Project configuration
+-- appinfo.json   # App metadata
+-- README.md      # This file
```
