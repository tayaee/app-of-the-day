"""Main game logic and rendering for Vector Elevator Panic Sorting."""

import pygame
import random
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, NUM_FLOORS, NUM_ELEVATORS,
    ELEVATOR_CAPACITY, MAX_LIVES, POINTS_PER_DELIVERY,
    COLOR_BG, COLOR_FLOOR, COLOR_ELEVATOR, COLOR_TEXT,
    COLOR_PASSENGER_WAITING, COLOR_DESTINATION,
    BUILDING_WIDTH, BUILDING_HEIGHT, FLOOR_HEIGHT, FLOOR_Y_START,
    ELEVATOR_WIDTH, ELEVATOR_HEIGHT, PASSENGER_SIZE, TIMER_RADIUS,
    PASSENGER_SPAWN_INTERVAL, INITIAL_PASSENGER_TIME,
    SPEED_INCREASE_INTERVAL, ELEVATOR_SPEED
)
from entities import Elevator, Building


class ElevatorGame:
    """Main game class for the elevator panic sorting game."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Elevator Panic Sorting")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        # Create elevators
        elevator_spacing = BUILDING_WIDTH // (NUM_ELEVATORS + 1)
        self.elevators = []
        for i in range(NUM_ELEVATORS):
            x = 100 + elevator_spacing * (i + 1) - ELEVATOR_WIDTH // 2
            self.elevators.append(Elevator(i, x, 0))

        # Create building and game state
        self.building = Building(NUM_FLOORS)
        self.score = 0
        self.lives = MAX_LIVES
        self.passenger_time = INITIAL_PASSENGER_TIME
        self.last_spawn_time = pygame.time.get_ticks()
        self.last_speed_increase = pygame.time.get_ticks()
        self.game_over = False

    def handle_input(self):
        """Handle keyboard input for elevator controls."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Continuous key input for elevator movement
        keys = pygame.key.get_pressed()

        # Left elevator controls (W/S)
        if keys[pygame.K_w]:
            self.elevators[0].move_up()
        elif keys[pygame.K_s]:
            self.elevators[0].move_down()
        else:
            self.elevators[0].stop()

        # Right elevator controls (Up/Down arrows)
        if keys[pygame.K_UP]:
            self.elevators[1].move_up()
        elif keys[pygame.K_DOWN]:
            self.elevators[1].move_down()
        else:
            self.elevators[1].stop()

    def update(self, dt):
        """Update game state."""
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()

        # Increase game speed over time
        if current_time - self.last_speed_increase > SPEED_INCREASE_INTERVAL:
            self.passenger_time = max(3000, self.passenger_time - 500)
            self.last_speed_increase = current_time

        # Spawn new passengers
        if current_time - self.last_spawn_time > PASSENGER_SPAWN_INTERVAL:
            self.building.spawn_passenger(self.passenger_time)
            self.last_spawn_time = current_time

        # Update elevators
        for elevator in self.elevators:
            elevator.update()

            # Check for passenger pickup/dropoff when stopped at a floor
            if not elevator.is_moving and abs(elevator.floor - round(elevator.floor)) < 0.1:
                floor_num = int(round(elevator.floor))

                # Drop off passengers
                exiting = elevator.get_passengers_for_floor(floor_num)
                self.score += len(exiting) * POINTS_PER_DELIVERY

                # Pick up passengers if capacity allows
                if elevator.can_pick_up():
                    waiting = self.building.get_waiting_passengers(floor_num)
                    available_slots = elevator.capacity - len(elevator.passengers)
                    to_pick_up = waiting[:available_slots]
                    for p in to_pick_up:
                        p.state = "riding"
                    elevator.passengers.extend(to_pick_up)
                    self.building.remove_passengers(floor_num, to_pick_up)

        # Update waiting passengers
        for floor in range(NUM_FLOORS):
            waiting = list(self.building.get_waiting_passengers(floor))
            for passenger in waiting:
                passenger.update(dt)
                if passenger.is_timeout():
                    self.building.remove_passengers(floor, [passenger])
                    self.lives -= 1

        # Check game over
        if self.lives <= 0:
            self.game_over = True

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw building floors
        for i in range(NUM_FLOORS):
            y = FLOOR_Y_START + i * FLOOR_HEIGHT
            pygame.draw.rect(self.screen, COLOR_FLOOR, (100, y, BUILDING_WIDTH, 3))
            floor_text = self.small_font.render(f"F{NUM_FLOORS - i}", True, COLOR_TEXT)
            self.screen.blit(floor_text, (60, y + FLOOR_HEIGHT // 2 - 10))

        # Draw waiting passengers
        for floor in range(NUM_FLOORS):
            y = FLOOR_Y_START + floor * FLOOR_HEIGHT + FLOOR_HEIGHT // 2
            waiting = self.building.get_waiting_passengers(floor)
            for idx, passenger in enumerate(waiting):
                x = 120 + idx * 25
                self._draw_passenger(x, y, passenger)

        # Draw elevators
        for elevator in self.elevators:
            self._draw_elevator(elevator)

        # Draw UI
        self._draw_ui()

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_elevator(self, elevator):
        """Draw an elevator with its passengers."""
        rect = pygame.Rect(elevator.x, int(elevator.y), ELEVATOR_WIDTH, ELEVATOR_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_ELEVATOR, rect, border_radius=5)

        # Draw passengers inside
        for idx, passenger in enumerate(elevator.passengers):
            x = elevator.x + 8 + (idx % 2) * 18
            y = int(elevator.y) + 8 + (idx // 2) * 20
            pygame.draw.circle(self.screen, COLOR_ELEVATOR, (x + 5, y + 5), 7)
            dest_text = self.small_font.render(str(passenger.destination + 1), True, (255, 255, 255))
            self.screen.blit(dest_text, (x, y))

        # Draw elevator number
        label = self.small_font.render(str(elevator.id + 1), True, (255, 255, 255))
        self.screen.blit(label, (elevator.x + ELEVATOR_WIDTH // 2 - 5, int(elevator.y) + ELEVATOR_HEIGHT + 5))

    def _draw_passenger(self, x, y, passenger):
        """Draw a passenger with destination and timer."""
        # Draw passenger
        pygame.draw.circle(self.screen, COLOR_PASSENGER_WAITING, (x, y), PASSENGER_SIZE // 2)

        # Draw destination above
        dest_text = self.small_font.render(str(passenger.destination + 1), True, COLOR_DESTINATION)
        self.screen.blit(dest_text, (x - 5, y - 25))

        # Draw timer ring
        timer_color = passenger.get_timer_color()
        timer_ratio = passenger.time_remaining / passenger.total_time
        if timer_ratio > 0:
            start_angle = 0
            end_angle = int(timer_ratio * 360)
            pygame.draw.circle(self.screen, timer_color, (x + 10, y - 8), TIMER_RADIUS, 1)
            if end_angle > 0:
                pygame.draw.arc(self.screen, timer_color,
                               (x + 10 - TIMER_RADIUS, y - 8 - TIMER_RADIUS, TIMER_RADIUS * 2, TIMER_RADIUS * 2),
                               0, end_angle, 2)

    def _draw_ui(self):
        """Draw the user interface."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (620, 20))

        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (620, 60))

        # Controls
        controls_y = 400
        controls = [
            "Controls:",
            "Left Elevator: W/S",
            "Right Elevator: Up/Down",
            "ESC: Quit"
        ]
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, COLOR_TEXT)
            self.screen.blit(text, (620, controls_y + i * 30))

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, (255, 100, 100))
        final_score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        restart_text = self.small_font.render("Press ESC to quit", True, COLOR_TEXT)

        self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(final_score_text, (WINDOW_WIDTH // 2 - 90, WINDOW_HEIGHT // 2))
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT // 2 + 50))

    def run(self):
        """Main game loop."""
        while True:
            dt = self.clock.tick(FPS)
            self.handle_input()
            self.update(dt)
            self.draw()
