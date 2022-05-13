import pygame
import random
from math import sin
import math
import src.utils as utils
import time
from src.objects.coin import Bounce
from src.objects.hole import Hole


class Particle:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.life = None  # how long should particle live(frames)


class EnemyHitParticle(Particle):
    color = (255, 0, 0)
    radius = random.randint(3, 8)

    def update(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)
        self.radius -= 0.20
        if self.radius <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)


class WallHitParticle(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = (128, 148, 171)
        self.radius = 10

    def update(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)
        self.radius -= 0.7

        if self.radius <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)


class Fire(Particle):
    """Besides some calculations and magic variables, there is a bsurf Surface in game class, which serves as screen
    to display fire plarticles, it is 4x times smaller than default window, but during blitting, it is resized to
    window size, as to achieve pixelated fire)"""

    def __init__(self, game, x, y, option='normal'):
        super().__init__(game, x, y)
        self.color = ((255, 255, 0),
                      (255, 173, 51),
                      (247, 117, 33),
                      (191, 74, 46),
                      (115, 61, 56),
                      (61, 38, 48))
        if option == 'normal':
            self.max_life = random.randint(6, 13)
            self.life = self.max_life
            self.sin = random.randint(-10, 10) / 7
            self.sin_r = random.randint(5, 10)
            self.radius = random.randint(0, 4)
            self.ox = random.randint(-1, 1)
            self.oy = random.randint(-1, 1)
            self.j = random.randint(0, 360)
            self.i = int(((self.life - 1) / self.max_life) * 6)
            self.alpha = None
        elif option == 'enemy':
            self.max_life = random.randint(6, 9)
            self.life = self.max_life
            self.sin = random.randint(-10, 10) / 7
            self.sin_r = random.randint(5, 10)
            self.radius = random.randint(0, 2)
            self.ox = random.randint(-1, 1)
            self.oy = random.randint(-1, 1)
            self.j = random.randint(0, 360)
            self.i = int(((self.life - 1) / self.max_life) * 6)
            self.alpha = None
        self.draw_x = x
        self.draw_y = y

    def update(self):
        if random.randint(1, 4) == 2:
            if self.j > 360:  # Angle
                self.j = 0
            self.life -= 1
            if self.life == 0:
                self.game.particle_manager.fire_particles.remove(self)
            self.i = int((self.life / self.max_life) * 6)
            self.y -= 0.7  # rise
            self.x += 0  # ((self.sin * sin(self.j / self.sin_r)) / 20)  # spread
            if not random.randint(0, 5):
                self.radius += 0.2  # circle radius, set to 10 for big bang
            self.draw_x, self.draw_y = self.x, self.y
            self.draw_x += self.ox * (5 - self.i)
            self.draw_y += self.oy * (5 - self.i)
            self.alpha = 255
            if self.life < self.max_life / 4:
                self.alpha = int((self.life / self.max_life) * 255)

    def draw(self, surface):
        alpha = 255
        pygame.draw.circle(surface,
                           self.color[self.i] + (alpha,),
                           (self.draw_x, self.draw_y),
                           self.radius, 0)
        if self.i == 0:
            pygame.draw.circle(surface,
                               (0, 0, 0, 0),
                               (self.draw_x + random.randint(-1, 1),
                                self.draw_y - 4),
                               self.radius * (((self.max_life - self.life) / self.max_life) / 0.88), 0)
        else:
            pygame.draw.circle(surface,
                               self.color[self.i - 1] + (alpha,),
                               (self.draw_x + random.randint(-1, 1), self.draw_y - 3),
                               self.radius / 1.5, 0)


class ChestParticle(Particle):
    def __init__(self, game, x, y, chest):
        super().__init__(game, x, y)
        self.color = [(232, 209, 58, 125), (255, 255, 255, 124), (232, 67, 58, 125)]
        self.radius = 4
        self.life = 1
        self.counter = 0
        self.chest = chest
        # self.surface = pygame.Surface((64, 128)).convert_alpha()

    def update(self):
        if random.randint(0, 6) == 5:
            self.x += random.randint(-8, 8)
            self.y += random.randint(-8, -2)
            self.life -= 0.15
        if self.life <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface=None):
        color = random.choice(self.color)
        base_surface = self.chest.room.tile_map.map_surface
        pygame.draw.rect(base_surface, color, (self.x, self.y, 8, 8))


