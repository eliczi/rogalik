from .object import Object
from pygame import Vector2
import math
import random


class Flask(Object):
    name = 'flask'
    type = 'flask'
    size = (48, 48)

    def __init__(self, game, room, position=None):
        Object.__init__(self, game, self.name, self.type, self.size, room, position)
        self.dropped = False
        self.bounce = None

    def activate_bounce(self):
        self.bounce = Bounce(self.rect.x, self.rect.y, self.rect.y + 20)

    def interact(self):
        self.interaction = False
        self.show_name.reset_line_length()
        self.image = self.original_image
        self.apply_effect()
        self.game.sound_manager.play_get_item_sound()

    def draw(self):
        surface = self.room.tile_map.map_surface
        surface.blit(self.image, (self.rect.x, self.rect.y))
        if self.interaction:
            self.show_name.draw(surface, self.rect)
        self.show_price.draw(surface)
        self.show_price.update()
        self.draw_shadow(surface, -1)

    def apply_effect(self):
        pass

    def update(self):
        self.hovering.hovering()
        self.update_bounce()
        self.update_hitbox()
        if self in self.game.player.items:
            self.bounce.reset()
            self.rect.bottomright = self.game.player.hitbox.topleft


class GreenFlask(Flask):
    name = 'green_flask'
    type = 'flask'
    size = (48, 48)

    def __init__(self, game, room, position=None):
        Object.__init__(self, game, self.name, self.type, self.size, room, position)
        self.dropped = False
        self.bounce = None
        self.value = 100

    def apply_effect(self):
        # if self.game.player.hp == self.game.player.max_hp:
        #     return
        if self.game.player.hp <= self.game.player.max_hp - 20:
            self.game.player.hp += 20
        else:
            self.game.player.hp = self.game.player.max_hp
        if self.room == self.game.world_manager.current_room:
            self.room.objects.remove(self)


class RedFlask(Flask):
    name = 'red_flask'
    type = 'flask'
    size = (48, 48)

    def __init__(self, game, room, position=None):
        Object.__init__(self, game, self.name, self.type, self.size, room, position)
        self.dropped = False
        self.bounce = None
        self.value = 400


    def apply_effect(self):
        self.game.player.hp += 20
        self.game.player.max_hp += 20
        if self.room == self.game.world_manager.current_room:
            self.room.objects.remove(self)


class Bounce:
    def __init__(self, x, y, limit):
        self.speed = random.uniform(0.5, 0.7)  # 0.5
        self.angle = random.randint(-5, 5) / 10  # random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = random.uniform(0.75, 0.9)  # 0.75
        self.gravity = (math.pi, 0.002)
        self.limit = limit
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
        if self.y > self.limit:
            self.y = 2 * (self.limit) - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticity

    def reset(self):
        self.speed = 0.5
        self.angle = random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = 0.75
