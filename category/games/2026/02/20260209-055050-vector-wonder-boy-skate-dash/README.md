# Vector Wonder Boy Skate Dash

Master the momentum in this simplified side-scrolling skateboard platformer inspired by the arcade classic.

## Description

A side-scrolling endless runner featuring a skateboarder navigating through varied terrain. The player automatically moves forward while scrolling terrain includes rolling hills and pits. Jump to avoid static fire pits and rock obstacles. A constantly depleting vitality bar requires collecting fruit items to stay alive. The game ends when vitality reaches zero or the player falls into a pit.

## Controls

- **SPACE / UP ARROW**: Jump
- **R**: Restart game (when game over)
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Auto-scrolling**: The landscape scrolls automatically from right to left
- **Vitality system**: Vitality constantly depletes; collect fruit to stay alive
- **Slope physics**: The skateboard tilts based on terrain angle
- **Invincibility frames**: Brief invincibility after taking damage

### Obstacles

- **Rocks**: Static boulders on the ground (deal damage on contact)
- **Fire pits**: Animated flame hazards (deal damage on contact)
- **Pits**: Gaps in the terrain (instant death if fallen into)

### Terrain

- **Rolling hills**: Gently sloping terrain that affects skateboard angle
- **Flat ground**: Normal running surface

### Items

- **Fruit (melon)**: Collect to restore 25 vitality and gain 100 bonus points

### Scoring

- 1 point per frame survived
- 100 bonus points for each fruit collected
- Distance displayed in meters (1m per 10 points)

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
- **Physics**: Gravity-based jump curve with slope-aware skateboard rotation
