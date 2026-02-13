# Rhythm Pulse Beat

Hit the beat at the perfect moment in this minimalist rhythm reaction game.

## Description

A rhythm-based reaction game where expanding pulses emanate from the center of the screen. The player must time their inputs to hit when the pulse aligns with the target zone. The game features progressive difficulty with increasing BPM, combo multipliers for consecutive hits, and visual feedback for timing accuracy.

## Rationale

Rhythm games provide an excellent benchmark for reinforcement learning agents focused on temporal precision and pattern recognition. The clear state space (pulse position relative to target), discrete action space (hit or wait), and immediate reward feedback make it ideal for testing timing-based decision making. The progressive difficulty curve allows for measuring improvement over training episodes.

## Details

The game features a central target zone with pulses expanding outward at regular intervals based on the current BPM. Players press SPACE when the pulse aligns with the target circle. Timing is evaluated as:
- **Perfect**: Within 15 pixels of target (100 points)
- **Good**: Within 40 pixels of target (50 points)
- **Miss**: Beyond 40 pixels (0 points, lose a life)

The game starts at 80 BPM and increases by 10 BPM every 10 successful hits, up to a maximum of 180 BPM. Combo multipliers increase score by 10% per consecutive hit, capped at 3x. Players have 3 lives.

## Build

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## Stop

Press `ESC` or close the window.

## How to Play

Press `SPACE` when the expanding pulse aligns with the target zone circle.

**Scoring:**
- Perfect hit (within 15px): +100 points
- Good hit (within 40px): +50 points
- Miss (beyond 40px): 0 points, lose 1 life
- Combo multiplier: +10% per consecutive hit (max 3x)

**Goal:** Survive as long as possible and achieve the highest score by maintaining rhythm accuracy.

**Progression:**
- Every 10 successful hits advances to the next level
- BPM increases by 10 per level (80 BPM start, 180 BPM max)
- Game ends when all 3 lives are lost

## AI Agent Input

For RL agent control:

**State Space:**
- `screen`: (width, height) tuple
- `center`: (x, y) coordinates of screen center
- `target_radius`: radius of target zone in pixels
- `active_pulse`: { `radius`, `distance_to_target` } or None
- `beat_timer`: time until next pulse spawn
- `beat_interval`: time between pulses (based on BPM)
- `score`: current score
- `lives`: remaining lives (0-3)
- `combo`: current combo count
- `level`: current difficulty level
- `bpm`: current beats per minute
- `state`: current game state ('menu', 'playing', 'gameover')

**Action Space:**
- `hit`: Press space to attempt hitting the active pulse

**Reward Structure:**
- Perfect hit: +100
- Good hit: +50
- Miss: -100 (also loses a life)
- Combo bonus: multiplier applies to points
- Episode termination: -500 on game over

**Observation Format:**
The game state can be accessed programmatically:
```python
from game import Game

game = Game()
state = game.get_state()  # Get current state
game.handle_input('hit')  # Attempt to hit pulse
```

## Project Structure

```
category/games/2026/02/20260213-120000-rhythm-pulse-beat/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Pulse, TargetZone, HitEffect, FloatingText classes
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Input Type**: Discrete (Space key)
- **Game Engine**: Pygame 2.0+

## How to Cleanup

```bash
# Remove virtual environment
rm -rf .venv

# Remove UV lock files
rm uv.lock
```
