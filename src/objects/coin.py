from .object import Object
import pygame
import random
import math


class Coin(Object):
    x = None
    y = None
    name = 'coin'
    object_type = 'coin'
    size = (16, 16)

    def __init__(self, game, room=None):
        self.images = []
        Object.__init__(self, game, self.name, self.object_type, self.size, room)
        self.dropped = False
        self.bounce = None
        self.animation_frame = 0
        self.value = 1

    def play_sound(self):
        self.game.sound_manager.play_coin_sound()

    def activate_bounce(self):
        self.bounce = Bounce(self.rect.x, self.rect.y, self.rect.y + random.randint(0, 123), self.size)

    def load_image(self):
        for i in range(4):
            image = pygame.image.load(f'./assets/objects/coin/{self.name}/{self.name}{i}.png').convert_alpha()
            image = pygame.transform.scale(image, self.size)
            self.images.append(image)
        self.image = self.images[0]

    def update_animation_frame(self):
        self.animation_frame += (1.5 + (random.randint(1, 5) / 10)) / 15  # random.randint(10, 20)/100
        if self.animation_frame > 3:
            self.animation_frame = 0
        self.image = self.images[int(self.animation_frame)]

    def update(self):
        self.update_animation_frame()
        self.update_bounce()
        self.magnet()
        self.update_hitbox()
        self.rect.y += 0.1

    def detect_collision(self):
        if self.game.player.hitbox.colliderect(self.rect):
            self.game.player.gold += self.value
            self.game.world_manager.current_room.objects.remove(self)
            self.play_sound()

    def magnet(self):
        dir_vector = pygame.math.Vector2(self.game.player.hitbox.center[0] - self.rect.x,
                                         self.game.player.hitbox.center[1] - self.rect.y)
        if 0 < dir_vector.length() < 200:
            speed = 1 / dir_vector.length() * 250
            dir_vector.normalize_ip()
            dir_vector.scale_to_length(speed)
            if dir_vector[0] < 1:
                dir_vector[0] = math.ceil(dir_vector[0])
            if dir_vector[1] < 1:
                dir_vector[1] = math.ceil(dir_vector[1])
            self.rect.move_ip(*dir_vector)

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 5, 3))
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        surface.blit(shape_surf, (self.rect.x + 2, self.rect.y + 20))

    def draw(self):
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)


class Emerald(Coin):
    name = 'emerald'
    object_type = 'coin'
    size = (24, 24)

    def __init__(self, game, room=None):
        super().__init__(game, room)
        self.value = 5


class Ruby(Coin):
    name = 'ruby'
    object_type = 'coin'
    size = (24, 24)

    def __init__(self, game, room=None):
        super().__init__(game, room)
        self.value = 15


def play_sound():
    pygame.mixer.Sound.play(pygame.mixer.Sound('./assets/sound/Coin.wav'))


class Bounce:
    def __init__(self, x, y, limit, size):
        self.speed = random.uniform(0.5, 0.6)  # 0.5
        self.angle = random.randint(-10, 10) / 10  # random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = random.uniform(0.75, 0.9)  # 0.75
        self.gravity = (math.pi, 0.002)
        self.limit = limit
        self.limits = [limit, 654]
        self.x, self.y = x, y
        self.size = size

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
        # if self.y > any(self.limits):
        if self.y > self.limit:
            self.y = 2 * self.limit - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticity

        elif self.y > 654 - self.size[0]:
            self.y = 2 * (654 - self.size[0]) - self.y
            self.angle = math.pi - self.angle
            self.speed *= self.elasticity

        if self.x < 198 + 10:
            self.x = 2 * (198 + 10) - self.x
            self.angle = - self.angle
            self.speed *= self.elasticity

        elif self.x > 1136 - self.size[0]:
            self.x = 2 * (1136 - self.size[0]) - self.x
            self.angle = - self.angle
            self.speed *= self.elasticity

    def reset(self):
        self.speed = 0.5
        self.angle = random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = 0.75
