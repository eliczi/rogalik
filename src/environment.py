import random
import pygame


class Wall(pygame.sprite.Sprite):
    def __init__(self, game, edge_length_w, edge_length_h, pos_x, pos_y, color, *groups):
        super().__init__(*groups)
        self.game = game
        wall = (edge_length_w, edge_length_h)
        self.image = pygame.Surface(wall)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
