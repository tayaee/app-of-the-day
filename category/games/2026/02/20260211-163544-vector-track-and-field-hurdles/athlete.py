"""
Athlete physics and input handling for hurdles.
"""

from pygame import K_LEFT, K_RIGHT, K_SPACE
from game_state import State, GameState


class Athlete:
    """Handles athlete movement, jumping, and input processing."""

    def __init__(self, state: State):
        self.state = state

    def handle_input(self, key):
        """Process keyboard input for running and jumping."""
        if self.state.state == GameState.COLLISION:
            return

        if self.state.state != GameState.RUNNING:
            return

        # Jump handling
        if key == K_SPACE:
            if not self.state.is_jumping():
                self.jump()
            return

        # Running key handling
        if key not in (K_LEFT, K_RIGHT):
            return

        current_key = "LEFT" if key == K_LEFT else "RIGHT"

        # Same key twice in a row gives no speed boost
        if self.state.last_key == current_key:
            return

        self.state.last_key = current_key
        self.accelerate()

    def jump(self):
        """Initiate a jump with velocity-based force."""
        # Jump force scales with current speed
        speed_factor = max(0.5, self.state.velocity / self.state.MAX_VELOCITY)
        self.state.vertical_velocity = -self.state.JUMP_FORCE * speed_factor

    def accelerate(self):
        """Apply acceleration."""
        self.state.velocity = min(
            self.state.velocity + self.state.VELOCITY_INCREMENT,
            self.state.MAX_VELOCITY
        )

    def update(self, dt: float):
        """Update physics for one frame."""
        if self.state.state == GameState.MENU:
            return

        # Handle collision recovery
        if self.state.state == GameState.COLLISION:
            self.state.collision_timer -= dt
            if self.state.collision_timer <= 0:
                self.state.state = GameState.RUNNING
                self.state.collision_timer = 0
            return

        if self.state.state != GameState.RUNNING:
            return

        # Apply friction
        self.state.velocity = max(0, self.state.velocity * (1 - self.state.FRICTION))

        # Update jump physics
        if self.state.is_jumping() or self.state.vertical_position > 0:
            self.state.vertical_velocity += self.state.GRAVITY * dt
            self.state.vertical_position += self.state.vertical_velocity * dt

            # Landing
            if self.state.vertical_position >= 0:
                self.state.vertical_position = 0
                self.state.vertical_velocity = 0

        # Move athlete
        self.state.distance += self.state.velocity * dt
        self.state.time_elapsed += dt

        # Check finish
        if self.state.distance >= self.state.TARGET_DISTANCE:
            self.state.state = GameState.FINISHED
            self.state.finish_time = self.state.time_elapsed
            self.state.distance = self.state.TARGET_DISTANCE
