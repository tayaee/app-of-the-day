# Vector Tapper: Sushi Conveyor

Serve the right sushi to hungry customers before they reach the end of the conveyor belt.

## Description

This game tests pattern matching and reaction time. It is designed for players who enjoy time-management puzzles and serves as an excellent environment for AI agents to practice discrete action selection under temporal pressure.

## Details

The game is a simplified version of classic arcade service games. Customers appear on the right side of four horizontal conveyor belts, each requesting a specific sushi type (represented by a unique color/shape). The player controls a chef who can move vertically between the lanes. The player must press a key corresponding to the requested sushi to "throw" it down the lane. If the sushi reaches the customer, they disappear and points are awarded. If a customer reaches the left end of the belt without being served, or if the wrong sushi is thrown, the player loses a life. The speed of customers increases as the score rises.

## Technical Specifications

- Lanes: 4 horizontal conveyor belts
- Sushi Types: 3 (Salmon/Red, Cucumber/Green, Tuna/Blue)
- Frame Rate: 60 FPS
- State Space: Current lane index, customer positions per lane, customer request types, remaining lives, game speed
- Action Space: Move up/down lanes, throw sushi type 1/2/3

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press ESC in the game window or close the window.

## How to Play

- Use UP and DOWN arrow keys to switch between the 4 lanes
- Press '1', '2', or '3' keys to serve the specific sushi type requested by the customer in your current lane
- Score increases by 100 points per correct dish
- Wrong dish: -50 points and lose a life
- Missed customer (reaches left end): lose a life
- Game ends when 3 customers are missed
- Speed increases every 500 points
- Press R to restart after game over

## Agent Observations

- `current_lane_index`: 0-3, which lane the chef is currently in
- `customer_positions_per_lane`: List of x-positions for customers in each lane
- `customer_request_types`: Sushi type (0-2) for each customer
- `remaining_lives`: 0-3, lives left before game over
- `game_speed`: Current speed multiplier for customer movement

## How to Cleanup

```bash
rm -rf .venv
```
