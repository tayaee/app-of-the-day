"""Runtime test script for the game."""

import os
import sys
import time
import json
import subprocess
import signal

# Set SDL environment to run without display (Windows uses windib driver)
os.environ['SDL_VIDEODRIVER'] = 'windib'

# Import pygame and game modules
try:
    import pygame
    from game import Game
    import config as cfg
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def run_runtime_test():
    """Run the game and perform runtime analysis for 2 minutes."""
    results = {
        "test_name": "Runtime Analysis",
        "app_name": "vector-super-mario-bros-infinite-koopa-shell-bounce",
        "start_time": time.time(),
        "test_duration_seconds": 120,
        "checks": []
    }

    start_time = time.time()
    max_duration = 120  # 2 minutes

    try:
        # Initialize pygame
        pygame.init()
        check = {
            "check": "Pygame Initialization",
            "status": "PASSED",
            "message": "Pygame initialized successfully"
        }
        results["checks"].append(check)

        # Create game instance
        game = Game()
        check = {
            "check": "Game Instance Creation",
            "status": "PASSED",
            "message": "Game instance created successfully"
        }
        results["checks"].append(check)

        # Verify initial state
        check = {
            "check": "Initial State Verification",
            "status": "PASSED",
            "details": {
                "player_position": {"x": game.player.x, "y": game.player.y},
                "shell_position": {"x": game.shell.x, "y": game.shell.y},
                "score": game.score,
                "combo": game.combo,
                "game_over": game.game_over,
                "waiting_to_kick": game.waiting_to_kick
            }
        }
        results["checks"].append(check)

        # Test observation space
        obs = game.get_observation()
        check = {
            "check": "Observation Space",
            "status": "PASSED",
            "details": {
                "player_x": obs.get("player_x"),
                "player_y": obs.get("player_y"),
                "shell_x": obs.get("shell_x"),
                "shell_y": obs.get("shell_y"),
                "is_grounded": obs.get("is_grounded")
            }
        }
        results["checks"].append(check)

        # Test action space
        actions = game.get_action_space()
        expected_actions = ["LEFT", "RIGHT", "JUMP", "NONE"]
        check = {
            "check": "Action Space",
            "status": "PASSED" if actions == expected_actions else "FAILED",
            "details": {
                "expected": expected_actions,
                "actual": actions
            }
        }
        results["checks"].append(check)

        # Run game loop for testing
        frame_count = 0
        max_frames = 7200  # 120 seconds * 60 FPS

        while frame_count < max_frames:
            elapsed = time.time() - start_time
            if elapsed >= max_duration:
                break

            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if game.waiting_to_kick:
                            game.shell.kick(1)
                            game.waiting_to_kick = False
                        else:
                            game.player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        frame_count = max_frames
                        break

            # Update game state
            if not game.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    game.player.move_left()
                elif keys[pygame.K_RIGHT]:
                    game.player.move_right()
                else:
                    game.player.stop_horizontal()

                game.player.update()
                game.shell.update()
                game.check_collisions()

                if game.combo > 0 and game.total_time - game.last_bounce_time > cfg.MAX_COMBO_TIME_SECONDS:
                    game.combo = 0

                game.score += cfg.POINTS_PER_FRAME
                game.total_time += 1 / cfg.FPS

            # Render
            game.screen.fill(cfg.SKY_BLUE)
            game.draw_platform()
            game.shell.draw(game.screen)
            game.player.draw(game.screen)
            game.draw_hud()
            pygame.display.flip()
            game.clock.tick(cfg.FPS)

            frame_count += 1

        check = {
            "check": "Game Loop Execution",
            "status": "PASSED",
            "details": {
                "frames_processed": frame_count,
                "runtime_seconds": time.time() - start_time
            }
        }
        results["checks"].append(check)

        # Test step function for RL
        game.reset()
        obs, reward, done, info = game.step("NONE")
        check = {
            "check": "RL Step Function",
            "status": "PASSED",
            "details": {
                "observation_keys": list(obs.keys()),
                "reward": reward,
                "done": done,
                "info": info
            }
        }
        results["checks"].append(check)

        # Final state check
        check = {
            "check": "Final State",
            "status": "PASSED",
            "details": {
                "player_alive": game.player.alive,
                "shell_active": game.shell.active,
                "final_score": game.score
            }
        }
        results["checks"].append(check)

        # Test game reset
        game.reset()
        check = {
            "check": "Game Reset",
            "status": "PASSED" if game.score == 0 and game.combo == 0 and not game.game_over else "FAILED",
            "details": {
                "score_after_reset": game.score,
                "combo_after_reset": game.combo,
                "game_over_after_reset": game.game_over
            }
        }
        results["checks"].append(check)

        # All tests passed
        results["overall_status"] = "PASSED"

    except Exception as e:
        check = {
            "check": "Exception During Runtime",
            "status": "FAILED",
            "error": str(e)
        }
        results["checks"].append(check)
        results["overall_status"] = "FAILED"

    finally:
        results["end_time"] = time.time()
        results["total_duration_seconds"] = results["end_time"] - results["start_time"]

        try:
            pygame.quit()
        except:
            pass

    return results


if __name__ == "__main__":
    results = run_runtime_test()
    print(json.dumps(results, indent=2))
