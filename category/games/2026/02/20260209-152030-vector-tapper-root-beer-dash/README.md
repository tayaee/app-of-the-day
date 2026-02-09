# Vector Tapper Root Beer Dash

Serve drinks to thirsty customers and collect empty mugs before they crash in this high-speed service simulation.

## Description

This game focuses on multi-tasking and queue management. It targets players who enjoy retro arcade challenges that test reaction time and resource prioritization. It provides an excellent environment for AI agents to learn optimal pathing and state-based decision making.

The game consists of four horizontal bars (aisles). Customers appear at the right end of each bar and slowly move toward the left. The player (bartender) can move between the left ends of the four bars. The player must fill a mug and send it sliding down the bar to reach a customer. If a customer receives a mug, they are pushed back or exit. The customer then eventually slides an empty mug back toward the left. The player must catch these empty mugs. The game ends if a customer reaches the left end of the bar, if a full mug is sent down a bar with no customer, or if the player fails to catch an empty mug returning to the left.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Play

Use the UP and DOWN arrow keys to move the bartender between the four aisles. Press the SPACE bar to pour and send a drink. Score 100 points for every customer served and 50 points for every empty mug collected. Avoid letting customers reach the left side or letting mugs fall off the counter.

## How to Stop

Ctrl+C or close the window

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specs

- Resolution: 800x600
- FPS: 60
- Input: Keyboard
- State Space: Customer positions, Bartender position, Mug positions
- Action Space: UP, DOWN, SPACE, IDLE
