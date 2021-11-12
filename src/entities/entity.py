import pygame
from animation import load_animation_sprites, EntityAnimation
from weapon import Weapon
import utils
from utils import get_mask_rect


class Entity:
    def __init__(self, game, name):
        self.game = game
        self.animation_database = load_animation_sprites(f'../assets/{name}/')
        self.image = pygame.transform.scale(pygame.image.load(f'../assets/{name}/idle/idle0.png').convert_alpha(),
                                            utils.basic_entity_size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(512, 400))
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.velocity = [0, 0]
        self.hurt = False
        self.dead = False
        self.direction = ''
        self.can_move = True
        self.player_animation = EntityAnimation(self)
        self.counter = 0
        self.time = 0


