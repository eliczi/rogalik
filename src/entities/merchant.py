import pygame
import random
from utils import get_mask_rect
from objects.object import ShowName
from objects.weapon import AnimeSword
from objects.power_up import ShieldPowerUp


class Merchant:
    name = 'merchant'
    size = (96, 96)

    def __init__(self, game, room):
        self.game = game
        self.room = room
        self.image = None
        self.images = []
        self.load_images()
        self.rect = self.image.get_rect(center=(550, 400))
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.items_position = [(650, 350), (750, 350), (850, 350)]
        self.items = []
        self.add_items()
        self.text = 'Oy Vey!'
        self.dialog = ShowName(self)
        self.dialog.text = self.text.replace("_", " ").title()
        self.dialog.text_length = len(self.text)
        self.interaction = False

    def load_images(self):
        for i in range(4):
            image = pygame.image.load(f'../assets/{self.name}/{self.name}{i}.png').convert_alpha()
            image = pygame.transform.scale(image, self.size)
            self.images.append(image)
        self.image = self.images[0]

    def add_items(self):
        self.items.append(AnimeSword(self.game, self.room, self.items_position[0]))
        self.items.append(ShieldPowerUp(self.game, self.room, self.items_position[1]))
        self.items[-1].owner = self
        self.items[-2].owner = self

    def update_animation_frame(self):
        self.animation_frame += 1.5 / 15
        if self.animation_frame > 3:
            self.animation_frame = 0
        self.image = self.images[int(self.animation_frame)]

    def update(self):
        self.update_animation_frame()
        self.detect_collision()

    def detect_collision(self):
        if self.game.player.hitbox.colliderect(self.hitbox):
            self.game.player.gold -= 1
            self.interaction = True
        else:
            self.interaction = False
            self.dialog.reset_line_length()

    def manage_items(self):
        for item in self.items:
            item.draw()
            item.update()
            item.detect_collision()

    def draw(self):
        # self.draw_shadow(self.room.tile_map.map_surface)
        self.manage_items()
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        if self.interaction:
            self.dialog.draw(self.room.tile_map.map_surface, self.rect)
