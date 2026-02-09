# Vector Motos: Gravity Clash

Bump enemies off the edge in a high-stakes physics-based arena combat.

## Description

Inspired by the classic arcade game Motos, this project focuses on momentum-based physics and spatial awareness. The player controls a circular unit with mass and inertia in a wall-less arena. Various enemy types populate the arena, each with different mass properties. The objective is to collide with enemies to push them off the edge while maintaining your own position.

## Controls

- **ARROW KEYS**: Apply force to move in four directions
- **SPACE**: Start game (from title screen)
- **R**: Restart game (when game over)
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Momentum-based movement**: The player unit has mass and inertia
- **Elastic collisions**: Physics-based 2D collision response between units
- **Wall-less arena**: No walls - fall off the edge and you lose a life
- **Progressive difficulty**: Arena shrinks and enemy density increases per level

### Enemy Types

- **Normal** (red): Standard mass and speed
- **Heavy** (orange): Higher mass, harder to push, slower movement
- **Fast** (magenta): Light mass, easier to push, quick and agile

### Scoring

- 100 points per enemy pushed off the edge
- Time bonus awarded when clearing all enemies
- Lives system with 3 starting lives

### Level Progression

- Arena shrinks slightly each level
- Enemy count increases (2 + level number)
- Heavy enemies appear from level 3+
- Fast enemies appear from level 2+

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

## Cleanup

```bash
rm -rf .venv
```

## Technical Details

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Engine**: Pygame
- **Physics**: Simplified 2D elastic collisions with momentum conservation
- **State Space**: Player (x, y, vx, vy), Enemy List [(x, y, mass, type)], Arena Bounds
