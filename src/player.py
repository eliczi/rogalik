import pygame
import os

from weapon import Weapon
from utils import get_mask_rect
import utils
from math import sqrt
from animation import load_animation_sprites


# import numpy as np
# Zoom note: transform.scale self.image and self.animation_database images to self.image_size * game.zoom_factor
class Player():
    def __init__(self, game):
        self.game = game

        self.animation_database = load_animation_sprites('../assets/player/')
        self.image = pygame.image.load("../assets/player/idle/idle0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, utils.basic_entity_size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(
            center=(500, 400))  # (center=self.game.screen.get_rect().center)  # mask -> image
        self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)  # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        self.speed = 75
        self.direction = ''
        self.player_moving = False
        self.player_index = 0  # frames
        self.attacking = False
        self.weapon = Weapon(self.game, 10, 'sword')  # deleted groups z self.game
        self.attacked = False
        self.gun_length = 15
        self.gun_width = 5
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

    def moving(self) -> bool:
        if sum(self.velocity):
            return True

    def animation(self):

        if self.moving():
            self.player_index += 1.0 / 15  # change factor of
            if self.player_index >= 4:  # 4 frames per movement
                self.player_index = 0
            if self.direction == 'LEFT':
                self.image = self.animation_database["WALK"][int(self.player_index)]
            elif self.direction == 'UP':
                self.image = self.animation_database["WALK"][int(self.player_index)]
            elif self.direction == "RIGHT":
                self.image = pygame.transform.flip(self.animation_database["WALK"][int(self.player_index)], True,
                                                   False)
            elif self.direction == "DOWN":
                self.image = self.animation_database["WALK"][int(self.player_index)]
        else:  # if idle
            self.player_index += 1.0 / 15
            if self.player_index >= 4:
                self.player_index = 0
            if self.direction == 'LEFT':
                self.image = self.animation_database["IDLE"][int(self.player_index)]
            elif self.direction == 'RIGHT':
                self.image = self.animation_database["IDLE"][int(self.player_index)]
            elif self.direction == "UP":
                self.image = self.animation_database["IDLE"][int(self.player_index)]
            elif self.direction == "DOWN":
                self.image = self.animation_database["IDLE"][int(self.player_index)]

    def set_velocity(self, velocity):
        self.velocity = velocity

    def player_size(self):
        image_size = tuple(int(self.game.zoom_level * x) for x in utils.basic_entity_size)
        self.image = pygame.transform.scale(self.image, image_size)

    def wall_collision(self):
        """Sets player's velocity to zero if it would collide with walls
           In other words, prevents player from colliding with walls"""

        test_rect = self.hitbox.move(*self.velocity)  # Position after moving, change name later
        collide_points = (test_rect.midbottom, test_rect.bottomleft, test_rect.bottomright)
        for wall in self.game.room_image.wall_list:
            for collide_point in collide_points:
                if wall.rect.collidepoint(collide_point):
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

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.weapon.draw(screen)
        # pygame.draw.rect(self.game.room_image.map_surface, (0, 255, 0), self.rect, 1)
        # pygame.draw.rect(self.game.room_image.map_surface, (255, 0, 0), self.hitbox, 1)

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
