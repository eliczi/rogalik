import pygame
import random
from src.utils import get_mask_rect
from src.objects.object import ShowName
from src.objects.weapon import AnimeSword, FireSword, Staff
from src.objects.power_up import ShieldPowerUp, AttackPowerUp
from src.objects.flask import GreenFlask, RedFlask
import numpy
from src.entities.entity import Entity

class Merchant(Entity):
    name = 'merchant'
    size = (96, 96)
    hp = 10000

    def __init__(self, game, room):
        super().__init__(game, self.name)
        self.room = room
        self.image = None
        self.images = []
        self.load_images()
        self.rect = self.image.get_rect(center=(550, 400))
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.items_position = [(670, 400), (770, 400), (870, 400)]
        self.items = []
        self.add_items()
        self.texts = ['Hello there', 'How you doin?', 'I\'m a merchant orc']
        self.dialog = ShowName(self)
        self.dialog.text_length = len(self.dialog.text)
        self.interaction = False
        for item in self.items:
            self.room.objects.append(item)
        self.room.tile_map.wall_list.append(self)
        self.dead = False
        self.player_bought = False

    def load_images(self):
        for i in range(4):
            image = pygame.image.load(f'./assets/characters/{self.name}/idle/idle{i}.png').convert_alpha()
            image = pygame.transform.scale(image, self.size)
            self.images.append(image)
        self.image = self.images[0]

    def add_items(self):
        items = [AnimeSword(self.game, self.room), RedFlask(self.game, self.room),
                 ShieldPowerUp(self.game, self.room), AttackPowerUp(self.game, self.room),
                 GreenFlask(self.game, self.room), FireSword(self.game, self.room),
                 Staff(self.game, self.room)]
        items = numpy.random.choice(items, size=2, replace=False, p=[0.03, 0.01, 0.2, 0.2, 0.5, 0.03, 0.03])
        for it in items:
            self.items.append(it)
        self.items[-1].rect.center = self.items_position[1]
        self.items[-2].rect.center = self.items_position[0]
        self.items[-1].for_sale = True
        self.items[-2].for_sale = True
        self.items[-1].show_price.__init__(self.items[-1])
        self.items[-2].show_price.__init__(self.items[-2])
        self.items[-2].show_price.set_text_position((650 + 15, 350 + 126))
        self.items[-1].show_price.set_text_position((750 + 15, 350 + 126))

    def update_animation_frame(self):
        self.animation_frame += 1.5 / 15
        if self.animation_frame > 4:
            self.animation_frame = 0
        self.image = self.images[int(self.animation_frame)]

    def update(self):
        self.update_animation_frame()
        self.detect_collision()
        if self.interaction:
            self.dialog.draw(self.room.tile_map.map_surface, self.rect)
        else:
            self.dialog.text = random.choice(self.texts)
            self.dialog.text_length = len(self.dialog.text)
            self.dialog.reset_line_length()

    def detect_collision(self):
        self.interaction = bool(self.game.player.hitbox.colliderect(self.hitbox))


    def draw(self):
        # self.draw_shadow(self.room.tile_map.map_surface)
        self.draw_shadow(self.room.tile_map.map_surface, 100, (0,0,40, 14), -15 + self.animation_frame,3)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
