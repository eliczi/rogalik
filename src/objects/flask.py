from .object import Object
from pygame import Vector2
import math
import random


class Flask(Object):
    name = 'green_flask'
    type = 'flask'
    size = (48, 48)

    def __init__(self, game, room, position=None):
        Object.__init__(self, game, self.name, self.type, self.size, room, position)
        self.dropped = False
        self.bounce = Bounce(self.rect.x, self.rect.y)

    def interact(self):
        if not self.game.player.weapon:
            self.game.player.weapon = self
        self.game.player.items.append(self)
        if self.room == self.game.room:
            self.room.objects.remove(self)
        self.interaction = False
        self.show_name.reset_line_length()
        self.image = self.original_image

    def update(self):
        if self.bounce.speed < 0.001:
            self.dropped = False
            self.bounce.reset()
        if self.dropped:
            for _ in range(15):
                self.bounce.move()
                self.bounce.bounce()
            self.rect.x = self.bounce.x
            self.rect.y = self.bounce.y
        if self in self.game.player.items:
            self.bounce.reset()
            self.rect.bottomright = self.game.player.hitbox.topleft


class Bounce:
    def __init__(self, x, y):
        self.speed = 0.5
        self.angle = random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = 0.75
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
        if self.y > self.limit - 64:
            self.y = 2 * (self.limit - 64) - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticity

    def reset(self):
        self.speed = 0.5
        self.angle = random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = 0.75
