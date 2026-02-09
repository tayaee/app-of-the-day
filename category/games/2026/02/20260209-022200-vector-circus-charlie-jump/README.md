# Vector Circus Charlie Jump

Master the timing of jumping through flaming hoops in this classic circus-themed arcade challenge.

## Description

A simplified 2D side-scrolling action game inspired by the classic Circus Charlie arcade game. Control a circus lion with a rider as you automatically move through a circus arena. Jump through flaming hoops and over fire pots with precise timing to survive and score points.

## Controls

- **SPACE / UP ARROW**: Jump
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Auto-running**: The lion and rider move automatically at increasing speed
- **Jump timing**: Tap for small hops, hold slightly longer for higher jumps
- **Flaming hoops**: Jump through the center gap to score (+10 points)
- **Fire pots**: Jump completely over them to score (+5 points)
- **Speed progression**: Each obstacle passed increases game speed

### Obstacles

- **Flaming Hoops**: Vertical rings with fire on top and bottom, safe passage through the center
- **Fire Pots**: Ground-based obstacles with flames rising from them

### Scoring

- 10 points for passing through a flaming hoop
- 5 points for jumping over a fire pot
- Speed increases with each obstacle cleared
- Game ends on collision with any obstacle

## Build & Run

```bash
# Initialize and install dependencies
uv sync

# Run the game
uv run python main.py
```

## Cleanup

```bash
rm -rf .venv && rm pyproject.toml uv.lock
```

## Technical Details

- **Resolution**: 800x400
- **Frame Rate**: 60 FPS
- **Style**: Minimalist vector art with high contrast colors
- **AI Training**: Suitable for reinforcement learning with discrete action space and temporal observation features
