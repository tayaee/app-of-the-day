"""Game entities and state for Vector Tapper Root Beer Dash."""

import random
from dataclasses import dataclass


@dataclass
class Customer:
    """A customer at the bar."""
    bar_index: int
    x: float
    speed: float

    def update(self, dt: float) -> None:
        """Move customer toward the left."""
        self.x -= self.speed * dt

    def is_at_left_end(self) -> bool:
        """Check if customer reached the left end."""
        return self.x <= 60


@dataclass
class Mug:
    """A mug (full or empty) sliding on the bar."""
    bar_index: int
    x: float
    speed: float
    is_full: bool = True
    active: bool = True

    def update(self, dt: float) -> None:
        """Move mug."""
        if self.is_full:
            self.x += self.speed * dt
        else:
            self.x -= self.speed * dt

    def is_at_right_end(self, bar_width: float) -> bool:
        """Check if full mug reached the right end."""
        return self.x >= bar_width - 20

    def is_at_left_end(self) -> bool:
        """Check if empty mug reached the left end."""
        return self.x <= 60


class GameState:
    """Main game state manager."""

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    NUM_BARS = 4
    BAR_WIDTH = 700
    BAR_HEIGHT = 80
    BAR_SPACING = 100

    def __init__(self):
        self.customers: list[Customer] = []
        self.mugs: list[Mug] = []
        self.bartender_bar = 0
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self.spawn_timer = 0.0
        self.base_spawn_interval = 3.0
        self.current_spawn_interval = self.base_spawn_interval

    def get_bar_y(self, bar_index: int) -> int:
        """Get Y position for a bar."""
        return 80 + bar_index * self.BAR_SPACING

    def move_bartender_up(self) -> None:
        """Move bartender to upper bar."""
        if self.bartender_bar > 0:
            self.bartender_bar -= 1

    def move_bartender_down(self) -> None:
        """Move bartender to lower bar."""
        if self.bartender_bar < self.NUM_BARS - 1:
            self.bartender_bar += 1

    def can_throw_mug(self) -> bool:
        """Check if bartender can throw a mug."""
        for mug in self.mugs:
            if mug.bar_index == self.bartender_bar and mug.active and mug.is_full:
                return False
        return True

    def throw_mug(self) -> bool:
        """Throw a full mug on current bar."""
        if not self.can_throw_mug():
            return False

        mug = Mug(
            bar_index=self.bartender_bar,
            x=60,
            speed=350.0,
            is_full=True,
            active=True
        )
        self.mugs.append(mug)
        return True

    def spawn_customer(self) -> bool:
        """Spawn a new customer on a random bar."""
        bar = random.randint(0, self.NUM_BARS - 1)

        for customer in self.customers:
            if customer.bar_index == bar and customer.x > self.BAR_WIDTH - 100:
                return False

        customer = Customer(
            bar_index=bar,
            x=self.BAR_WIDTH,
            speed=25.0 + random.random() * 15.0
        )
        self.customers.append(customer)
        return True

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.game_over:
            return

        # Spawn customers
        self.spawn_timer += dt
        if self.spawn_timer >= self.current_spawn_interval:
            self.spawn_timer = 0.0
            if len(self.customers) < self.NUM_BARS * 2:
                self.spawn_customer()

            # Gradually increase difficulty
            if self.current_spawn_interval > 1.5:
                self.current_spawn_interval -= 0.02

        # Update customers
        for customer in self.customers[:]:
            customer.update(dt)
            if customer.is_at_left_end():
                self.game_over = True
                self.game_over_reason = "Customer reached the left end!"
                return

        # Update mugs
        for mug in self.mugs[:]:
            if not mug.active:
                continue

            mug.update(dt)

            if mug.is_full:
                # Full mug moving right
                for customer in self.customers[:]:
                    if customer.bar_index == mug.bar_index:
                        if abs(customer.x - mug.x) < 30:
                            # Customer caught the mug
                            mug.active = False
                            self.score += 100

                            # Customer is pushed back or leaves
                            if customer.x > self.BAR_WIDTH - 100:
                                customer.x = self.BAR_WIDTH
                            else:
                                customer.x += 60

                                # Customer leaves, send empty mug back
                                self.customers.remove(customer)
                                empty_mug = Mug(
                                    bar_index=mug.bar_index,
                                    x=customer.x,
                                    speed=250.0,
                                    is_full=False,
                                    active=True
                                )
                                self.mugs.append(empty_mug)
                            break

                # Full mug reached end with no customer
                if mug.active and mug.is_at_right_end(self.BAR_WIDTH):
                    has_customer = any(
                        c.bar_index == mug.bar_index
                        for c in self.customers
                    )
                    if not has_customer:
                        self.game_over = True
                        self.game_over_reason = "Full mug with no customer!"
                        return
                    mug.active = False

            else:
                # Empty mug moving left
                if mug.bar_index == self.bartender_bar:
                    if abs(mug.x - 60) < 30:
                        # Bartender caught the mug
                        mug.active = False
                        self.score += 50
                        continue

                # Empty mug fell off
                if mug.is_at_left_end():
                    self.game_over = True
                    self.game_over_reason = "Empty mug not caught!"
                    return

        # Clean up inactive mugs
        self.mugs = [m for m in self.mugs if m.active]

    def reset(self) -> None:
        """Reset game state."""
        self.customers.clear()
        self.mugs.clear()
        self.bartender_bar = 0
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self.spawn_timer = 0.0
        self.current_spawn_interval = self.base_spawn_interval
