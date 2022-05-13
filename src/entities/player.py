import pygame
from math import sqrt
from src.objects.p import Poop
from src.objects.flask import GreenFlask
from .entity import Entity
from src.particles import Dust


class Player(Entity):
    name = 'player'
    speed = 360
    max_hp = 100
    gold = 0
    shield = 1
    strength = 1
    hp = max_hp
    items = []

    def __init__(self, game):
        Entity.__init__(self, game, self.name)
        self.rect = self.image.get_rect(center=(512 + 2.5 * 64, 600))
        self.weapon = None
        self.attacking = False
        self.interaction = True
        self.attack_cooldown = 350  # ms
        self.room = None
        self.death_counter = 1
        self.falling = False
        self.floor_value = self.rect.y
        self.fall(-100)

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
        if pressed[pygame.K_TAB]:
            self.game.mini_map.draw_all(self.game.screen)
            self.game.mini_map.draw_mini_map = False
        else:
            self.game.mini_map.draw_mini_map = True
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.items:
                if event.button == 4:
                    self.weapon = self.items[self.items.index(self.weapon) - 1]
                    self.shift_items_left()
                    self.weapon = self.items[0]
                elif event.button == 5:
                    self.weapon = self.items[(self.items.index(self.weapon) + 1) % len(self.items)]
                    self.shift_items_right()
                    self.weapon = self.items[0]

        # constant_dt = 0.06
        constant_dt = self.game.dt
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

        if pygame.mouse.get_pressed()[0] and pygame.time.get_ticks() - self.time > self.attack_cooldown \
                and self.weapon:
            self.time = pygame.time.get_ticks()
            self.attacking = True
            if self.weapon.name != 'staff':
                self.weapon.weapon_swing.swing_side *= (-1)

    def shift_items_right(self):
        self.items = [self.items[-1]] + self.items[:-1]

    def shift_items_left(self):
        self.items = self.items[1:] + [self.items[0]]

    def falling_update(self):
        if self.rect.y < self.floor_value:
            value = 15
            self.rect.y += value
        else:
            self.falling = False
            self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Hit.wav'))

    def add_walking_particles(self):
        if self.moving():
            self.game.sound_manager.play_walk_sound()
            self.game.particle_manager.add_particle(Dust(self.game, self, *self.rect.midbottom))

    def update(self) -> None:
        if self.falling:
            self.falling_update()
        else:
            self.add_walking_particles()
            if self.death_counter == 0:
                return
            self.entity_animation.update()
            self.wall_collision()
            if self.can_move:
                self.rect.move_ip(*self.velocity)
                self.hitbox.move_ip(*self.velocity)
            self.detect_death()
        if self.weapon:
            self.weapon.update()
        self.update_hitbox()

    def fall(self, value):
        self.rect.y = value
        self.falling = True

    def calculate_collision(self, enemy):
        if not self.shield and not self.dead:
            self.hp -= enemy.damage
            self.game.sound_manager.play(self.game.sound_manager.player_hurt)
            if not self.dead:
                self.hurt = True
            self.entity_animation.hurt_timer = pygame.time.get_ticks()
        if self.shield:
            self.shield -= 1
            self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Random1.wav'))

    def draw(self, surface):
        if self.death_counter == 0:
            return
        self.draw_shadow(surface)
        surface.blit(self.image, self.rect)
        if self.weapon:
            self.weapon.draw()
