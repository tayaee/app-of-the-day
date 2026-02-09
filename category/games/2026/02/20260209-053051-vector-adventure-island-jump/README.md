# Vector Adventure Island Jump

Navigate a prehistoric landscape by jumping over obstacles and collecting fruit to maintain stamina.

## Description

A simplified version of the classic Adventure Island. Control a character moving from left to right across a continuously scrolling landscape. Obstacles include rocks (static) and snails (moving). The player has a stamina bar that constantly depletes; it can be replenished by collecting floating fruit. Touching an obstacle or running out of stamina results in a game over. The speed of the game increases slightly every 100 points.

## Controls

- **SPACE / UP ARROW**: Jump (press again for double jump)
- **DOWN ARROW**: Duck (avoid high obstacles)
- **R**: Restart game (when game over)
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Auto-scrolling**: The landscape scrolls automatically from right to left
- **Stamina system**: Stamina constantly depletes; collect fruit to stay alive
- **Double jump**: Press jump again while in the air for extra height
- **Ducking**: Hold down to duck under certain obstacles
- **Speed progression**: Game speed increases every 100 points

### Obstacles

- **Rocks (triangular)**: Static obstacles on the ground
- **Snails (rectangular)**: Moving obstacles that crawl toward the player

### Items

- **Fruit (circular)**: Collect to restore 30 stamina and gain 50 bonus points

### Scoring

- 1 point per frame survived
- 50 bonus points for each fruit collected
- Speed increases every 100 points (up to a maximum)

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

- **Resolution**: 800x400
- **Frame Rate**: 60 FPS
- **Style**: Minimalist vector art with high contrast colors
- **Physics**: Gravity-based jump curve with acceleration
