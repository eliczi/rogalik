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
        self.sin = random.randint(-10, 10) / 7
        self.sin_r = random.randint(5, 10)
        self.radius = random.randint(0, 4)
        self.ox = random.randint(-1, 1)
        self.oy = random.randint(-1, 1)
        self.j = random.randint(0, 360)
        self.i = int(((self.life - 1) / self.max_life) * 6)
        self.alpha = None
        self.draw_x = x
        self.draw_y = y
        self.surface = pygame.Surface((64, 64), pygame.SRCALPHA).convert_alpha()
        self.counter = 0
        self.counter2 = 0

    def update(self):

        self.counter = 0
        if self.j > 360:  # Angle
            self.j = 0
        self.life -= 1
        if self.life == 0:
            self.game.particle_manager.particle_list.remove(self)
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

    def draw(self, surface):
        if self.counter2 == 5:
            self.counter2 = 0
            alpha = 255
            self.surface.fill((255, 255, 255, 0))
            pygame.draw.circle(self.surface,
                               self.color[self.i] + (alpha,),
                               (self.draw_x, self.draw_y),
                               self.radius, 0)
            if self.i == 0:
                pygame.draw.circle(self.surface,
                                   (0, 0, 0, 0),
                                   (self.draw_x + random.randint(-1, 1),
                                    self.draw_y - 4),
                                   self.radius * (((self.max_life - self.life) / self.max_life) / 0.88), 0)
            else:
                pygame.draw.circle(self.surface,
                                   self.color[self.i - 1] + (alpha,),
                                   (self.draw_x + random.randint(-1, 1), self.draw_y - 3),
                                   self.radius / 1.5, 0)
        else:
            self.counter2 += 1
        self.game.display.blit(pygame.transform.scale(self.surface, (250, 250)), (0, 0))


class ChestParticle(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = [(232, 209, 58, 125), (255, 255, 255, 124), (232, 67, 58, 125)]
        self.radius = 4
        self.life = 1
        self.counter = 0
        # self.surface = pygame.Surface((64, 128)).convert_alpha()

    def update(self):
        if random.randint(0, 6) == 5:
            self.x += random.randint(-8, 8)
            self.y += random.randint(-8, -2)
            self.life -= 0.15
        if self.life <= 0:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        color = random.choice(self.color)
        pygame.draw.rect(surface, color, (self.x, self.y, 8, 8))
        # pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        # self.surface = pygame.transform.scale(self.surface, (256, 512))
        # self.game.screen.blit(self.surface, (250, 250))


class DeathAnimation:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.images = []
        self.load_images()
        self.counter = -0.5

    def load_images(self):
        for i in range(12):
            self.images.append(pygame.image.load(f'../assets/vfx/death/death{i + 1}.png').convert_alpha())

    def update(self):
        self.counter += 0.4
        if self.counter >= 12:
            self.game.particle_manager.particle_list.remove(self)

    def draw(self, surface):
        surface.blit(self.images[int(self.counter)], (self.x, self.y))


class ParticleManager:
    def __init__(self, game):
        self.game = game
        self.particle_list = []
        self.surface = self.game.screen
        # self.surface = pygame.Surface((utils.world_size[0] // 4, utils.world_size[1] // 4),
        #                               pygame.SRCALPHA).convert_alpha()

    def update_particles(self):
        if self.particle_list:
            for particle in self.particle_list:
                particle.update()

    def add_particle(self, particle):
        self.particle_list.append(particle)

    def draw_particles(self, surface):
        for particle in self.particle_list:
            particle.draw(surface)
