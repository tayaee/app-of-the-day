# Vector Outrun Highway Drive

Retro pseudo-3D highway racing game inspired by classic arcade titles like OutRun. Focus on high-speed dodging and distance scoring.

## Description

Experience the thrill of high-speed highway driving with this pseudo-3D racer. Navigate curving roads, dodge traffic, and push your limits as the difficulty increases with distance. The game uses 2D scaling techniques to create a convincing 3D illusion without a full 3D engine.

## Controls

- **LEFT/RIGHT arrows**: Steer the car
- **UP arrow**: Accelerate
- **DOWN arrow**: Brake
- **R**: Restart game (when crashed)
- **ESC**: Quit

## Gameplay

- **Distance Score**: Primary score based on meters traveled
- **Overtake Bonus**: +100 points for each car passed
- **Difficulty**: Traffic density increases every 1000 meters
- **Off-Road Penalty**: Speed reduces significantly when driving on grass
- **Game Over**: Crashing into another vehicle ends the run

## Technical Details

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Rendering**: Pseudo-3D using perspective projection and sprite scaling
- **State Space**: Player X position, traffic positions/distances, road curve intensity, current speed

## Build & Run

```bash
# Initialize and install dependencies
uv venv
uv pip install pygame

# Run the game
uv run main.py
```

## Cleanup

```bash
rm -rf .venv
```
