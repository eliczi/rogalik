import pygame
from math import sqrt
import random
from objects.weapon import Weapon
from .entity import Entity
from .animation import load_animation_sprites
from utils import get_mask_rect
from particles import DeathAnimation
import utils


class Dust:
    def __init__(self, player, x, y):
        self.player = player
        self.x = x
        self.y = y
        self.color = pygame.Color(173, 173, 172, 0)
        self.life = random.randint(4, 5)

    def update(self):
        if self.player.velocity:
            if self.player.velocity[0] > 0:
                self.x -= random.randint(1, 2) / 4
            elif self.player.velocity[0] < 0:
                self.x += random.randint(1, 2) / 4
            self.y -= random.randint(-2, 3) / 4
            self.life -= 0.5
            if self.life < 0:
                self.player.walking_particles.remove(self)

    def draw(self):
        if self.player.velocity:
            rect = (self.x, self.y, 5, 5)
            pygame.draw.rect(self.player.game.screen, self.color, rect)


class Player(Entity):
    def __init__(self, game):
        Entity.__init__(self, game, 'player')
        self.rect = self.image.get_rect(center=(512, 400))
        self.speed = 100
        self.max_hp = 60
        self.hp = self.max_hp
        self.weapon = None
        self.attacking = False
        self.items = []
        self.interaction = True
        self.gold = 0
        self.walking_particles = []
        self.size = 64
        self.shield = 2
        self.strength = 1
        self.step = pygame.mixer.Sound('../assets/sound/footsteps.wav')
        self.attack_cooldown = 400
        self.death_counter = 1
        self.dupa = False

    def input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.direction = 'up'
        if pressed[pygame.K_s]:
            self.direction = 'down'
        if pressed[pygame.K_a]:
            self.direction = 'left'
        if pressed[pygame.K_d]:
            self.direction = 'right'
        if pressed[pygame.K_e] and pygame.time.get_ticks() - self.time > 300:
            self.time = pygame.time.get_ticks()
            self.game.object_manager.interact()
        if pressed[pygame.K_q] and self.weapon and pygame.time.get_ticks() - self.time > 300:
            self.time = pygame.time.get_ticks()
            self.weapon.drop()
            if self.items:
                self.weapon = self.items[0]

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.items:
                if event.button == 4:
                    # self.weapon = self.items[self.items.index(self.weapon) - 1]
                    self.shift_items_left()
                    self.weapon = self.items[0]
                elif event.button == 5:
                    # self.weapon = self.items[(self.items.index(self.weapon) + 1) % len(self.items)]
                    self.shift_items_right()
                    self.weapon = self.items[0]

        constant_dt = 0.06
        #constant_dt = self.game.dt
        vel_up = [0, -self.speed * constant_dt]
        vel_up = [i * pressed[pygame.K_w] for i in vel_up]
        vel_down = [0, self.speed * constant_dt]
        vel_down = [i * pressed[pygame.K_s] for i in vel_down]
        vel_left = [-self.speed * constant_dt, 0]
        vel_left = [i * pressed[pygame.K_a] for i in vel_left]
        vel_right = [self.speed * constant_dt, 0]
        vel_right = [i * pressed[pygame.K_d] for i in vel_right]
        vel = zip(vel_up, vel_down, vel_left, vel_right)
        vel_list = [sum(item) for item in vel]

        x = sqrt(pow(vel_list[0], 2) + pow(vel_list[1], 2))

        if 0 not in vel_list:
            z = x / (abs(vel_list[0]) + abs(vel_list[1]))
            vel_list_fixed = [item * z for item in vel_list]
            self.set_velocity(vel_list_fixed)
        else:
            self.set_velocity(vel_list)
        if pygame.mouse.get_pressed()[
            0] and pygame.time.get_ticks() - self.time > self.attack_cooldown and self.weapon:  # player attacking
            self.time = pygame.time.get_ticks()
            self.attacking = True
            self.weapon.weapon_swing.swing_side *= (-1)

    def shift_items_right(self):
        self.items = [self.items[-1]] + self.items[:-1]

    def shift_items_left(self):
        self.items = self.items[1:] + [self.items[0]]

    def detect_death(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.entity_animation.animation_frame = 0
            self.dupa = True
            self.can_move = False

        if self.death_counter == 0 and self.dupa:
            position = (self.rect.x, self.rect.y)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position))
            self.dupa = False

    def update(self) -> None:
        if self.death_counter == 0:
            return
        if self.weapon:
            self.weapon.update()
        self.entity_animation.update()
        self.wall_collision()
        if self.can_move:
            self.rect.move_ip(*self.velocity)
            self.hitbox.move_ip(*self.velocity)
        self.update_hitbox()
        self.detect_death()

    def calculate_collision(self, enemy):
        if not self.shield:
            self.hp -= enemy.damage
            if not self.dead:
                self.hurt = True
            self.entity_animation.hurt_timer = pygame.time.get_ticks()
        if self.shield:
            self.shield -= 1

    def draw(self, surface):
        if self.death_counter == 0:
            return
        if (self.velocity[0] != 0 or self.velocity[1] != 0) and random.randint(1, 8) % 4 == 0:
            self.walking_particles.append(Dust(self, *self.rect.midbottom))
        for p in self.walking_particles:
            p.update()
            p.draw()
        self.draw_shadow(surface)
        surface.blit(self.image, self.rect)
        if self.weapon:
            self.weapon.draw()
