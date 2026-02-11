# Vector Elevator Action Spy Escape

Navigate through a high-security building using elevators and tactical movement to retrieve documents and escape.

## Description

A stealth-action game where you play as a spy infiltrating an 11-floor building. Your mission is to collect all secret documents from red doors across multiple floors and escape via the garage in the basement. Use elevators for vertical movement and avoid or eliminate security guards.

## Game Rules

- **Scoring**: 100 points per document, 50 points per defeated enemy, 1000 bonus points for escape
- **Win Condition**: Collect all red door documents and reach the basement escape car
- **Lose Condition**: Lose 3 lives (hit by bullets or enemies)

## Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Walk horizontally |
| UP | Enter elevator and go up |
| DOWN | Enter elevator and go down / Crouch |
| SPACE | Jump |
| Z | Shoot |
| ESC | Quit game |

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press ESC key or close the game window.

## How to Play

1. Start at the top floor (Floor 10)
2. Use LEFT/RIGHT arrows to walk on each floor
3. Step into the elevator (center of screen) and use UP/DOWN to change floors
4. Pass in front of RED doors to collect secret documents
5. Avoid BLUE doors (neutral, no documents)
6. Defeat enemies with your Z key shots or dodge their fire
7. Collect all documents to activate the escape car in the basement (Floor G)
8. Reach the escape car to win

## Cleanup

```bash
rm -rf .venv && rm -f *.pyc
```

## Technical Details

- Resolution: 800x600
- Framework: Pygame-ce
- State representation: Grid-based floor system with entity vectors
- 11 floors total (10-0, where 0 is the garage/basement)
