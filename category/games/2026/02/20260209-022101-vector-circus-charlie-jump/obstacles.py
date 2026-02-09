"""Obstacle entities."""

import pygame
import random


class Hoop:
    def __init__(self, x, has_bonus=False):
        self.x = x
        self.y = 200
        self.width = 40
        self.height = 120
        self.has_bonus = has_bonus
        self.passed = False
        self.bonus_collected = False

        # Flame regions (top and bottom opening)
        self.flame_width = 10
        self.opening_y = self.y + 30
        self.opening_height = 60

    def update(self, speed):
        self.x -= speed

    def get_flame_rects(self):
        # Top flame
        top_flame = pygame.Rect(self.x, self.y, self.flame_width, self.opening_y - self.y)
        # Bottom flame
        bottom_flame = pygame.Rect(
            self.x, self.opening_y + self.opening_height,
            self.flame_width, self.y + self.height - (self.opening_y + self.opening_height)
        )
        return [top_flame, bottom_flame]

    def get_bonus_rect(self):
        if not self.has_bonus or self.bonus_collected:
            return None
        return pygame.Rect(self.x + 15, self.opening_y + 25, 10, 10)

    def check_collision(self, player_rect):
        for flame in self.get_flame_rects():
            if flame.colliderect(player_rect):
                return True
        return False

    def draw(self, surface):
        # Draw hoop structure
        hoop_color = (200, 50, 200)
        pygame.draw.line(surface, hoop_color, (self.x, self.y), (self.x + self.flame_width, self.y), 3)
        pygame.draw.line(surface, hoop_color, (self.x, self.y + self.height), (self.x + self.flame_width, self.y + self.height), 3)

        # Draw flames
        for flame in self.get_flame_rects():
            for i in range(3):
                flame_y = flame.y + i * 5
                color_intensity = 255 - i * 50
                flame_color = (color_intensity, 100 + i * 30, 0)
                pygame.draw.rect(surface, flame_color, (flame.x, flame_y, flame.width, 4))

        # Draw bonus if present
        if self.has_bonus and not self.bonus_collected:
            pygame.draw.circle(surface, (255, 255, 0), (int(self.x + 20), int(self.opening_y + 30)), 8)


class FirePot:
    def __init__(self, x):
        self.x = x
        self.y = 350
        self.width = 30
        self.height = 30
        self.passed = False

    def update(self, speed):
        self.x -= speed

    def get_rect(self):
        # Pot body
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_flame_rect(self):
        # Flame on top
        return pygame.Rect(self.x + 5, self.y - 20, 20, 25)

    def check_collision(self, player_rect):
        return self.get_flame_rect().colliderect(player_rect)

    def draw(self, surface):
        # Pot body
        pygame.draw.rect(surface, (100, 50, 50), (self.x, self.y, self.width, self.height))

        # Flame
        flame_rect = self.get_flame_rect()
        for i in range(4):
            flame_y = flame_rect.y + i * 5
            color_intensity = 255 - i * 40
            flame_color = (color_intensity, 100 + i * 30, 0)
            height = min(5, flame_rect.height - i * 5)
            if height > 0:
                pygame.draw.rect(surface, flame_color, (flame_rect.x, flame_y, flame_rect.width, height))


class ObstacleManager:
    def __init__(self):
        self.hoops = []
        self.fire_pots = []
        self.last_obstacle_x = 200
        self.stage_length = 5000

    def update(self, speed, distance):
        # Update existing obstacles
        for hoop in self.hoops[:]:
            hoop.update(speed)
            if hoop.x < -100:
                self.hoops.remove(hoop)

        for pot in self.fire_pots[:]:
            pot.update(speed)
            if pot.x < -100:
                self.fire_pots.remove(pot)

        # Spawn new obstacles
        if distance < self.stage_length:
            if self.last_obstacle_x - distance < 300:
                obstacle_type = random.choice(['hoop', 'fire_pot', 'hoop_with_bonus'])
                spawn_x = distance + random.randint(300, 500)

                if obstacle_type == 'fire_pot':
                    self.fire_pots.append(FirePot(spawn_x))
                else:
                    self.hoops.append(Hoop(spawn_x, has_bonus=(obstacle_type == 'hoop_with_bonus')))

                self.last_obstacle_x = spawn_x

    def check_collisions(self, player_rect):
        for hoop in self.hoops:
            if hoop.check_collision(player_rect):
                return True
        for pot in self.fire_pots:
            if pot.check_collision(player_rect):
                return True
        return False

    def check_passes(self, player_rect):
        score = 0
        player_center = player_rect.centerx

        for hoop in self.hoops:
            if not hoop.passed and hoop.x + hoop.width < player_center:
                hoop.passed = True
                score += 100

        for pot in self.fire_pots:
            if not pot.passed and pot.x + pot.width < player_center:
                pot.passed = True
                score += 50

        return score

    def check_bonus(self, player_rect):
        bonus_score = 0
        for hoop in self.hoops:
            if hoop.has_bonus and not hoop.bonus_collected:
                bonus_rect = hoop.get_bonus_rect()
                if bonus_rect and bonus_rect.colliderect(player_rect):
                    hoop.bonus_collected = True
                    bonus_score += 50
        return bonus_score

    def draw(self, surface):
        for hoop in self.hoops:
            hoop.draw(surface)
        for pot in self.fire_pots:
            pot.draw(surface)
