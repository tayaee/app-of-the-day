"""
Track and Field Hurdles - A rhythmic hurdle race game.

Run by alternating LEFT and RIGHT arrow keys.
Press SPACE to jump over hurdles.
Time your jumps carefully - hitting hurdles costs precious seconds!
"""

import pygame
import sys
from game_state import State, GameState
from athlete import Athlete
from hurdles import Hurdles
from renderer import Renderer


def main():
    """Main game loop."""
    pygame.init()

    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Track and Field Hurdles")

    clock = pygame.time.Clock()
    FPS = 60

    state = State()
    hurdle_positions = state.generate_hurdle_positions()
    hurdles = Hurdles(state, hurdle_positions)
    athlete = Athlete(state)
    renderer = Renderer(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    if state.state == GameState.MENU:
                        state.state = GameState.RUNNING
                    elif state.state == GameState.FINISHED:
                        # Reset for new race
                        state.reset()
                        hurdle_positions = state.generate_hurdle_positions()
                        hurdles.reset(hurdle_positions)
                        state.state = GameState.RUNNING
                    else:
                        athlete.handle_input(event.key)

                elif state.state == GameState.RUNNING:
                    athlete.handle_input(event.key)

        # Update game state
        athlete.update(dt)
        hurdles.check_collisions()
        renderer.update_camera(state)

        # Render
        if state.state in (GameState.RUNNING, GameState.COLLISION):
            renderer.draw_background(state)
            renderer.draw_finish_line(state)
            renderer.draw_hurdles(state, hurdles)
            renderer.draw_athlete(state)
            renderer.draw_ui(state, hurdles)
        elif state.state == GameState.MENU:
            renderer.draw_background(state)
            renderer.draw_menu(state)
        elif state.state == GameState.FINISHED:
            renderer.draw_background(state)
            renderer.draw_finish_line(state)
            renderer.draw_athlete(state)
            renderer.draw_finished(state)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
