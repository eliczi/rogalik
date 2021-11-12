import pygame
import random
from math import sin

import utils


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
            self.game.particles.remove(self)

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
            self.game.particles.remove(self)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)


class Fire(Particle):
    """Besides some calculations and magic variables, there is a bsurf Surface in game class, which serves as screen
    to display fire plarticles, it is 4x times smaller than default window, but during blitting, it is resized to
    window size, as to achieve pixelated fire)"""

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = ((255, 255, 0),
                      (255, 173, 51),
                      (247, 117, 33),
                      (191, 74, 46),
                      (115, 61, 56),
                      (61, 38, 48))
        self.max_life = random.randint(13, 27)
        self.life = self.max_life
        self.sin = random.randint(-10, 10) / 7  # ???? XD
        self.sin_r = random.randint(5, 10)
        self.radius = random.randint(0, 2)

        self.ox = random.randint(-1, 1)
        self.oy = random.randint(-1, 1)
        self.j = random.randint(0, 360)
        self.i = int(((self.life - 1) / self.max_life) * 6)
        self.alpha = None
        self.draw_x = x
        self.draw_y = y
        self.counter = 0

    def update(self):
        if self.counter == 4:
            self.counter = 0
            if self.j > 360:  # Angle
                self.j = 0

            self.life -= 1
            if self.life == 0:
                self.game.particles.remove(self)

            self.i = int((self.life / self.max_life) * 6)

            self.y -= 0.7  # rise
            self.x += ((self.sin * sin(self.j / self.sin_r)) / 20)  # spread

            if not random.randint(0, 5):
                self.radius += 0.2  # circle radius, set to 10 for big bang

            self.draw_x, self.draw_y = self.x, self.y

            self.draw_x += self.ox * (5 - self.i)
            self.draw_y += self.oy * (5 - self.i)

            self.alpha = 255
            if self.life < self.max_life / 4:
                self.alpha = int((self.life / self.max_life) * 255)
        else:
            self.counter += 1

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


class DeathParticle(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = (192, 192, 192)
        self.radius = random.randint(5, 7)
        self.life = random.randint(30, 50)
        self.counter = 0  # to slow down animation speed

    def update(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)
        self.radius += 0.05
        self.life -= 1
        if self.life <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (0, 0, 0, 0),
                           (self.x + random.randint(-1, 1), self.y + random.randint(-1, 1)), self.radius)


class ChestParticle(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = [(232, 209, 58, 125), (255, 255, 255, 124), (232, 67, 58, 125)]
        self.radius = 1
        self.life = 1
        self.counter = 0

    def update(self):
        if random.randint(0, 6) == 5:
            self.x += random.randint(-2, 2)
            self.y += random.randint(-2, -1)
            self.life -= 0.15
        if self.life <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        color = random.choice(self.color)
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)


class ParticleManager:
    def __init__(self, game):
        self.game = game
        self.particle_list = []
        self.surface = pygame.Surface((utils.world_size[0] // 4, utils.world_size[1] // 4),
                                      pygame.SRCALPHA).convert_alpha()

    def update_particles(self):
        if self.particle_list:
            for particle in self.particle_list:
                particle.update()
            self.draw_particles()

    def add_particle(self, particle):
        self.particle_list.append(particle)

    def draw_particles(self):
        self.surface.fill((0, 0, 0, 0))
        for particle in self.particle_list:
            particle.draw(self.surface)
        #self.game.screen.blit(pygame.transform.scale(self.surface, utils.world_size), (0, 0))
