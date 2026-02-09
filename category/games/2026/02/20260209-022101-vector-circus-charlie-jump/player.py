"""Player entity."""

import pygame


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vel_y = 0
        self.is_jumping = False
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = -12
            self.is_jumping = True
            self.on_ground = False

    def update(self):
        self.vel_y += 0.6
        self.y += self.vel_y

        ground_y = 350
        if self.y >= ground_y:
            self.y = ground_y
            self.vel_y = 0
            self.is_jumping = False
            self.on_ground = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        # Lion body
        lion_rect = pygame.Rect(self.x - 10, self.y + 10, 50, 30)
        pygame.draw.rect(surface, (200, 150, 50), lion_rect)

        # Lion legs
        for i, leg_x in enumerate([self.x + 5, self.x + 15, self.x + 25, self.x + 35]):
            leg_y = self.y + 40 if not self.on_ground or i % 2 == 0 else self.y + 38
            pygame.draw.line(surface, (200, 150, 50), (leg_x, self.y + 40), (leg_x, leg_y), 3)

        # Player on lion
        player_rect = pygame.Rect(self.x, self.y - 25, 30, 30)
        pygame.draw.rect(surface, (255, 200, 100), player_rect)

        # Player head
        pygame.draw.circle(surface, (255, 200, 100), (int(self.x + 15), int(self.y - 30)), 12)
