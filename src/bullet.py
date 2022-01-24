import math
import pygame
import random

from particles import EnemyHitParticle, WallHitParticle


class BulletManager:
    def __init__(self):
        pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self, master, game, x, y, target, entity='normal', rotation=None):
        super().__init__()
        self.game = game
        self.bullet_size = 7
        self.image = pygame.Surface([self.bullet_size, self.bullet_size])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        if entity == 'boss':
            self.speed = 7
        self.damage = 10
        self.pos = (x, y)
        target_x, target_y = target
        self.dir = pygame.math.Vector2(target_x - x, target_y - y)
        self.angle = rotation
        if self.angle:
            self.dir.rotate_ip(self.angle)
        length = math.hypot(*self.dir)
        self.dir = (self.dir[0] / length, self.dir[1] / length)
        self.entity = entity
        self.bounce_back = True

        self.vector = None

    def update(self):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.wall_collision()
        if self.bounce_back is False:
            for enemy in self.game.enemy_manager.enemy_list:
                if self.rect.colliderect(enemy.hitbox):
                    enemy.hp -= self.damage
                    self.game.particle_manager.particle_list.append(
                        EnemyHitParticle(self.game, self.rect.x, self.rect.y))
                    self.kill()
        self.player_collision(self.game.player)
        self.bounce()
        if self.rect.y < 0 or self.rect.y > 1000:
            self.kill()

    def draw(self, surface):
        radius = 5
        # self.sparkle()
        pygame.draw.circle(surface, (255, 255, 255), (self.rect.x + radius / 2, self.rect.y + radius / 2),
                           radius)
        pygame.draw.circle(surface, (58, 189, 74), (self.rect.x + radius / 2, self.rect.y + radius / 2),
                           radius - 1)

    def wall_collision(self):
        collide_points = (self.rect.midbottom, self.rect.bottomleft, self.rect.bottomright)
        for wall in self.game.world_manager.current_map.wall_list:
            if any(wall.hitbox.collidepoint(point) for point in collide_points):
                self.game.particle_manager.particle_list.append(WallHitParticle(self.game, self.rect.x, self.rect.y))
                self.kill()

    def player_collision(self, collision_enemy):
        if self.rect.colliderect(collision_enemy.hitbox):
            self.game.player.hp -= self.damage
            self.game.player.hurt = True
            self.game.player.time = pygame.time.get_ticks()
            self.sparkle()
            self.kill()

    def sparkle(self):
        for _ in range(random.randint(2, 4)):
            self.game.particle_manager.particle_list.append(EnemyHitParticle(self.game, self.rect.x, self.rect.y))

    def bounce(self):
        if (
                self.game.player.weapon
                and self.game.player.attacking
                and pygame.sprite.collide_mask(self.game.player.weapon, self)
                and self.bounce_back
        ):
            self.dir = (-self.dir[0] + random.randint(-20, 10) / 100, -self.dir[1] + random.randint(-10, 10) / 100)
            self.speed *= random.randint(10, 20) / 10
            self.bounce_back = False
