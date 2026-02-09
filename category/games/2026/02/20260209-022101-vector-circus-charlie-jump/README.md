# Vector Circus Charlie Jump

Master the timing of jumping through flaming hoops in this classic circus-themed arcade challenge.

## Description

A simplified 2D side-scroller inspired by the classic circus jumping level. Control a character riding a lion moving at constant speed through obstacles including flaming hoops and fire pots.

## Technical Details

- Language: Python 3.12+
- Library: pygame-ce
- Resolution: 800x400
- Frame Rate: 60
- Input: Discrete (Jump/Idle)

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

```bash
pkill -f 'python main.py'
```

## How to Play

**Objective**: Reach the end of the stage without touching obstacles.

**Scoring**:
- +100 points for jumping through a hoop
- +50 points for jumping over a fire pot
- +50 bonus points for collecting items inside hoops

**Controls**: Press `SPACE` or `UP ARROW` to jump. Horizontal movement is automatic.

**Game Over**: Collision with any flame or obstacle ends the game.

## How to Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
```

## RL Integration

This game provides a deterministic environment for reinforcement learning:

- Fixed gravity and jump velocity
- Clear reward signals (+0.1 per frame distance, +10 per obstacle, -100 on collision)
- Discrete action space suitable for Q-learning and policy gradient methods
- Binary state representation possible for tabular methods
