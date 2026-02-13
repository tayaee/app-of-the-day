# Reaction Reflex Test

Test your reaction speed by clicking targets as quickly as possible before they disappear.

## Description

A minimalist reaction time testing game where circular targets appear at random locations on screen. Each target shrinks over time - click it before it vanishes. Clicking while the target is large yields more points. As your score increases, targets spawn faster and shrink more quickly. Three misses ends the game.

## Rationale

This game provides a pure measure of reaction time and visual processing speed. It targets anyone interested in measuring and improving their reflexes, as well as AI agents learning to respond to visual stimuli with minimal latency.

## Details

The game area is an 800x600 window where red circles appear at random positions. Each circle starts at 50px radius and shrinks continuously. The player must click the circle with the mouse before it disappears.

**Scoring:**
- Points awarded based on remaining radius when clicked (larger = more points)
- Maximum 100 points per target if clicked instantly
- Clicking empty space counts as a miss

**Difficulty:**
- Targets spawn faster as score increases
- Targets shrink faster as score increases
- Multiple targets can be on screen simultaneously

**Game Over:**
- 3 missed targets (clicked empty space or let target vanish)
- Game over screen shows final score
- Press R to restart, ESC to quit

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## Stop

Press `ESC` or close the window.

## How to Play

Use your mouse to click the appearing red circles as quickly as possible.

**Controls:**
- **Mouse Left Click** - Click target
- **ESC** - Quit game
- **R** - Restart (when game over)

**Scoring:**
- Up to 100 points per target based on speed
- Faster clicks = more points
- 3 misses allowed before game ends

## AI Agent Input

For RL agent control:

**Observation Space:**
- 800x600 pixel array or normalized positions:
  - Target positions (x, y, radius) for up to N active targets
  - Current score
  - Misses remaining

**Action Space:**
- Continuous: (x, y) click position
- Discrete: [CLICK] at specific target

**Reward Structure:**
- +(radius * 2) for successful click
- -50 for miss (empty click or target vanished)
- Game ends at 3 misses

**Optimal Strategy:**
Prioritize larger targets (newer spawns) for maximum points. Minimize distance traveled between clicks.

## Project Structure

```
category/games/2026/02/20260213-130000-reaction-reflex-test/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
├── appinfo.json     - App metadata
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Input Type**: Mouse (position + click)
- **Language**: Python 3.12+
- **Library**: pygame-ce
- **Max Targets**: Unlimited (dynamic spawning)
