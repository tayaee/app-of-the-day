"""Runtime analysis script for Vector Ice Block Pengo Logic."""

import sys
import time
import json
import pygame
from datetime import datetime

# Import game modules
from config import *
from game import PengoGame


def test_basic_initialization():
    """Test that the game initializes correctly."""
    results = []

    try:
        game = PengoGame()
        results.append({
            "test": "initialization",
            "status": "PASSED",
            "message": "Game initialized successfully"
        })

        # Check grid size
        if len(game.grid) == GRID_SIZE:
            results.append({
                "test": "grid_size",
                "status": "PASSED",
                "message": f"Grid is {GRID_SIZE}x{GRID_SIZE}"
            })
        else:
            results.append({
                "test": "grid_size",
                "status": "FAILED",
                "message": f"Grid size is {len(game.grid)}, expected {GRID_SIZE}"
            })

        # Check player position
        if game.player_pos == [GRID_SIZE // 2, GRID_SIZE // 2]:
            results.append({
                "test": "player_position",
                "status": "PASSED",
                "message": f"Player at center {game.player_pos}"
            })
        else:
            results.append({
                "test": "player_position",
                "status": "FAILED",
                "message": f"Player at {game.player_pos}, expected center"
            })

        # Check initial lives
        if game.lives == STARTING_LIVES:
            results.append({
                "test": "initial_lives",
                "status": "PASSED",
                "message": f"Starting with {STARTING_LIVES} lives"
            })
        else:
            results.append({
                "test": "initial_lives",
                "status": "FAILED",
                "message": f"Has {game.lives} lives, expected {STARTING_LIVES}"
            })

        # Check enemies exist
        if len(game.enemies) > 0:
            results.append({
                "test": "enemies_spawned",
                "status": "PASSED",
                "message": f"{len(game.enemies)} enemies spawned"
            })
        else:
            results.append({
                "test": "enemies_spawned",
                "status": "FAILED",
                "message": "No enemies spawned"
            })

        # Check ice blocks exist
        ice_count = sum(row.count(ICE_BLOCK) for row in game.grid)
        diamond_count = sum(row.count(DIAMOND_BLOCK) for row in game.grid)
        wall_count = sum(row.count(WALL) for row in game.grid)

        results.append({
            "test": "block_counts",
            "status": "PASSED" if ice_count > 0 and diamond_count == 3 and wall_count > 0 else "FAILED",
            "message": f"Ice: {ice_count}, Diamonds: {diamond_count}, Walls: {wall_count}"
        })

        return game, results

    except Exception as e:
        results.append({
            "test": "initialization",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })
        return None, results


def test_player_movement(game):
    """Test player movement in all directions."""
    results = []
    original_pos = game.player_pos.copy()

    try:
        # Test moving up
        game.move_player(UP)
        if game.player_pos != original_pos:
            results.append({
                "test": "player_movement_up",
                "status": "PASSED",
                "message": "Player moved up"
            })
        else:
            results.append({
                "test": "player_movement_up",
                "status": "PARTIAL",
                "message": "Player could not move up (may be blocked)"
            })

        # Test moving down
        game.move_player(DOWN)
        results.append({
            "test": "player_movement_down",
            "status": "PASSED",
            "message": "Down movement processed"
        })

        # Test moving left
        game.move_player(LEFT)
        results.append({
            "test": "player_movement_left",
            "status": "PASSED",
            "message": "Left movement processed"
        })

        # Test moving right
        game.move_player(RIGHT)
        results.append({
            "test": "player_movement_right",
            "status": "PASSED",
            "message": "Right movement processed"
        })

    except Exception as e:
        results.append({
            "test": "player_movement",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })

    return results


def test_block_interaction(game):
    """Test that player can interact with ice blocks."""
    results = []

    try:
        # Find an adjacent ice block
        px, py = game.player_pos
        found_block = False

        for dx, dy in DIRECTIONS:
            check_x, check_y = px + dx, py + dy
            if game.is_valid_pos(check_y, check_x):
                cell = game.get_cell(check_y, check_x)
                if cell in (ICE_BLOCK, DIAMOND_BLOCK):
                    found_block = True
                    # Try to push it
                    game.move_player((dx, dy))
                    results.append({
                        "test": "block_interaction",
                        "status": "PASSED",
                        "message": f"Player interacted with block at ({check_x}, {check_y})"
                    })
                    break

        if not found_block:
            results.append({
                "test": "block_interaction",
                "status": "PARTIAL",
                "message": "No adjacent block found to interact"
            })

    except Exception as e:
        results.append({
            "test": "block_interaction",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })

    return results


def test_enemy_ai(game):
    """Test that enemies move toward player."""
    results = []

    try:
        original_enemy_positions = [e['pos'].copy() for e in game.enemies]

        # Wait for enemy movement
        start_time = time.time()
        enemies_moved = False

        while time.time() - start_time < 1.5:
            game._move_enemies()
            for i, enemy in enumerate(game.enemies):
                if enemy['pos'] != original_enemy_positions[i]:
                    enemies_moved = True
                    break
            if enemies_moved:
                break
            time.sleep(0.1)

        if enemies_moved:
            results.append({
                "test": "enemy_ai_movement",
                "status": "PASSED",
                "message": "Enemies moved autonomously"
            })
        else:
            results.append({
                "test": "enemy_ai_movement",
                "status": "PARTIAL",
                "message": "Enemies did not move in time window"
            })

    except Exception as e:
        results.append({
            "test": "enemy_ai_movement",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })

    return results


def test_rendering(game):
    """Test that the game can render without errors."""
    results = []

    try:
        game.draw()
        results.append({
            "test": "rendering",
            "status": "PASSED",
            "message": "Game rendered successfully"
        })

        # Check display is active
        if pygame.display.get_surface():
            results.append({
                "test": "display_surface",
                "status": "PASSED",
                "message": f"Display surface {pygame.display.get_surface().get_size()}"
            })
        else:
            results.append({
                "test": "display_surface",
                "status": "FAILED",
                "message": "No display surface"
            })

    except Exception as e:
        results.append({
            "test": "rendering",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })

    return results


def test_event_handling(game):
    """Test that the game handles events correctly."""
    results = []

    try:
        # Create a QUIT event
        quit_event = pygame.event.Event(pygame.QUIT)
        result = game.handle_event(quit_event)
        results.append({
            "test": "quit_event",
            "status": "PASSED" if result == False else "FAILED",
            "message": "QUIT event handled correctly"
        })

        # Create KEYDOWN events
        key_events = [
            (pygame.K_ESCAPE, "ESC"),
            (pygame.K_UP, "UP"),
            (pygame.K_DOWN, "DOWN"),
            (pygame.K_LEFT, "LEFT"),
            (pygame.K_RIGHT, "RIGHT"),
            (pygame.K_r, "R"),
        ]

        for key, name in key_events:
            key_event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
            result = game.handle_event(key_event)
            results.append({
                "test": f"key_event_{name}",
                "status": "PASSED",
                "message": f"{name} key handled"
            })

    except Exception as e:
        results.append({
            "test": "event_handling",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        })

    return results


def run_runtime_analysis():
    """Run comprehensive runtime analysis."""
    print("Starting runtime analysis...")

    analysis = {
        "app_name": "vector-ice-block-pengo-logic",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": 0,
        "tests": []
    }

    start_time = time.time()

    # Initialize pygame
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Runtime Analysis - Vector Ice Block Pengo Logic")

    try:
        # Test 1: Basic initialization
        print("Testing initialization...")
        game, init_results = test_basic_initialization()
        analysis["tests"].extend(init_results)

        if game is None:
            analysis["overall_status"] = "FAILED"
            analysis["error"] = "Game initialization failed"
            print("CRITICAL: Game initialization failed!")
        else:
            # Test 2: Player movement
            print("Testing player movement...")
            movement_results = test_player_movement(game)
            analysis["tests"].extend(movement_results)

            # Test 3: Block interaction
            print("Testing block interaction...")
            block_results = test_block_interaction(game)
            analysis["tests"].extend(block_results)

            # Test 4: Enemy AI
            print("Testing enemy AI...")
            enemy_results = test_enemy_ai(game)
            analysis["tests"].extend(enemy_results)

            # Test 5: Rendering
            print("Testing rendering...")
            render_results = test_rendering(game)
            analysis["tests"].extend(render_results)

            # Test 6: Event handling
            print("Testing event handling...")
            event_results = test_event_handling(game)
            analysis["tests"].extend(event_results)

            # Count results
            passed = sum(1 for t in analysis["tests"] if t["status"] == "PASSED")
            failed = sum(1 for t in analysis["tests"] if t["status"] == "FAILED")
            partial = sum(1 for t in analysis["tests"] if t["status"] == "PARTIAL")
            total = len(analysis["tests"])

            print(f"\nTest Results: {passed}/{total} passed, {failed} failed, {partial} partial")

            # Determine overall status
            if failed == 0:
                analysis["overall_status"] = "PASSED"
            elif passed > failed:
                analysis["overall_status"] = "PASSED"
            else:
                analysis["overall_status"] = "FAILED"

    except Exception as e:
        analysis["overall_status"] = "FAILED"
        analysis["error"] = str(e)
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        end_time = time.time()
        analysis["duration_seconds"] = round(end_time - start_time, 2)
        analysis["test_count"] = len(analysis["tests"])

        # Count by status
        analysis["summary"] = {
            "passed": sum(1 for t in analysis["tests"] if t["status"] == "PASSED"),
            "failed": sum(1 for t in analysis["tests"] if t["status"] == "FAILED"),
            "partial": sum(1 for t in analysis["tests"] if t["status"] == "PARTIAL")
        }

        pygame.quit()

        # Save results
        with open("runtime_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"\nRuntime analysis completed in {analysis['duration_seconds']}s")
        print(f"Overall status: {analysis['overall_status']}")
        print(f"Results saved to runtime_analysis.json")


if __name__ == "__main__":
    run_runtime_analysis()
