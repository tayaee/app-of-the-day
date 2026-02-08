"""Entry point for Vector Sokoban Warehouse Logic."""

import pygame
from game import Game


def main():
    """Launch the game."""
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
