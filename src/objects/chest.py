import pygame
import random

import utils
from particles import ChestParticle
from objects.weapon import AnimeSword
from .object import Object
from .flask import Flask
from .coin import Coin, Emerald


class Chest(Object):
    name = 'chest'
    object_type = 'chest'
    size = (64, 64)

    def __init__(self, game, room):
        self.image = None
        Object.__init__(self, game, self.name, self.object_type, self.size, room)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (21 * 64 / 2, 7.25 * 64)
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.open = False
        self.items = [AnimeSword(game, room), Flask(game, room)]  # items in chest
        self.items[0].chest = self
        self.add_treasure()
        self.interaction = False
        self.counter = 0

    def add_treasure(self):
        for _ in range(random.randint(10, 20)):
            self.items.append(Coin(self.game, self.room, self))
        for _ in range(random.randint(2, 7)):
            self.items.append(Emerald(self.game, self.room, self))

    def load_image(self):
        image = pygame.image.load('../assets/chest/full/chest_full0.png').convert_alpha()
        image = pygame.transform.scale(image, self.size)
        self.image = image

    def chest_particles(self):
        if random.randint(0, 30) == 5 and not self.open:
            position = (self.rect.x + 0.5 * 64, self.rect.y)
            self.game.particle_manager.add_particle(ChestParticle(self.game, *position, self))

    def change_chest_state(self):
        if self.open and self.animation_frame <= 2:
            self.animation_frame += 1 / 20
            self.image = pygame.image.load(
                f'../assets/chest/full/chest_full{int(self.animation_frame)}.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, utils.basic_entity_size)
        elif 2 < self.animation_frame <= 3:
            self.animation_frame += 1 / 20
        elif self.open:
            self.image = pygame.image.load(
                '../assets/chest/empty/chest_empty2.png'
            ).convert_alpha()
            self.image = pygame.transform.scale(self.image, utils.basic_entity_size)
            self.drop_items()  # at the last frame of animation, drop items

    def update(self):
        self.chest_collision()
        self.chest_particles()
        self.change_chest_state()

    def draw(self):
        self.room.tile_map.map_surface.blit(self.image, self.rect)

    def detect_collision(self):
        if self.game.player.hitbox.colliderect(self.rect):
            self.image = pygame.image.load('../assets/chest/full/chest_picked.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (64, 64))
            self.interaction = True
        else:
            self.image = pygame.image.load('../assets/chest/full/chest_full0.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, utils.basic_entity_size)

    def chest_collision(self):
        test_rect = self.game.player.hitbox.move(*self.game.player.velocity)
        collide_points = (test_rect.midbottom, test_rect.bottomleft, test_rect.bottomright)
        if any(self.hitbox.collidepoint(point) for point in collide_points):
            self.game.player.velocity = [0, 0]

    def interact(self):
        self.open = True
        self.interaction = False
        # self.drop_items()

    def drop_items(self):
        for item in self.items:
            item.rect.midtop = self.rect.topleft
            item.dropped = True
            item.activate_bounce()
            item.bounce.x = self.hitbox.midtop[0]
            item.bounce.y = self.hitbox.midtop[1]
            self.room.objects.append(item)
            self.items.remove(item)

    def __repr__(self):
        return f'Chest in room {self.room}'
