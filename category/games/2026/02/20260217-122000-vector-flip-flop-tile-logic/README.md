# Vector Flip Flop Tile Logic

**Category:** Games

**Description:** A strategic tile-flipping puzzle game inspired by the classic Lights Out mechanics.

## Rationale

This game targets puzzle enthusiasts and logic learners. It provides a clean, mathematical challenge that is ideal for AI agents to learn state-space search and optimization strategies, while being simple enough for any human player to understand instantly.

## Details

The game consists of a 5x5 grid of tiles. Each tile has two states: On (White) and Off (Black). When a tile is clicked (or selected by an agent), it flips its own state and the states of its four adjacent neighbors (Up, Down, Left, Right). The objective is to turn all tiles from the "On" state to the "Off" state in the minimum number of moves. The game includes a level generator that ensures every puzzle is solvable. The visual style is strictly monochromatic to maintain a professional, vector-based look.

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run main.py
```

Or use the provided scripts:

```bash
# Windows
run.bat

# Linux/macOS
./run.sh
```

## Controls

- **Mouse Left Click** - Flip a tile and its neighbors
- **R** - Reset with a new puzzle
- **ESC** - Quit

## How to Play

1. Click any tile to start the game
2. Each click flips the clicked tile and its four adjacent neighbors
3. The goal is to turn all tiles black (off)
4. Score is calculated as (1000 - moves * 10)
5. Fewer moves result in a higher score
6. Press R to generate a new solvable puzzle

## Scoring

- Base score: 1000 points
- Each move: -10 points
- Minimum score: 0 points

## AI Integration

AI agents can interact with the game through the `Game` class:

### Reward Structure

- Progress reward: Based on number of tiles off (up to 1.0)
- Solved reward: 100.0 points

### Observation Space

```python
{
    "grid_state": [bool, ...],      # 25 booleans (True = on, False = off)
    "moves": int,                    # Number of moves made
    "score": int,                    # Current score
    "is_solved": bool,               # Whether puzzle is solved
    "state": str,                    # Current game state
    "high_score": int                # Highest score achieved
}
```

### Action Space

- 0-24: Click tile at position (row * 5 + col), where row, col are 0-4

```python
# Example AI interaction
game = Game()
obs, reward, done = game.step_ai(action)  # action: 0-24
```

## How to Stop

Press ESC key or close the game window. For automation:

```bash
kill $PPID
```

## How to Cleanup

```bash
rm -rf .venv && rm uv.lock
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame
- **Grid Size:** 5x5
- **Resolution:** 700x800
- **Input:** Mouse or Action space (for AI)
