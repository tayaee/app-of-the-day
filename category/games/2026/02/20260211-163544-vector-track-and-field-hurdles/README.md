# Vector Track and Field Hurdles

A high-speed rhythmic hurdle race challenging your timing and reaction speed.

## Description

Inspired by the classic Konami Track and Field, this game focuses on the core mechanics of speed maintenance and obstacle avoidance. The player controls an athlete in a side-scrolling hurdle race with hurdles placed at various intervals. The athlete's speed increases as the player alternates two run keys. Jumping over a hurdle requires pressing a separate jump key at the correct distance.

## Game Rules

### Speed Mechanic
Speed is gained by alternating 'Left' and 'Right' arrow keys rapidly. Pressing the same key twice in a row provides no speed boost.

### Jump Mechanic
The 'Space' key triggers a jump. The jump trajectory is determined by the current running speed - faster running results in longer jumps.

### Collision Penalty
Hitting a hurdle stops all forward momentum and costs 1.5 seconds of recovery time.

### Win Condition
Cross the finish line (1000m mark) as fast as possible.

## Technical Specifications

- **Framework**: Pygame
- **Resolution**: 800x400
- **State Space**: Athlete velocity, distance to the next hurdle, athlete's current vertical position
- **Action Space**: Run Left, Run Right, Jump, Idle

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

Or use the provided run scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press ESC or close the game window.

## How to Play

**Goal**: Reach the finish line (1000m) in the shortest time possible.

**Controls**:
- Alternately press LEFT and RIGHT arrow keys to run faster
- Press SPACEBAR to jump over hurdles

**Tips**:
- Jump when approximately 5-8 meters from a hurdle
- Maintain speed by keeping a rhythm with alternating keys
- Higher speed = longer jump distance

**Scoring**: Score is calculated based on total time taken, hurdles cleared, and hurdles hit. Faster completion with fewer collisions yields higher scores.

## How to Cleanup

```bash
rm -rf .venv
```
