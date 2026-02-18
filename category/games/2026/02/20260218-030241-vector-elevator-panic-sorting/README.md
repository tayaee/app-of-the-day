# Vector Elevator Panic Sorting

Master the rush hour by managing elevators to transport passengers to their target floors in a race against time.

## Overview

A fast-paced time-management game that challenges your prioritization skills and reaction speed. Transport passengers to their destinations before their patience runs out while managing two elevators efficiently.

## Game Rules

- **Building**: 5 floors (F5 top to F1 bottom)
- **Elevators**: 2 elevators, each with capacity for 3 passengers
- **Passengers**: Appear randomly with destination floor displayed above them
- **Timer**: Each passenger has a shrinking timer ring indicating remaining patience
- **Lives**: You start with 3 lives; lose one when a passenger times out

## How to Play

1. Use **W/S** keys to move the left elevator up/down
2. Use **Up/Down** arrow keys to move the right elevator up/down
3. Stop at a floor with waiting passengers to pick them up (automatic when stopped)
4. Stop at a passenger's destination floor to drop them off (automatic when stopped)
5. Deliver passengers before their timer runs out to score points

## Scoring

- +100 points per successful delivery
- -1 life per passenger that times out
- Game speed increases over time, making it more challenging

## Build and Run

```bash
# Create virtual environment and install dependencies
uv sync

# Start the game (Windows)
.\run.bat

# Start the game (Linux/Mac)
./run.sh

# Or manually run with Python 3.12
uv run --no-active --python 3.12 python main.py
```

## Project Structure

```
vector-elevator-panic-sorting/
├── main.py          # Entry point
├── game.py          # Game loop and rendering
├── entities.py      # Game entities (Elevator, Passenger, Building)
├── config.py        # Constants and configuration
├── run.bat          # Windows startup script
├── run.sh           # Linux/Mac startup script
├── pyproject.toml   # Dependencies
└── README.md        # This file
```

## Technical Details

- **Language**: Python 3.12+
- **Library**: Pygame
- **Display**: 800x600 resolution
- **Style**: Vector-based minimalist graphics

## Controls

| Action | Left Elevator | Right Elevator |
|--------|---------------|----------------|
| Move Up | W | Up Arrow |
| Move Down | S | Down Arrow |
| Stop | Release keys | Release keys |
| Quit | ESC | ESC |
