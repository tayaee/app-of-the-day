# Retro Word Scramble Classic

A classic word puzzle game where you unscramble randomly shuffled letters to find the correct word.

## Description

The game selects a random word from a predefined list and shuffles its letters randomly. The player must look at the scrambled letters and guess the original word by typing it in. Correct answers earn points within the time limit, while wrong answers cost chances. A hint feature is available but reduces earned points by half.

## How to Build

```bash
pip install pygame
```

## How to Start

```bash
python main.py
```

## How to Stop

```bash
killall python
```

Or press `ESC` during the game.

## How to Play

- Use the keyboard to type your answer word and press `ENTER` to submit
- Correct answers earn points proportional to the word length
- Press `ESC` to quit the game
- Click the hint button or press `TAB` to get a hint (reduces points by half)
- Press `R` to restart after game over

## Examples

When the screen displays `OHELL`, the player types `HELLO` to earn 100 points and advance to the next level.

## How to Cleanup

```bash
rm -rf __pycache__
```
