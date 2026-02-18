"""Game entities for Vector Elevator Panic Sorting."""

import pygame
from config import (
    FLOOR_HEIGHT, ELEVATOR_WIDTH, ELEVATOR_HEIGHT,
    PASSENGER_SIZE, TIMER_RADIUS, COLOR_DESTINATION,
    COLOR_PASSENGER_WAITING, COLOR_PASSENGER_RIDING,
    COLOR_TIMER_HIGH, COLOR_TIMER_MED, COLOR_TIMER_LOW,
    INITIAL_PASSENGER_TIME
)


class Elevator:
    """Represents an elevator that can move between floors."""

    def __init__(self, elevator_id, x_pos, start_floor):
        self.id = elevator_id
        self.x = x_pos
        self.floor = start_floor
        self.target_floor = start_floor
        self.passengers = []
        self.capacity = 3
        self.is_moving = False

    @property
    def y(self):
        return 100 + self.floor * FLOOR_HEIGHT - ELEVATOR_HEIGHT // 2

    def move_up(self):
        """Move the elevator up."""
        if self.floor < 4:
            self.target_floor = min(4, self.target_floor + 1)
            self.is_moving = True

    def move_down(self):
        """Move the elevator down."""
        if self.floor > 0:
            self.target_floor = max(0, self.target_floor - 1)
            self.is_moving = True

    def stop(self):
        """Stop the elevator at current position."""
        self.target_floor = self.floor
        self.is_moving = False

    def update(self):
        """Update elevator position towards target floor."""
        if self.floor < self.target_floor:
            self.floor += 0.05
        elif self.floor > self.target_floor:
            self.floor -= 0.05

        # Snap to floor when close
        if abs(self.floor - self.target_floor) < 0.05:
            self.floor = self.target_floor

        # Check if movement stopped
        if abs(self.floor - self.target_floor) < 0.01:
            self.is_moving = False

    def can_pick_up(self):
        """Check if elevator can pick up passengers."""
        return len(self.passengers) < self.capacity

    def get_passengers_for_floor(self, floor_num):
        """Get passengers who want to exit at the given floor."""
        exiting = [p for p in self.passengers if p.destination == floor_num]
        self.passengers = [p for p in self.passengers if p.destination != floor_num]
        return exiting


class Passenger:
    """Represents a passenger waiting to be transported."""

    def __init__(self, spawn_floor, destination, total_time):
        self.current_floor = spawn_floor
        self.destination = destination
        self.total_time = total_time
        self.time_remaining = total_time
        self.state = "waiting"  # waiting, riding, delivered

    def update(self, dt):
        """Update passenger timer."""
        if self.state == "waiting":
            self.time_remaining -= dt

    def get_timer_color(self):
        """Get color based on remaining time."""
        ratio = self.time_remaining / self.total_time
        if ratio > 0.6:
            return COLOR_TIMER_HIGH
        elif ratio > 0.3:
            return COLOR_TIMER_MED
        return COLOR_TIMER_LOW

    def is_timeout(self):
        """Check if passenger has timed out."""
        return self.time_remaining <= 0


class Building:
    """Manages the building with floors and passengers."""

    def __init__(self, num_floors):
        self.num_floors = num_floors
        self.waiting_passengers = [[] for _ in range(num_floors)]

    def spawn_passenger(self, total_time):
        """Spawn a passenger on a random floor with a random destination."""
        import random
        spawn_floor = random.randint(0, self.num_floors - 1)
        destination = random.randint(0, self.num_floors - 1)
        while destination == spawn_floor:
            destination = random.randint(0, self.num_floors - 1)
        passenger = Passenger(spawn_floor, destination, total_time)
        self.waiting_passengers[spawn_floor].append(passenger)
        return passenger

    def get_waiting_passengers(self, floor):
        """Get all waiting passengers at a floor."""
        return self.waiting_passengers[floor]

    def remove_passengers(self, floor, passengers):
        """Remove specific passengers from waiting at a floor."""
        for p in passengers:
            if p in self.waiting_passengers[floor]:
                self.waiting_passengers[floor].remove(p)

    def get_waiting_at_floor(self, floor):
        """Get waiting passengers at a floor and clear them."""
        passengers = list(self.waiting_passengers[floor])
        self.waiting_passengers[floor] = []
        return passengers
