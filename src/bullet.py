import pygame
import math
import random
from particles import EnemyHitParticle, WallHitParticle


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.bullet_size = 7
        self.image = pygame.Surface([self.bullet_size, self.bullet_size])
        self.image.fill(self.game.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.damage = 10 + self.game.player.score * 5

        self.pos = (x, y)

        mx, my = pygame.mouse.get_pos()
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        self.dir = (self.dir[0] / length, self.dir[1] / length)

    def update(self):
        """

        :return:
        :rtype:
        """
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]


    def draw(self):
        """

        :return:
        :rtype:
        """
        radius = 5
        #self.sparkle()
        pygame.draw.circle(self.game.screen, self.game.GREEN, (self.rect.x + radius / 2, self.rect.y + radius / 2),
                           radius)
        pygame.draw.circle(self.game.screen, (242, 255, 50), (self.rect.x + radius / 2, self.rect.y + radius / 2),
                           radius - 1)

    def collision(self, collision_obj):
        """

        :param collision_obj:
        :type collision_obj:
        :return:
        :rtype:
        """
        if self.rect.colliderect(collision_obj.rect):
            self.game.particles.append(WallHitParticle(self.game, self.rect.x, self.rect.y))
            self.kill()

    def collision_enemy(self, collision_enemy):
        """

        :param collision_enemy:
        :type collision_enemy:
        :return:
        :rtype:
        """
        if self.rect.colliderect(collision_enemy.rect_mask):  # rect->rect_mask
            self.game.player.calculate_collision(collision_enemy, self.damage)
            self.sparkle()
            self.kill()

    def sparkle(self):
        """

        :return:
        :rtype:
        """
        for _ in range(random.randint(2, 4)):
            self.game.particles.append(EnemyHitParticle(self.game, self.rect.x, self.rect.y))
