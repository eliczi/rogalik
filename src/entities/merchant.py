import pygame
import random
from utils import get_mask_rect
from objects.object import ShowName
from objects.weapon import AnimeSword, FireSword, Staff
from objects.power_up import ShieldPowerUp, AttackPowerUp
from objects.flask import GreenFlask, RedFlask


class Merchant:
    name = 'merchant'
    size = (96, 96)
    hp = 10000

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
        self.texts = ['Hello there', 'How you doin?', 'I\'m a merchant orc', 'My green ass has all the coins!']
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
            image = pygame.image.load(f'../assets/characters/{self.name}/{self.name}{i}.png').convert_alpha()
            image = pygame.transform.scale(image, self.size)
            self.images.append(image)
        self.image = self.images[0]

    def add_items(self):
        items = []
        self.items.append(RedFlask(self.game, self.room, self.items_position[0]))
        self.items.append(ShieldPowerUp(self.game, self.room, self.items_position[1]))
        self.items[-1].for_sale = True
        self.items[-2].for_sale = True
        self.items[-2].show_price.__init__(self.items[-2])
        self.items[-1].show_price.__init__(self.items[-1])
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
        elif self.player_bought and not self.interaction:
            self.dialog.text = 'Thank you!'
        else:
            self.dialog.text = random.choice(self.texts)
            self.dialog.text_length = len(self.dialog.text)
            self.dialog.reset_line_length()

    def detect_collision(self):
        self.interaction = bool(self.game.player.hitbox.colliderect(self.hitbox))

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((100, 100), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 40, 14))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (200, 200))
        position = [self.hitbox.bottomleft[0] + 3, self.hitbox.bottomleft[1] - 15 + self.animation_frame]
        surface.blit(shape_surf, position)

    def draw(self):
        # self.draw_shadow(self.room.tile_map.map_surface)
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