class Bounce:
    def __init__(self, x, y):
        self.speed = random.uniform(0.5, 0.6)  # 0.5
        self.angle = random.randint(-10, 10) / 10  # random.choice([10, -10])
        self.drag = 0.999
        self.elasticity = random.uniform(0.75, 0.9)  # 0.75
        self.gravity = (math.pi, 0.002)
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


class PowerUpParticle(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = [(255, 21, 121)]
        self.radius = 4
        self.life = 20
        self.counter = 0
        self.bounce = Bounce(self.x, self.y)

    def update(self):
        self.life -= 1
        for _ in range(5):
            self.bounce.move()
        self.x = self.bounce.x
        self.y = self.bounce.y
        if self.life <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        color = random.choice(self.color)
        pygame.draw.rect(surface, color, (self.x, self.y, 8, 8))


class PowerUpAttackParticle(PowerUpParticle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = [(255, 21, 121), (255, 111, 204)]


class ShieldParticle(PowerUpParticle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = [(3, 188, 139), (11, 144, 141)]


class DeathAnimation:
    def __init__(self, game, x, y, entity):
        self.game = game
        self.x = x
        self.y = y
        self.images = []
        self.entity = entity
        self.load_images()
        self.counter = -0.5

    def load_images(self):
        for i in range(12):
            self.images.append(pygame.image.load(f'./assets/misc/death/death{i + 1}.png').convert_alpha())
            if self.entity.name == 'boss':
                self.images[-1] = pygame.transform.scale(self.images[-1], (192, 192))

    def update(self):
        self.counter += 0.3
        if self.counter >= 12:
            self.game.particle_manager.particle_list.remove(self)
            if self.entity.name == 'boss':
                position = self.entity.rect.center
                self.entity.room.objects.append(Hole(self.game, position, self.entity.room))

    def draw(self, surface):
        surface.blit(self.images[int(self.counter)], (self.x, self.y))


class StaffParticle(Particle):
    colors = ((151, 218, 63), (140, 218, 63), (160, 218, 63))
    radius = random.randint(7, 8)

    def __init__(self, game, x, y, room):
        super().__init__(game, x, y)
        self.room = room

    def update(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)
        self.radius -= 0.20
        if self.radius <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        color = random.choice(self.colors)
        surface = self.room.tile_map.map_surface
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)


class Dust(Particle):
    def __init__(self, game, player, x, y):
        super().__init__(game, x, y)
        self.player = player
        self.x = x
        self.y = y
        self.color = pygame.Color(173, 173, 172, 0)
        self.life = random.randint(4, 5)
        if random.randint(1, 8) % 4 != 0:
            self.life = 0

    def update(self):
        # if self.player.velocity:
        if self.player.velocity[0] > 0:
            self.x -= random.randint(1, 2) / 4
        elif self.player.velocity[0] < 0:
            self.x += random.randint(1, 2) / 4
        self.y -= random.randint(-2, 3) / 4
        self.life -= 0.5
        if self.life <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        if self.player.velocity:
            rect = (self.x, self.y, 5, 5)
            pygame.draw.rect(surface, self.color, rect)


class ParticleManager:
    def __init__(self, game):
        self.game = game
        self.particle_list = []
        self.fire_particles = []
        # self.surface = self.game.screen
        self.surface = pygame.Surface((utils.world_size[0] // 4, utils.world_size[1] // 4),
                                      pygame.SRCALPHA).convert_alpha()
        self.dest_surf = pygame.Surface((utils.world_size[0], utils.world_size[1])).convert_alpha()

    def update_particles(self):
        if self.particle_list:
            for particle in self.particle_list:
                particle.update()

    def update_fire_particles(self):
        for p in self.fire_particles:
            p.update()

    def draw_fire_particles(self):
        self.surface.fill((0, 0, 0, 0))
        for p in self.fire_particles:
            p.draw(self.surface)
        s = self.game.world_manager.current_map.map_surface
        s.blit(pygame.transform.scale(self.surface, (utils.world_size[0], utils.world_size[1]), self.dest_surf), (0, 0))

    def add_particle(self, particle):
        self.particle_list.append(particle)

    def add_fire_particle(self, particle):
        self.fire_particles.append(particle)

    def draw_particles(self, surface):
        for particle in self.particle_list:
            particle.draw(surface)
