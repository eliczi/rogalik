from .object import Object
import pygame
import random
import math


class Coin(Object):
    x = None
    y = None
    name = 'coin'
    object_type = 'coin'
    size = (32, 32)

    def __init__(self, game, room=None, chest=None):
        self.game = game
        self.room = room
        self.chest = chest
        self.images = []
        Object.__init__(self, game, self.name, self.object_type, self.size, room, (self.x, self.y))
        self.dropped = False
        self.bounce = Bounce(self.rect.x, self.rect.y)

    def load_image(self):
        for i in range(4):
            self.images.append(pygame.image.load(f'../assets/{self.name}/{self.name}{i}.png').convert_alpha())
        self.image = self.images[0]


class Bounce:
    def __init__(self, x, y):
        self.speed = random.uniform(0.5, 0.6)  # 0.5
        self.angle = random.randint(-5, 5) / 10  # random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = random.uniform(0.75, 0.9)  # 0.75
        self.gravity = (math.pi, 0.002)
        self.limit = 6 * 64
        self.x, self.y = x, y

    @staticmethod
    def add_vectors(angle1, length1, angle2, length2):
        x = math.sin(angle1) * length1 + math.sin(angle2) * length2
        y = math.cos(angle1) * length1 + math.cos(angle2) * length2
        angle = 0.5 * math.pi - math.atan2(y, x)
        length = math.hypot(x, y)
        return angle, length

    def move(self):
        self.angle, self.speed = self.add_vectors(self.angle, self.speed, *self.gravity)
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.speed *= self.drag

    def bounce(self):
        if self.y > self.limit - 48:
            self.y = 2 * (self.limit - 48) - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticity

    def reset(self):
        self.speed = 0.5
        self.angle = random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = 0.75
