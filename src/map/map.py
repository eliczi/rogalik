import pygame
from collections import namedtuple
import math
import src.utils as utils


class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def image_at(self, rectangle, colorkey=None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        image.blit(self.sheet, (0, 0), rect)
        # if colorkey is not None:
        #     if colorkey is -1:
        #         colorkey = image.get_at((0, 0))
        #     colorkey = (0, 0, 0)
        # image.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, rectangle, x, y, spritesheet, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = spritesheet.image_at(rectangle)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def change_image(self, rectangle, spritesheet):
        self.image = spritesheet.image_at(rectangle)
        self.image = pygame.transform.scale(self.image, self.size)


class TileMap:
    def __init__(self, room, filename, spritesheet, tile_size=64):
        self.room = room
        # self.map_width = len(filename[0][0])
        # self.map_height = len(filename[0]) + 1
        # self.map_size = (len(filename[0][0]) * 64 + 128, (len(filename[0]) + 1) * 64)
        self.map_size = (utils.world_size[0], utils.world_size[1])
        self.tile_size = tile_size
        self.spritesheet = spritesheet
        self.wall_list = []
        self.door = namedtuple('Door', ['direction', 'value', 'tile'])
        self.tiles = []
        self.filename = filename
        self.load_tiles(filename)
        self.original_map_surface = pygame.Surface(self.map_size).convert()
        self.original_map_surface.set_colorkey((0, 0, 0, 0))
        self.map_surface = None
        self.x, self.y = 0, 0  # position of map surface on screen surface
        self.game = None
        self.load_map()

    def correct_map_position(self):
        if self.y != 0:
            self.y = 0
        if self.x != 0:
            self.x = 0

    def draw_map(self, surface):
        surface.blit(self.map_surface, (self.x, self.y))
        self.clear_map()
        # for wall in self.wall_list:
        #     pygame.draw.rect(surface, (255, 255, 255), wall.rect, 2)

    def clear_map(self):
        self.map_surface = self.original_map_surface.copy()

    def load_map(self):
        self.original_map_surface.fill(utils.BLACK)
        for layer in self.tiles:
            for tile in layer:
                tile.draw(self.original_map_surface)
        self.clear_map()

    @staticmethod
    def get_location(number):
        a = number // 32
        b = number % 32
        return b * 16, a * 16


    def load_tiles(self, filename):
        for file in filename:
            tiles = []
            x, y = 0, self.tile_size / 2
            for row in file:
                x = self.tile_size
                for tile in row:
                    tiles.append(Tile((*self.get_location(int(tile)), 16, 16), x, y, self.spritesheet,
                                      (self.tile_size, self.tile_size)))
                    if int(tile) in utils.wall_list:
                        self.wall_list.append(tiles[-1])
                    x += self.tile_size
                y += self.tile_size
            self.tiles.append(tiles)
