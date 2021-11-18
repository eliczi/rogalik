import random

import pygame
import utils
from collections import namedtuple


class BackgroundEffects:
    class Circle:
        def __init__(self,radius, color, x, y, width):
            self.radius = radius
            self.color = color
            self.x = x
            self.y = y
            self.width = width

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.color = (54, 127, 188)
        self.surface = pygame.Surface((utils.world_size[0] / 4, utils.world_size[1] / 4)).convert_alpha()
        self.circles = []
        self.counter = 0

    def update(self):
        if self.counter == 3:
            self.counter = 0
            for circle in self.circles:
                circle.y -= 1
        else:
            self.counter += 1
        #if random.randint(1, 10) % 10 == 0:
            #self.add_circle()

    def add_circle(self):
        radius = random.randint(4, 25)
        color = (self.color[0] + random.randint(-50, 50), self.color[1] + random.randint(-5, 5),
                 self.color[2] + random.randint(-5, 5))
        x, y = random.randint(-100, utils.world_size[0] + 100), utils.world_size[1]/4
        width = random.randint(0, 25)
        self.circles.append(self.Circle(radius, color, x, y, width))

    def draw(self, surface):
        self.surface.fill((0, 0, 0, 0))
        for circle in self.circles:
            pygame.draw.circle(self.surface, circle.color, (circle.x, circle.y), circle.radius, circle.width)
        surface.blit(pygame.transform.scale(self.surface, (utils.world_size[0], utils.world_size[1])), (0, 0))
