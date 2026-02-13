"""Entry point for Reaction Reflex Test."""

import pygame
from game import Game


def main():
    """Launch the game."""
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
