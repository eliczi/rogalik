import csv
import os
import pygame

import utils


class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey=None):
        """Loads image from x,y,x+offset,y+offset"""
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image


def get_map(world, position):
    return world[position[0]][position[1]]


class Tile(pygame.sprite.Sprite):
    def __init__(self, rectangle, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.image_at(rectangle)
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.wall_type = None  # if entrance, type =

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def new_image(self, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (64, 64))


class TileMap:
    def __init__(self, filename, spritesheet, doors, map_size=(15 * 64, 12 * 64)):
        self.tile_size = 64
        self.spritesheet = spritesheet
        self.wall_list = []
        self.entrance = []  # [Tile,direction]
        self.doors = doors
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface(map_size)
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()
        self.x, self.y = 3 * 64, 64

    def draw_map(self, surface):
        # self.testing()
        surface.blit(self.map_surface, (self.x, self.y))

    def load_map(self):
        self.map_surface.fill(utils.BLACK)
        for tile in self.tiles:
            tile.draw(self.map_surface)
            # pygame.draw.rect(self.map_surface, (0, 0, 255), tile.rect, 1)

    def read_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map

    def get_location(self, number):
        a = number // 15
        b = number % 15
        return b * 16, a * 16

    def load_tiles(self, filename):
        tiles = []
        room_map = filename
        x, y = 0, 64
        for row in room_map:
            x = 64
            for tile in row:
                tiles.append(Tile((*self.get_location(int(tile)), 16, 16), x, y, self.spritesheet))
                if int(tile) in [-1, 75]:
                    if tiles[-1].rect.x / 64 == 7 and tiles[-1].rect.y / 64 == 2:
                        self.entrance.append([tiles[-1], 'up'])
                    if tiles[-1].rect.x / 64 == 7 and tiles[-1].rect.y / 64 == 10:
                        self.entrance.append([tiles[-1], 'down'])
                    if tiles[-1].rect.x / 64 == 1 and tiles[-1].rect.y / 64 == 6:
                        self.entrance.append([tiles[-1], 'left'])
                    if tiles[-1].rect.x / 64 == 13 and tiles[-1].rect.y / 64 == 6:
                        self.entrance.append([tiles[-1], 'right'])
                if int(tile) in (135, 15, 17, 60, 61, 62, 63, 1, 18, 3, 46, 45, 40, 42, 47, 0, 30, 2, 32, 33, 3):
                    self.wall_list.append(tiles[-1])
                x += self.tile_size
            y += self.tile_size
        return tiles

    def animation(self, wall, game, direction):
        if wall[1] == 'up':
            self.y += 25
        elif wall[1] == 'down':
            self.y -= 25
        elif wall[1] == 'right':
            self.x += 35
        elif wall[1] == 'left':
            self.x -= 35
        print(self.x)
        if self.x < 0 - 15 * 64 or self.x > utils.world_size[0] or self.y + 13 * 64 < 0 or self.y > 15 * 64:
            if direction == 'up':
                game.room = game.world[game.x - 1][game.y]
                game.room_image = game.room.room_image
                self.x, self.y = 3 * 64, 64
            if direction == 'down':
                game.room = game.world[game.x + 1][game.y]
                game.room_image = game.room.room_image
                self.x, self.y = 3 * 64, 64
            if direction == 'right':
                game.room = game.world[game.x][game.y + 1]
                game.room_image = game.room.room_image
                self.x, self.y = 3 * 64, 64
            if direction == 'left':
                game.room = game.world[game.x][game.y - 1]
                game.room_image = game.room.room_image
                self.x, self.y = 3 * 64, 64

    def next_level(self, game, player, world):

        # for door in game.room.doors:
        #     pass
        for wall in self.entrance:
            if wall[0].rect.collidepoint(player.hitbox.midbottom) \
                    or wall[0].rect.collidepoint(player.hitbox.bottomleft) \
                    or wall[0].rect.collidepoint(player.hitbox.bottomright):
                player.can_move = False
                direction = wall[1]
                self.animation(wall, game, direction)
