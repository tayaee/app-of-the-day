# Vector Kaboom: Bomb Catch

Catch falling bombs from the Mad Bomber to save the city in this high-speed reaction challenge.

## Description

A simplified version of the classic arcade game "Kaboom!". A "Mad Bomber" moves horizontally at the top of the screen, dropping bombs at random intervals. The player controls a set of three buckets stacked vertically at the bottom. If a bomb touches a bucket, it is defused and the player gains points. If a bomb hits the ground, it explodes, and the player loses one bucket. The game ends when all buckets are lost.

## Game Rules

| Rule | Value |
|------|-------|
| Catch Score | +10 points |
| Miss Penalty | Lose 1 bucket |
| Survival Bonus | +1 point per second |
| Game Over | All 3 buckets lost |
| Difficulty | Increases with score and time |

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

Use the Left and Right arrow keys or Mouse movement to position the buckets under falling bombs. Catching a bomb increases the score. If a bomb reaches the bottom without being caught, a bucket is lost. The game concludes when all three buckets are destroyed. Press `R` to restart after game over.

## RL Environment Info

**Observation Space:** Player X position, Bomber X position, Falling Bomb coordinates (X, Y list), Current Score, Buckets Remaining

**Action Space:** Move Left, Move Right, Stay

**Reward System:** +10 for catching a bomb, -50 for losing a bucket, +1 per frame survived

## How to Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```
