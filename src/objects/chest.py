import pygame
import random

import utils
from particles import ChestParticle
from objects.weapon import Weapon
from .object import Object
from .flask import Flask


class Chest(Object):
    name = 'chest'
    object_type = 'chest'
    size = (64, 64)

    def __init__(self, game, room):
        self.image = None
        Object.__init__(self, game, self.name, self.object_type, self.size, room)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (17 * 64 / 2, 6 * 64)
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.surface = self.room.tile_map.map_surface
        self.open = False
        self.items = [Flask(game, room)]  # items in chest
        self.interaction = True
        self.counter = 0

    def load_image(self):
        image = pygame.image.load('../assets/chest/full/chest_full0.png').convert_alpha()
        image = pygame.transform.scale(image, self.size)
        self.image = image

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
