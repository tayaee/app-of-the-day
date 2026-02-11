"""Game entities: Player, Enemy, Item, Floor, Trampoline, Door, Wave."""

import pygame
import config


class Player:
    """The police mouse controlled by the player."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.rect = pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE)
        self.on_floor = False
        self.on_trampoline = False
        self.current_trampoline = None
        self.consecutive_bounces = 0
        self.facing_right = True
        self.door_cooldown = 0

    def move_left(self):
        self.vx = -config.PLAYER_SPEED
        self.facing_right = False

    def move_right(self):
        self.vx = config.PLAYER_SPEED
        self.facing_right = True

    def stop_horizontal(self):
        self.vx = 0

    def jump(self, is_trampoline: bool = False):
        force = config.TRAMPOLINE_BOUNCE_FORCE if is_trampoline else config.PLAYER_JUMP_VELOCITY
        self.vy = -force

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # Apply gravity
        if not self.on_floor and not self.on_trampoline:
            self.vy += 0.5

        # Screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x > config.SCREEN_WIDTH - config.PLAYER_SIZE:
            self.x = config.SCREEN_WIDTH - config.PLAYER_SIZE

        # Update rect
        self.rect = pygame.Rect(int(self.x), int(self.y), config.PLAYER_SIZE, config.PLAYER_SIZE)

        # Update door cooldown
        if self.door_cooldown > 0:
            self.door_cooldown -= 1

        # Reset floor/trampoline state (will be set in collision detection)
        self.on_floor = False
        self.on_trampoline = False


class Trampoline:
    """A trampoline for bouncing between floors."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.bounce_count = 0
        self.broken = False

    def get_color(self):
        if self.bounce_count == 0:
            return config.COLOR_TRAMPOLINE_SAFE
        elif self.bounce_count < config.MAX_BOUNCES - 1:
            return config.COLOR_TRAMPOLINE_WARN
        else:
            return config.COLOR_TRAMPOLINE_DANGER

    def reset(self):
        self.bounce_count = 0
        self.broken = False


class Door:
    """A door that can release a wave to push enemies."""

    def __init__(self, x: float, y: float, facing_right: bool):
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.is_open = False
        self.open_timer = 0
        self.cooldown = 0
        self.rect = pygame.Rect(x, y, config.DOOR_WIDTH, config.DOOR_HEIGHT)


class Wave:
    """A wave released from a door that pushes enemies back."""

    def __init__(self, x: float, y: float, direction: int):
        self.x = x
        self.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.lifetime = config.WAVE_DURATION
        self.width = 40
        self.height = 50

    def update(self):
        self.x += self.direction * config.WAVE_SPEED
        self.lifetime -= 1
        return self.lifetime > 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


class Floor:
    """A floor in the house."""

    def __init__(self, x: float, y: float, width: float, index: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = config.FLOOR_HEIGHT
        self.index = index
        self.rect = pygame.Rect(x, y, width, self.height)
        self.trampoline = None
        self.door = None
        self.items = []

    def add_trampoline(self, x: float):
        self.trampoline = Trampoline(x, self.y)

    def add_door(self, x: float, facing_right: bool):
        self.door = Door(x, self.y - config.DOOR_HEIGHT + 5, facing_right)


class Enemy:
    """A cat (Meowky) that chases the player."""

    def __init__(self, x: float, y: float, floor_index: int, speed: float):
        self.x = x
        self.y = y
        self.floor_index = floor_index
        self.speed = speed
        self.direction = 1  # 1 for right, -1 for left
        self.rect = pygame.Rect(x, y, config.ENEMY_SIZE, config.ENEMY_SIZE)
        self.stunned = 0
        self.push_velocity = 0

    def update(self):
        # Handle being pushed by wave
        if self.stunned > 0:
            self.x += self.push_velocity
            self.stunned -= 1
            if self.stunned <= 0:
                self.push_velocity = 0
        else:
            # Normal movement
            self.x += self.direction * self.speed

        # Update rect
        self.rect = pygame.Rect(int(self.x), int(self.y), config.ENEMY_SIZE, config.ENEMY_SIZE)

    def reverse(self):
        self.direction *= -1

    def push(self, velocity: float, duration: int):
        self.stunned = duration
        self.push_velocity = velocity


class Item:
    """A stolen item to collect."""

    def __init__(self, x: float, y: float, item_type: str):
        self.x = x
        self.y = y
        self.item_type = item_type  # "radio", "tv", "safe"
        self.collected = False
        self.rect = pygame.Rect(x, y, config.ITEM_SIZE, config.ITEM_SIZE)

    def get_points(self):
        if self.item_type == "radio":
            return config.POINTS_RADIO
        elif self.item_type == "tv":
            return config.POINTS_TV
        elif self.item_type == "safe":
            return config.POINTS_SAFE
        return 0

    def get_color(self):
        if self.item_type == "radio":
            return config.COLOR_ITEM_RADIO
        elif self.item_type == "tv":
            return config.COLOR_ITEM_TV
        elif self.item_type == "safe":
            return config.COLOR_ITEM_SAFE
        return (255, 255, 255)


class GameState:
    """Overall game state."""

    def __init__(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.level_complete = False
        self.player = None
        self.floors = []
        self.enemies = []
        self.waves = []
        self.items_collected = 0
        self.total_items = 0

    def reset(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.level_complete = False
        self._init_level()

    def next_level(self):
        self.level += 1
        self.level_complete = False
        self._init_level()

    def _init_level(self):
        self.player = Player(400, 50)
        self.floors = []
        self.enemies = []
        self.waves = []
        self.items_collected = 0

        # Create floors
        floor_width = 700
        start_x = 50
        for i in range(config.NUM_FLOORS):
            y = 100 + i * config.FLOOR_SPACING
            floor = Floor(start_x, y, floor_width, i)

            # Add trampoline to middle floors
            if 0 < i < config.NUM_FLOORS - 1:
                floor.add_trampoline(400)

            # Add doors
            floor.add_door(150, True)   # Door facing right
            floor.add_door(600, False)  # Door facing left

            self.floors.append(floor)

        # Create items based on level
        item_types = ["radio", "tv", "safe"]
        num_enemies = min(2 + self.level, 6)

        for i, floor in enumerate(self.floors):
            # Place items on floors
            num_items = 2 if i < 3 else 1
            for j in range(num_items):
                item_x = 100 + j * 200
                item_type = item_types[(i + j) % len(item_types)]
                item = Item(item_x, floor.y - config.ITEM_SIZE - 5, item_type)
                floor.items.append(item)
                self.total_items += 1

        # Create enemies
        enemy_speed = config.ENEMY_SPEED_BASE + (self.level - 1) * config.ENEMY_SPEED_INCREMENT
        for i in range(num_enemies):
            floor_idx = i % (config.NUM_FLOORS - 1) + 1
            floor = self.floors[floor_idx]
            enemy = Enemy(floor.x + 50, floor.y - config.ENEMY_SIZE, floor_idx, enemy_speed)
            self.enemies.append(enemy)

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            # Reset player position
            self.player.x = 400
            self.player.y = 50
            self.player.vx = 0
            self.player.vy = 0
