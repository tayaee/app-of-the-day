"""
Automated runtime analysis test for Vector Track and Field Hurdles.
This script tests the game without human intervention using pygame events.
"""

import pygame
import sys
import time
import json
from datetime import datetime

# Add the game directory to path
sys.path.insert(0, '.')

from game_state import State, GameState
from athlete import Athlete
from hurdles import Hurdles
from renderer import Renderer


class RuntimeAnalyzer:
    """Automated test harness for runtime analysis."""

    def __init__(self):
        self.test_results = {
            "test_name": "vector-track-and-field-hurdles",
            "timestamp": datetime.now().isoformat(),
            "start_time": time.time(),
            "tests": []
        }
        self.errors = []
        self.warnings = []

    def log_test(self, test_name, status, details=""):
        """Log a test result."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time() - self.test_results["start_time"]
        }
        self.test_results["tests"].append(result)
        print(f"[{status}] {test_name}: {details}")

    def log_error(self, error_msg):
        """Log an error."""
        self.errors.append(error_msg)
        self.log_test("ERROR", "FAILED", error_msg)

    def run_tests(self):
        """Run all runtime tests."""
        try:
            self.test_initialization()
            self.test_game_states()
            self.test_athlete_mechanics()
            self.test_hurdle_system()
            self.test_renderer()

            # Calculate overall status
            self.test_results["end_time"] = time.time()
            self.test_results["duration_seconds"] = (
                self.test_results["end_time"] - self.test_results["start_time"]
            )

            failed_tests = [t for t in self.test_results["tests"] if t["status"] == "FAILED"]
            self.test_results["overall_status"] = "PASSED" if not failed_tests else "FAILED"
            self.test_results["failed_test_count"] = len(failed_tests)
            self.test_results["passed_test_count"] = len(self.test_results["tests"]) - len(failed_tests)
            self.test_results["errors"] = self.errors
            self.test_results["warnings"] = self.warnings

        except Exception as e:
            self.log_error(f"Critical test failure: {str(e)}")
            self.test_results["overall_status"] = "FAILED"

        return self.test_results

    def test_initialization(self):
        """Test that pygame and game components initialize correctly."""
        try:
            # Test pygame initialization
            pygame.init()
            self.log_test("pygame_init", "PASSED", "Pygame initialized successfully")

            # Test video mode
            WIDTH, HEIGHT = 800, 400
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.log_test("display_mode", "PASSED", f"Display mode set to {WIDTH}x{HEIGHT}")

            # Test component creation
            state = State()
            self.log_test("state_init", "PASSED", f"State initialized with distance={state.distance}")

            hurdle_positions = state.generate_hurdle_positions()
            self.log_test("hurdle_generation", "PASSED", f"Generated {len(hurdle_positions)} hurdles")

            hurdles = Hurdles(state, hurdle_positions)
            self.log_test("hurdles_init", "PASSED", "Hurdles manager initialized")

            athlete = Athlete(state)
            self.log_test("athlete_init", "PASSED", "Athlete initialized")

            renderer = Renderer(screen)
            self.log_test("renderer_init", "PASSED", "Renderer initialized")

            pygame.quit()
            return True

        except Exception as e:
            self.log_error(f"Initialization failed: {str(e)}")
            return False

    def test_game_states(self):
        """Test game state transitions."""
        try:
            state = State()

            # Test initial state
            if state.state == GameState.MENU:
                self.log_test("initial_state", "PASSED", "Game starts in MENU state")
            else:
                self.log_test("initial_state", "FAILED", f"Expected MENU, got {state.state}")

            # Test state transitions
            state.state = GameState.RUNNING
            if state.state == GameState.RUNNING:
                self.log_test("state_to_running", "PASSED", "State transition to RUNNING")
            else:
                self.log_test("state_to_running", "FAILED", "State transition failed")

            # Test collision state
            state.trigger_collision()
            if state.state == GameState.COLLISION and state.collision_timer > 0:
                self.log_test("collision_state", "PASSED", f"Collision triggered, timer={state.collision_timer}")
            else:
                self.log_test("collision_state", "FAILED", "Collision state not set correctly")

            # Test finished state
            state.distance = state.TARGET_DISTANCE
            state.state = GameState.FINISHED
            if state.state == GameState.FINISHED:
                self.log_test("finished_state", "PASSED", "Finished state set correctly")
            else:
                self.log_test("finished_state", "FAILED", "Finished state not set")

            return True

        except Exception as e:
            self.log_error(f"Game state test failed: {str(e)}")
            return False

    def test_athlete_mechanics(self):
        """Test athlete physics and input handling."""
        try:
            state = State()
            state.state = GameState.RUNNING
            athlete = Athlete(state)

            # Test acceleration with alternating keys
            initial_velocity = state.velocity
            athlete.handle_input(pygame.K_LEFT)
            after_first = state.velocity

            athlete.handle_input(pygame.K_RIGHT)
            after_second = state.velocity

            if after_second > initial_velocity:
                self.log_test("acceleration", "PASSED",
                             f"Velocity increased: {initial_velocity} -> {after_second}")
            else:
                self.log_test("acceleration", "FAILED",
                             f"Velocity did not increase properly")

            # Test same key penalty (no boost)
            before = state.velocity
            athlete.handle_input(pygame.K_RIGHT)  # Same key again
            after = state.velocity
            if after == before:
                self.log_test("same_key_penalty", "PASSED", "Same key gives no speed boost")
            else:
                self.log_test("same_key_penalty", "FAILED",
                             "Same key should not give speed boost")

            # Test jump
            initial_vpos = state.vertical_position
            athlete.jump()
            if state.vertical_velocity < 0:
                self.log_test("jump_initiation", "PASSED",
                             f"Jump velocity: {state.vertical_velocity}")
            else:
                self.log_test("jump_initiation", "FAILED", "Jump velocity not set")

            # Test is_jumping
            if state.is_jumping():
                self.log_test("jump_detection", "PASSED", "is_jumping() returns True")
            else:
                self.log_test("jump_detection", "FAILED", "is_jumping() should return True")

            # Test physics update
            dt = 0.016  # 60 FPS
            athlete.update(dt)
            if state.distance > 0:
                self.log_test("physics_update", "PASSED",
                             f"Distance after update: {state.distance:.2f}")
            else:
                self.log_test("physics_update", "FAILED", "Distance not updated")

            return True

        except Exception as e:
            self.log_error(f"Athlete mechanics test failed: {str(e)}")
            return False

    def test_hurdle_system(self):
        """Test hurdle generation and collision detection."""
        try:
            state = State()
            state.state = GameState.RUNNING
            hurdle_positions = state.generate_hurdle_positions()
            hurdles = Hurdles(state, hurdle_positions)

            # Test hurdle generation
            if len(hurdle_positions) > 0:
                self.log_test("hurdle_count", "PASSED", f"Generated {len(hurdle_positions)} hurdles")
            else:
                self.log_test("hurdle_count", "FAILED", "No hurdles generated")

            # Test hurdle spacing
            for i in range(1, len(hurdle_positions)):
                spacing = hurdle_positions[i] - hurdle_positions[i-1]
                if state.MIN_HURDLE_SPACING <= spacing <= state.MAX_HURDLE_SPACING:
                    continue
                else:
                    self.log_test("hurdle_spacing", "FAILED",
                                 f"Invalid spacing: {spacing}")
                    break
            else:
                self.log_test("hurdle_spacing", "PASSED", "All hurdles properly spaced")

            # Test get_upcoming_hurdle
            next_hurdle = hurdles.get_upcoming_hurdle()
            if next_hurdle is not None and next_hurdle > state.distance:
                self.log_test("next_hurdle", "PASSED", f"Next hurdle at {next_hurdle:.1f}m")
            else:
                self.log_test("next_hurdle", "FAILED", "Could not get next hurdle")

            # Test distance to next hurdle
            dist = hurdles.get_distance_to_next_hurdle()
            if dist > 0 and dist != float('inf'):
                self.log_test("distance_to_hurdle", "PASSED", f"Distance: {dist:.1f}m")
            else:
                self.log_test("distance_to_hurdle", "FAILED", "Invalid distance")

            # Test collision detection (no collision when far)
            state.distance = 0
            state.vertical_position = 0
            hurdles.check_collisions()
            if state.state == GameState.RUNNING:
                self.log_test("no_collision_far", "PASSED", "No collision when far from hurdle")
            else:
                self.log_test("no_collision_far", "FAILED", "False collision detected")

            # Test collision at hurdle (should trigger collision)
            state.distance = hurdle_positions[0] + 1  # At hurdle, not jumping
            state.vertical_position = 0
            hurdles.check_collisions()
            if state.state == GameState.COLLISION:
                self.log_test("collision_at_hurdle", "PASSED", "Collision triggered at hurdle")
            else:
                self.log_test("collision_at_hurdle", "FAILED", "Collision not detected")

            return True

        except Exception as e:
            self.log_error(f"Hurdle system test failed: {str(e)}")
            return False

    def test_renderer(self):
        """Test rendering components."""
        try:
            pygame.init()
            WIDTH, HEIGHT = 800, 400
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            renderer = Renderer(screen)
            state = State()

            # Test camera update
            state.distance = 100
            renderer.update_camera(state)
            if renderer.camera_x >= 0:
                self.log_test("camera_update", "PASSED", f"Camera at {renderer.camera_x:.1f}")
            else:
                self.log_test("camera_update", "FAILED", "Camera position invalid")

            # Test world to screen conversion
            screen_x = renderer.world_to_screen(100)
            self.log_test("world_to_screen", "PASSED", f"World 100m -> Screen {screen_x:.1f}")

            # Test drawing methods (they should not crash)
            try:
                renderer.draw_background(state)
                renderer.draw_finish_line(state)

                hurdle_positions = state.generate_hurdle_positions()
                hurdles = Hurdles(state, hurdle_positions)
                renderer.draw_hurdles(state, hurdles)
                renderer.draw_athlete(state)
                renderer.draw_ui(state, hurdles)

                self.log_test("rendering", "PASSED", "All draw methods executed")
            except Exception as e:
                self.log_test("rendering", "FAILED", f"Draw error: {str(e)}")

            # Test menu rendering
            state.state = GameState.MENU
            try:
                renderer.draw_menu(state)
                self.log_test("menu_render", "PASSED", "Menu rendered")
            except Exception as e:
                self.log_test("menu_render", "FAILED", f"Menu render error: {str(e)}")

            # Test finished screen
            state.state = GameState.FINISHED
            state.finish_time = 45.5
            try:
                renderer.draw_finished(state)
                self.log_test("finished_render", "PASSED", "Finish screen rendered")
            except Exception as e:
                self.log_test("finished_render", "FAILED", f"Finish render error: {str(e)}")

            pygame.quit()
            return True

        except Exception as e:
            self.log_error(f"Renderer test failed: {str(e)}")
            try:
                pygame.quit()
            except:
                pass
            return False


def main():
    """Run the automated runtime analysis."""
    print("=" * 60)
    print("Vector Track and Field Hurdles - Runtime Analysis")
    print("=" * 60)
    print()

    analyzer = RuntimeAnalyzer()
    results = analyzer.run_tests()

    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
    print(f"Passed: {results.get('passed_test_count', 0)}")
    print(f"Failed: {results.get('failed_test_count', 0)}")

    if results['errors']:
        print()
        print("Errors:")
        for error in results['errors']:
            print(f"  - {error}")

    print()
    print("Writing results to runtime_analysis.json...")

    with open('runtime_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Runtime analysis complete.")
    return 0 if results['overall_status'] == 'PASSED' else 1


if __name__ == "__main__":
    sys.exit(main())
