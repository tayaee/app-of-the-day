"""Game entities for Vector Tapper Soda Dash."""

from dataclasses import dataclass
from enum import Enum
import pygame


class EntityType(Enum):
    CUSTOMER = "customer"
    DRINK = "drink"
    EMPTY_MUG = "empty_mug"


@dataclass
class Customer:
    """A customer at the bar."""
    bar_index: int
    x: float
    speed: float
    patience: float = 100.0

    def update(self, dt: float) -> None:
        """Move customer forward."""
        self.x += self.speed * dt

    def is_at_end(self, bar_width: float) -> bool:
        """Check if customer reached the end."""
        return self.x >= bar_width - 40


@dataclass
class Drink:
    """A drink sliding down the bar."""
    bar_index: int
    x: float
    speed: float
    active: bool = True

    def update(self, dt: float) -> None:
        """Move drink forward."""
        self.x += self.speed * dt

    def is_at_end(self, bar_width: float) -> bool:
        """Check if drink reached the end."""
        return self.x >= bar_width - 20


@dataclass
class EmptyMug:
    """An empty mug sliding back."""
    bar_index: int
    x: float
    speed: float
    active: bool = True

    def update(self, dt: float) -> None:
        """Move mug backward (towards bartender)."""
        self.x -= self.speed * dt

    def is_at_end(self) -> bool:
        """Check if mug reached the bartender end."""
        return self.x <= 60


class GameState:
    """Main game state manager."""

    def __init__(self, num_bars: int = 4):
        self.num_bars = num_bars
        self.bar_width = 700
        self.bar_height = 80
        self.bar_spacing = 100

        # Bartender state
        self.bartender_bar = 0
        self.bartender_x = 60.0
        self.bartender_speed = 200.0
        self.bartender_target_x = 60.0

        # Game entities
        self.customers: list[Customer] = []
        self.drinks: list[Drink] = []
        self.empty_mugs: list[EmptyMug] = []

        # Game state
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0

        # Movement state
        self.moving_left = False
        self.moving_right = False

    def get_bar_y(self, bar_index: int) -> int:
        """Get Y position for a bar."""
        return 50 + bar_index * self.bar_spacing

    def move_bartender_up(self) -> None:
        """Move bartender to upper bar."""
        if self.bartender_bar > 0:
            self.bartender_bar -= 1
            self.bartender_target_x = 60.0

    def move_bartender_down(self) -> None:
        """Move bartender to lower bar."""
        if self.bartender_bar < self.num_bars - 1:
            self.bartender_bar += 1
            self.bartender_target_x = 60.0

    def start_move_left(self) -> None:
        """Start moving left."""
        self.moving_left = True

    def start_move_right(self) -> None:
        """Start moving right."""
        self.moving_right = True

    def stop_move_left(self) -> None:
        """Stop moving left."""
        self.moving_left = False

    def stop_move_right(self) -> None:
        """Stop moving right."""
        self.moving_right = False

    def throw_drink(self) -> bool:
        """Throw a drink on current bar."""
        if self.game_over:
            return False

        # Check if there's already a drink on this bar
        for drink in self.drinks:
            if drink.bar_index == self.bartender_bar and drink.active:
                return False

        # Create new drink
        drink = Drink(
            bar_index=self.bartender_bar,
            x=self.bartender_x + 20,
            speed=400.0
        )
        self.drinks.append(drink)
        return True

    def spawn_customer(self) -> bool:
        """Spawn a new customer on a random bar."""
        if self.game_over:
            return False

        import random
        bar = random.randint(0, self.num_bars - 1)

        # Check if bar already has a customer
        for customer in self.customers:
            if customer.bar_index == bar and customer.x < 100:
                return False

        customer = Customer(
            bar_index=bar,
            x=0.0,
            speed=30.0 + random.random() * 20.0
        )
        self.customers.append(customer)
        return True

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.game_over:
            return

        # Update bartender position
        if self.moving_left:
            self.bartender_target_x = min(self.bar_width - 40, self.bartender_target_x + self.bartender_speed * dt)
        if self.moving_right:
            self.bartender_target_x = max(60, self.bartender_target_x - self.bartender_speed * dt)

        # Smooth movement
        diff = self.bartender_target_x - self.bartender_x
        self.bartender_x += diff * 10.0 * dt

        # Spawn customers
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            if len(self.customers) < 6:
                self.spawn_customer()

        # Update customers
        for customer in self.customers:
            customer.update(dt)
            if customer.is_at_end(self.bar_width):
                self.game_over = True
                self.game_over_reason = "Customer reached the bar!"
                return

        # Update drinks
        for drink in self.drinks:
            if not drink.active:
                continue
            drink.update(dt)

            # Check collision with customers
            for customer in self.customers:
                if customer.bar_index == drink.bar_index:
                    if abs(customer.x - drink.x) < 30:
                        # Hit!
                        customer.x -= 50  # Push back
                        drink.active = False
                        self.score += 50

                        # Check if customer leaves
                        if customer.x < 0:
                            self.customers.remove(customer)

                            # Send empty mug back
                            mug = EmptyMug(
                                bar_index=drink.bar_index,
                                x=self.bar_width - 40,
                                speed=200.0
                            )
                            self.empty_mugs.append(mug)
                        break

            # Check if drink reached end with no customer
            if drink.active and drink.is_at_end(self.bar_width):
                drink.active = False
                # Check if there's any customer on this bar
                has_customer = any(c.bar_index == drink.bar_index for c in self.customers)
                if not has_customer:
                    self.game_over = True
                    self.game_over_reason = "Drink broke at the end!"
                    return

        # Update empty mugs
        for mug in self.empty_mugs:
            if not mug.active:
                continue
            mug.update(dt)

            # Check collision with bartender
            if mug.bar_index == self.bartender_bar:
                if abs(mug.x - self.bartender_x) < 30:
                    mug.active = False
                    self.score += 100
                    continue

            # Check if mug fell
            if mug.is_at_end():
                self.game_over = True
                self.game_over_reason = "Empty mug fell!"
                return

        # Clean up inactive entities
        self.drinks = [d for d in self.drinks if d.active]
        self.empty_mugs = [m for m in self.empty_mugs if m.active]

    def reset(self) -> None:
        """Reset game state."""
        self.customers.clear()
        self.drinks.clear()
        self.empty_mugs.clear()
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self.spawn_timer = 0.0
        self.bartender_bar = 0
        self.bartender_x = 60.0
        self.bartender_target_x = 60.0
        self.moving_left = False
        self.moving_right = False
