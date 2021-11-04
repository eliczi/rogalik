import pygame
import os

import utils
from weapon import Weapon
from utils import get_mask_rect
from Entity import Entity
from math import sqrt


# import numpy as np
# Zoom note: transform.scale self.image and self.animation_database images to self.image_size * game.zoom_factor

class Player():
    def __init__(self, game):
        self.game = game
        self.animation_database = {"IDLE_LEFT": [],
                                   "IDLE_RIGHT": [],
                                   "WALK_LEFT": [],
                                   "WALK_RIGHT": []}

        self.image_size = (64, 64)
        self.image = pygame.image.load("../assets/player/idle/right_idle0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, self.image_size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center = (500, 400))#(center=self.game.screen.get_rect().center)  # mask -> image
        self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)  # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        self.old_velocity = [0, 0]
        self.speed = 100
        self.direction = ''
        self.player_moving = False
        self.player_index = 0  # animation frames
        # Player Attacking
        self.attacking = False
        self.hasWeapon = True
        self.weapon = Weapon(self.game, 10, 'sword')  # usuniete groups z self.game
        self.hp = 100
        self.max_stamina = 1000
        self.current_stamina = self.max_stamina
        self.attacked = False
        ########GUN PROPERTIES,########
        self.gun_length = 15
        self.gun_width = 5
        # Animation loading
        self.load_animation('../assets/player/')
        # hitbox
        self.hitbox = self.rect_mask
        self.can_move = True

    def input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.direction = 'UP'
        if pressed[pygame.K_s]:
            self.direction = 'DOWN'
        if pressed[pygame.K_a]:
            self.direction = 'LEFT'
        if pressed[pygame.K_d]:
            self.direction = 'RIGHT'

        constant_dt = 0.06
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

        if pygame.mouse.get_pressed()[0] and self.game.counter > 30:
            self.attacking = True
            self.attacked = False
            self.weapon.swing_side *= (-1)  # self.player.weapon.swing_side * (-1) + 1
            self.game.counter = 0

    def load_animation(self, path):
        """Loads animation frames to dictionary"""

        # Lists all the subdirectories in specified path
        animation_states = os.listdir(path)
        for state in animation_states:
            substates = os.listdir(path + state)
            for ss in substates:
                image_loc = ss
                elements = image_loc.split('_')
                key = state.upper() + '_' + elements[0].upper()  # key to dictionary
                animation_image = pygame.image.load(path + state + '/' + image_loc).convert()
                animation_image = pygame.transform.scale(animation_image, self.image_size)
                self.animation_database[key].append(animation_image)

    def moving(self) -> bool:

        if self.velocity[0] != 0 or self.velocity[1] != 0:
            return True
        else:
            return False

    def animation(self):

        if self.moving():
            self.player_index += 1.0 / 15  # change factor of animation
            if self.player_index >= 4:  # 4 frames per movement
                self.player_index = 0
            if self.direction == 'LEFT':
                self.image = self.animation_database["WALK_LEFT"][int(self.player_index)]
            elif self.direction == 'UP':
                self.image = self.animation_database["WALK_RIGHT"][int(self.player_index)]
            elif self.direction == "RIGHT":
                self.image = pygame.transform.flip(self.animation_database["WALK_LEFT"][int(self.player_index)], True,
                                                   False)
            elif self.direction == "DOWN":
                self.image = self.animation_database["WALK_RIGHT"][int(self.player_index)]
        else:  # if idle
            self.player_index += 1.0 / 15
            if self.player_index >= 4:
                self.player_index = 0
            if self.direction == 'LEFT':
                self.image = self.animation_database["IDLE_LEFT"][int(self.player_index)]
            elif self.direction == 'RIGHT':
                self.image = self.animation_database["IDLE_RIGHT"][int(self.player_index)]
            elif self.direction == "UP":
                self.image = self.animation_database["IDLE_RIGHT"][int(self.player_index)]
            elif self.direction == "DOWN":
                self.image = self.animation_database["IDLE_RIGHT"][int(self.player_index)]

    def weapon_attack(self, enemy):
        pass

    def calculate_collison(self, collision_obj, damage):

        if collision_obj.hp > 0:
            collision_obj.hp -= damage
            collision_obj.hurt = True  # indicating that enemy is hurt
            if collision_obj.hp <= 0:
                self.score += 1
        self.attacked = True

    def set_velocity(self, velocity):
        self.old_velocity = self.velocity
        self.velocity = velocity

    def player_size(self):
        self.image_size = (64, 64)
        self.image_size = tuple(int(self.game.zoom_level * x) for x in self.image_size)
        self.image = pygame.transform.scale(self.image, self.image_size)

    def wall_collision(self):
        """Sets player's velocity to zero if it would collide with walls
           In other words, prevents player to collide with walls"""
        for wall in self.game.map.wall_list:
            test_rect = self.hitbox.move(*self.velocity)
            if wall.rect.collidepoint(test_rect.midbottom) or wall.rect.collidepoint(
                    test_rect.bottomleft) or wall.rect.collidepoint(test_rect.bottomright):
                self.velocity = [0, 0]

    def update(self) -> None:
        self.weapon.update()
        self.animation()
        self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        self.wall_collision()
        if self.can_move:
            self.rect.move_ip(*self.velocity)
            self.rect_mask.move_ip(*self.velocity)

        self.hitbox = self.rect_mask
        self.hitbox.midbottom = self.rect.midbottom

        pygame.draw.rect(self.game.screen, (0, 255, 0), self.rect, 1)
        pygame.draw.rect(self.game.screen, (255, 0, 0), self.hitbox, 1)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.weapon.draw(screen)

    def render(self):  # Render weapon
        pass
        # start = pygame.math.Vector2(self.rect.midright)
        # mouse = pygame.mouse.get_pos()
        # end = start + (mouse - start).normalize() * self.gun_length

        # pygame.draw.lines(self.game.screen, (255, 255, 255), False, (start, end), width=self.gun_width)

    def gun_point(self):

        start = pygame.math.Vector2(self.rect.midright)
        mouse = pygame.mouse.get_pos()
        end = start + (mouse - start).normalize() * self.gun_length
        return end

    def assign_weapon(self, weapon: Weapon):

        self.weapon = weapon
        self.hasWeapon = True
