# Vector Tapper Soda Shop Logic

Serve thirsty customers before they reach the end of the bar in this fast-paced retro management sim.

## Description

A bartender must serve customers across four bars while managing empty mugs being returned. Customers appear from the left and advance toward the bartender. Pour drinks and send them sliding to serve customers. Catch empty mugs returning from customers to avoid breakage and earn bonus points.

## Features

- Four horizontal bars with simultaneous customer management
- Progressive difficulty with increasing speed and customer frequency
- Serve customers (+100 points) and catch empty mugs (+50 points)
- Three lives system with multiple fail conditions
- Retro vector-style graphics with smooth animations

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

Then open your browser to: `http://127.0.0.1:5000`

## How to Stop

```bash
kill -9 $(pgrep -f vector-tapper-soda-shop-logic)
```

## Controls

- **UP Arrow**: Move to upper bar
- **DOWN Arrow**: Move to lower bar
- **SPACE**: Pour and send drink sliding left

## Scoring

- Serve a customer: +100 points
- Catch an empty mug: +50 points
- Miss a customer (they reach the end): -1 life
- Throw a drink where no customer exists: -1 life
- Break an empty mug (it reaches the end): -1 life

## Game Over Conditions

The game ends when:
- A customer reaches the bartender's end of the bar, OR
- Three lives are lost

## Tips

- Keep track of all four bars simultaneously
- Prioritize customers closest to the end
- Catching mugs requires the bartender to be on the same bar
- Speed increases every 10 seconds (level up)
