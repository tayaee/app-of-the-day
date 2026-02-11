"""
Hurdle management and collision detection.
"""

from game_state import State


class Hurdles:
    """Manages hurdle positions and collision detection."""

    HURDLE_WIDTH = 8.0  # meters
    COLLISION_DISTANCE = 3.0  # distance from hurdle center to check collision

    def __init__(self, state: State, positions: list):
        self.state = state
        self.positions = positions
        self.cleared = set()  # Track which hurdles have been cleared

    def get_upcoming_hurdle(self) -> tuple:
        """Get the next hurdle that hasn't been cleared."""
        for pos in self.positions:
            if pos not in self.cleared and pos > self.state.distance:
                return pos
        return None

    def get_distance_to_next_hurdle(self) -> float:
        """Get distance to the next upcoming hurdle."""
        next_hurdle = self.get_upcoming_hurdle()
        if next_hurdle is None:
            return float('inf')
        return next_hurdle - self.state.distance

    def check_collisions(self):
        """Check for collisions with hurdles."""
        if self.state.is_in_collision():
            return

        if self.state.state.name != "RUNNING":
            return

        athlete_pos = self.state.distance

        for hurdle_pos in self.positions:
            if hurdle_pos in self.cleared:
                continue

            # Check if athlete is near hurdle
            distance_to_hurdle = hurdle_pos - athlete_pos

            # Athlete is at or just past the hurdle
            if -2.0 <= distance_to_hurdle <= self.HURDLE_WIDTH / 2:
                # Check if jumping high enough
                if self.state.vertical_position < -self.state.JUMP_CLEAR_HEIGHT:
                    # Successfully cleared
                    self.cleared.add(hurdle_pos)
                    self.state.hurdles_cleared += 1
                elif not self.state.is_jumping() and distance_to_hurdle < 1.0:
                    # Collision - wasn't jumping or didn't jump high enough
                    self.state.trigger_collision()
                    self.cleared.add(hurdle_pos)
                    return

    def reset(self, positions: list):
        """Reset hurdles for a new race."""
        self.positions = positions
        self.cleared = set()
