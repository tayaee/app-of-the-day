# Vector Urban Champion: Street Brawl

A simplified 2D street fighting game focused on timing, spacing, and tactical stamina management.

## Description

This is a 1vs1 side-view brawler set on a single-screen street. Players can move left and right, block, and perform high or low punches. A stamina bar limits continuous attacking. Health decreases upon successful hits. The environment includes borders at each end of the screen; pushing the opponent off the edge wins the round.

## Game Rules

- Reduce opponent health to zero to win by KO
- Push opponent off the screen edge for a ring-out victory
- Each punch consumes stamina - manage it wisely
- High punches can be blocked with high block, low punches with low block
- Correct blocking prevents all damage
- Score 100 points per successful hit
- Score 500 bonus points for ring-out victory

## Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Move |
| A | High Punch |
| Z | Low Punch |
| S (hold) | High Block |
| X (hold) | Low Block |
| R | Restart (when game over) |

## Technical Specs

- **Resolution**: 800x400
- **Framework**: Pygame
- **State Space**: player_pos, enemy_pos, player_health, enemy_health, player_stamina, enemy_stamina, player_action_state
- **Action Space**: move_left, move_right, punch_high, punch_low, block_high, block_low, idle

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run main.py

# Or use the provided scripts
run.bat      # Windows
./run.sh     # Linux/Mac
```

## Cleanup

```bash
rm -rf .venv
```
