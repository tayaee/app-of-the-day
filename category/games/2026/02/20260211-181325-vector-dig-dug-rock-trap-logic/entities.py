"""Game entities for Dig Dug Rock Trap Logic."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import random


class EntityType(Enum):
    PLAYER = "player"
    POOKA = "pooka"
    FYGAR = "fygar"
    ROCK = "rock"


@dataclass
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def to_tuple(self):
        return (self.x, self.y)


class Entity:
    def __init__(self, x: int, y: int, entity_type: EntityType):
        self.pos = Position(x, y)
        self.entity_type = entity_type
        self.alive = True
        self.move_delay = 0
        self.move_counter = 0

    def update(self):
        self.move_counter += 1


class Player(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, EntityType.PLAYER)
        self.pump_active = False
        self.pump_direction = None
        self.pump_timer = 0
        self.pump_hit_pos = None

    def start_pump(self, direction: str):
        self.pump_active = True
        self.pump_direction = direction
        self.pump_timer = 30

    def update(self):
        super().update()
        if self.pump_active:
            self.pump_timer -= 1
            if self.pump_timer <= 0:
                self.pump_active = False
                self.pump_direction = None
                self.pump_hit_pos = None


class Enemy(Entity):
    def __init__(self, x: int, y: int, entity_type: EntityType, move_delay: int):
        super().__init__(x, y, entity_type)
        self.move_delay_max = move_delay
        self.inflation = 0  # 0 to INFLATION_REQUIRED
        self.inflation_timer = 0

    def can_move(self) -> bool:
        return self.move_counter >= self.move_delay_max

    def reset_move_counter(self):
        self.move_counter = 0

    def inflate(self):
        self.inflation += 1
        self.inflation_timer = 60

    def update(self):
        super().update()
        if self.inflation > 0:
            self.inflation_timer -= 1
            if self.inflation_timer <= 0:
                self.inflation = max(0, self.inflation - 1)
                self.inflation_timer = 60


class Pooka(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, EntityType.POOKA, 15)
        self.ghost_mode = False
        self.ghost_timer = 0
        self.ghost_duration = 120

    def toggle_ghost(self):
        self.ghost_mode = not self.ghost_mode
        if self.ghost_mode:
            self.ghost_timer = self.ghost_duration

    def update(self):
        super().update()
        if self.ghost_mode:
            self.ghost_timer -= 1
            if self.ghost_timer <= 0:
                self.ghost_mode = False


class Fygar(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, EntityType.FYGAR, 18)
        self.breath_cooldown = 0
        self.breath_cooldown_max = 180
        self.facing_right = True

    def can_breathe_fire(self) -> bool:
        return self.breath_cooldown <= 0

    def breathe_fire(self):
        self.breath_cooldown = self.breath_cooldown_max

    def update(self):
        super().update()
        if self.breath_cooldown > 0:
            self.breath_cooldown -= 1


class Rock(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, EntityType.ROCK)
        self.state = "stable"  # stable, wobbling, falling
        self.wobble_timer = 0
        self.fall_progress = 0
        self.enemies_crushed = []

    def start_wobble(self):
        if self.state == "stable":
            self.state = "wobbling"
            self.wobble_timer = 30

    def start_falling(self):
        self.state = "falling"
        self.fall_progress = 0
        self.enemies_crushed = []

    def update(self):
        super().update()
        if self.state == "wobbling":
            self.wobble_timer -= 1
            if self.wobble_timer <= 0:
                self.start_falling()
        elif self.state == "falling":
            self.fall_progress += 1


class Grid:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.cells = [[0 for _ in range(rows)] for _ in range(cols)]
        self.rocks: list[Rock] = []
        self._initialize_level()

    def _initialize_level(self):
        # Create initial tunnels (center horizontal and some vertical)
        mid_y = self.rows // 2
        mid_x = self.cols // 2

        # Center horizontal tunnel
        for x in range(self.cols):
            self.cells[x][mid_y] = 1

        # Vertical tunnels
        for y in range(self.rows):
            self.cells[mid_x][y] = 1
            self.cells[mid_x - 4][y] = 1
            self.cells[mid_x + 4][y] = 1

        # Small horizontal tunnels at different heights
        for x in range(mid_x - 2, mid_x + 3):
            self.cells[x][2] = 1
            self.cells[x][self.rows - 3] = 1

        # Place rocks in soil
        rock_positions = [
            (mid_x - 2, 2), (mid_x + 2, 2),
            (mid_x - 3, mid_y - 2), (mid_x + 3, mid_y - 2),
            (mid_x - 1, mid_y + 2), (mid_x + 1, mid_y + 2),
            (mid_x - 2, self.rows - 4), (mid_x + 2, self.rows - 4),
        ]
        for rx, ry in rock_positions:
            if 0 <= rx < self.cols and 0 <= ry < self.rows:
                # Make sure rock is in soil, not tunnel
                if self.cells[rx][ry] == 0:
                    self.rocks.append(Rock(rx, ry))

    def is_soil(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.cells[x][y] == 0

    def is_tunnel(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.cells[x][y] == 1

    def dig(self, x: int, y: int) -> bool:
        if self.is_soil(x, y):
            self.cells[x][y] = 1
            return True
        return False

    def has_solid_ground(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return True  # Border counts as solid
        return self.cells[x][y] == 0

    def get_rock_at(self, x: int, y: int) -> Optional[Rock]:
        for rock in self.rocks:
            if rock.pos.x == x and rock.pos.y == y and rock.alive:
                return rock
        return None

    def is_occupied_by_rock(self, x: int, y: int) -> bool:
        return self.get_rock_at(x, y) is not None
