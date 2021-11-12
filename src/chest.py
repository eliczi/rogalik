import pygame
import random

import utils
from particles import ChestParticle


class Chest:
    def __init__(self, game, room):
        self.game = game
        self.room = room
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (17 * 64 / 2, 6 * 64)
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.surface = self.room.tile_map.map_surface
        self.open = False
        self.items = []  # items in chest

    @staticmethod
    def load_image():
        image = pygame.image.load(
            '../assets/chest/full/chest_full0.png'
        ).convert_alpha()

        image = pygame.transform.scale(image, utils.basic_entity_size)
        return image

    def chest_particles(self):
        if random.randint(0, 30) == 5 and not self.open:
            position = ((self.rect.midtop[0]) // 4 + random.randint(30, 34), (self.rect.midtop[1]) // 4 + 15)
            self.game.particle_manager.add_particle(ChestParticle(self.game, *position))

    def update(self):
        self.chest_particles()
        if self.open and self.animation_frame <= 2:
            self.animation_frame += 1 / 20
            self.image = pygame.image.load(
                f'../assets/chest/full/chest_full{int(self.animation_frame)}.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, utils.basic_entity_size)

    def draw(self):
        self.surface.blit(self.image, self.rect)
        # pygame.draw.rect(self.surface, (255, 123, 234), self.rect, 2)

    def detect_collision(self, player):
        self.game.can_open_chest = bool(player.hitbox.colliderect(self.rect))

    def open_chest(self):
        self.open = True

    def __repr__(self):
        return f'Chest in room {self.room}'
