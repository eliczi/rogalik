import pygame
import random

import utils
from particles import ChestParticle
from objects.weapon import Weapon
from .flask import Flask


class Chest:
    def __init__(self, game, room):
        self.name = 'chest'
        self.game = game
        self.room = room
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (17 * 64 / 2, 6 * 64)
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.surface = self.room.tile_map.map_surface
        self.open = False
        self.items = [Flask(game, 'green_flask', (48, 48), room)]  # items in chest
        self.interaction = True
        self.counter = 0

    @staticmethod
    def load_image():
        image = pygame.image.load(
            '../assets/chest/full/chest_full0.png'
            # '../../assets/chest/full/chest_full0.png'
        ).convert_alpha()

        image = pygame.transform.scale(image, utils.basic_entity_size)
        return image

    def chest_particles(self):
        if random.randint(0, 30) == 5 and not self.open:
            position = (self.rect.x + 2.5 * 64, self.rect.y + 64)
            self.game.particle_manager.add_particle(ChestParticle(self.game, *position))

    def update(self):
        self.chest_particles()
        if self.open and self.animation_frame <= 2:
            self.animation_frame += 1 / 20
            self.image = pygame.image.load(
                f'../assets/chest/full/chest_full{int(self.animation_frame)}.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, utils.basic_entity_size)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # self.surface.blit(self.image, self.rect)

    def detect_collision(self, player):
        self.game.can_open_chest = bool(player.rect.colliderect(self.rect))
        if player.rect.colliderect(self.rect) and self.interaction:
            self.image = pygame.image.load('../assets/chest/full/chest_picked.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (64, 64))
        elif self.interaction:
            self.image = pygame.image.load(f'../assets/chest/full/chest_full0.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, utils.basic_entity_size)

    def interact(self):
        self.open = True
        self.interaction = False
        self.drop_items()

    def drop_items(self):
        self.items[0].rect.midtop = self.rect.topleft
        self.items[0].dropped = True
        self.items[0].bounce.x = self.rect.x
        self.items[0].bounce.y = self.rect.y

        self.room.objects.append(self.items[0])
        self.items.pop()

    def __repr__(self):
        return f'Chest in room {self.room}'
