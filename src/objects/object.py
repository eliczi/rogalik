import pygame
from utils import get_mask_rect
from PIL import Image


class Object:
    def __init__(self, game, name, room=None):
        self.game = game
        self.name = name
        self.original_image = None
        self.image_picked = None
        self.hud_image = None
        self.hitbox = None
        self.image = None
        self.rect = None
        self.size = None

    def load_image(self):
        """Load weapon image and initialize instance variables"""
        self.original_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.image_picked = pygame.image.load(f'../assets/weapon/{self.name}/picked_{self.name}.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, self.size)
        self.hud_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}_hud.png').convert_alpha()
        self.hitbox = get_mask_rect(self.original_image, 0, 0)
        self.image = self.original_image
        self.rect = self.image.get_rect()

    def set_size(self, filepath):
        self.size = tuple(3 * x for x in Image.open(filepath).size)
