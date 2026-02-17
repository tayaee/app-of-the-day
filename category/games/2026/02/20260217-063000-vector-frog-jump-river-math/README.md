# Vector Frog Jump River Math

Cross the river by jumping on lily pads with correct mathematical answers.

## Description

Guide your frog from the start zone at the bottom to the goal zone at the top. The river flows with rows of moving lily pads, each displaying a number. A math problem (e.g., "5 + 3 = ?") appears at the top. You must identify the correct answer and jump only on lily pads containing that number. Jumping on wrong answers causes the frog to sink. Lily pads move at varying speeds, and difficulty increases every 5 successful jumps.

## Features

- Grid-based movement with arrow keys
- Dynamic math problems with addition and subtraction
- Moving lily pads with varying speeds and directions
- Progressive difficulty - numbers and speed increase over time
- Score tracking with points for correct jumps and reaching the goal

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

On Windows:
```bash
run.bat
```

On Linux/Mac:
```bash
bash run.sh
```

## How to Stop

Close the game window or press ESC.

## Controls

- **Up Arrow**: Move one grid space forward
- **Down Arrow**: Move one grid space backward
- **Left Arrow**: Move one grid space left
- **Right Arrow**: Move one grid space right
- **Space**: Restart after game over or winning
- **ESC**: Quit the game

## Rules

- Solve the math problem displayed at the top
- Jump only on lily pads containing the correct answer
- Jumping on wrong numbers causes the frog to sink (game over)
- Touching the water without being on a lily pad ends the game
- Lily pads move and carry you with them - don't float off screen
- Reach the GOAL zone at the top to score 50 points
- Each correct lily pad jump earns 10 points
- Difficulty increases every 5 successful jumps

## How to Cleanup

```bash
rm -rf .venv uv.lock __pycache__
```

## RL State Space

### Observation
- Frog coordinates (x, y)
- Relative positions of lily pads in the next 3 rows
- Current math problem string
- Values on visible lily pads

### Action Space
- 0: Stay
- 1: Up
- 2: Down
- 3: Left
- 4: Right

### Reward Function
- Small positive reward for moving closer to target lily pad
- Large positive reward (+10) for landing on correct pad
- Very large positive reward (+50) for reaching opposite bank
- Large negative reward for death or wrong answer
