"""Vector Tapper Root Beer Dash - A fast-paced arcade service game."""

import pygame
import sys

from game import GameState
from renderer import Renderer


def main():
    """Main game loop."""
    pygame.init()

    state = GameState()
    renderer = Renderer(state)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif not state.game_over:
                    if event.key == pygame.K_UP:
                        state.move_bartender_up()
                    elif event.key == pygame.K_DOWN:
                        state.move_bartender_down()
                    elif event.key == pygame.K_SPACE:
                        state.throw_mug()

                else:
                    if event.key == pygame.K_r:
                        state.reset()

        state.update(dt)
        renderer.render()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
