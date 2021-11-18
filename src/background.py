import pygame


class BackgroundEffects:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 40
        self.color = (54, 127, 188)

    def update(self):
        self.y -= 5
        self.x += 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 5)
