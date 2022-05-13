import pygame
from .object import Object

class Poop(Object):
    name = 'poop'
    type = 'poop'
    size = (64, 64)

    def __init__(self, game, room, position):
        super().__init__(game, self.name, self.type, self.size, room, position)
        self.dropped = False
        self.bounce = None

    def load_image(self):
        self.image = pygame.image.load('./assets/objects/poop/poop.png').convert_alpha()

    def detect_collision(self):
        pass

    def draw(self):
        surface = self.room.tile_map.map_surface
        surface.blit(self.image, (self.rect.x, self.rect.y))
