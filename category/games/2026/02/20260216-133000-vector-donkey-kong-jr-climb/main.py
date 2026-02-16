"""
Vector Donkey Kong Jr Climb
Rescue the captured giant by climbing vines and avoiding mechanical traps.
"""

import pygame
import sys
from game import Game


def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
