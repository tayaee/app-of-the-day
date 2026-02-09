"""Vector Pac-Man Maze Escape - Main entry point."""

import pygame
import sys
from game import GameEngine, Direction
from renderer import Renderer


def main():
    pygame.init()
    engine = GameEngine(width=20, height=15)
    renderer = Renderer(engine)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif (engine.game_over or engine.won) and event.key == pygame.K_SPACE:
                    engine = GameEngine(width=20, height=15)
                    renderer = Renderer(engine)

                elif not engine.game_over and not engine.won:
                    if event.key == pygame.K_UP:
                        engine.player.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN:
                        engine.player.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT:
                        engine.player.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT:
                        engine.player.next_direction = Direction.RIGHT

        if not engine.game_over and not engine.won:
            engine.move_player(engine.player.next_direction)
            engine.update()

        renderer.render()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
