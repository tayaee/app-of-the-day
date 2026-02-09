# Vector Tapper Soda Dash

Serve thirsty customers and collect empty mugs in this fast-paced arcade classic.

## Description

A simplified version of the arcade classic Tapper. The player controls a bartender across four horizontal bars. Customers appear at the left side of each bar and slowly advance toward the right. The player must pour a drink and send it sliding down the bar to push the customer back and eventually make them leave.

## Gameplay

- **Goal**: Survive as long as possible while maximizing score
- **Scoring**: 50 points for serving a customer, 100 points for catching an empty mug
- **Fail conditions**:
  - A customer reaches the bartender's end
  - A drink is thrown with no customer present (breaks at the end)
  - An empty mug is not caught

## Controls

- **UP/DOWN**: Change between bars
- **LEFT/RIGHT**: Move along the current bar
- **SPACE**: Pour and throw a drink
- **ESC**: Quit game
- **R**: Restart (when game over)

## Build & Run

```bash
uv sync
uv run main.py
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Engine**: Pygame
- **State Space**: Customer positions per bar, empty mug positions, bartender current bar, bartender horizontal position
- **Action Space**: MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, THROW_DRINK

## Project Structure

```
vector-tapper-soda-dash/
├── assets/
│   └── screenshots/
├── main.py           # Main game loop and rendering
├── entities.py       # Game entities and state management
├── pyproject.toml    # UV project configuration
└── README.md
```
