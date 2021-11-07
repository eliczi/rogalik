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
        self.entrances = {}  # [Tile,direction]
        self.doors = doors
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface(map_size)
        self.rect = self.map_surface.get_rect()
        self.map_surface.set_colorkey((0, 0, 0))
        # self.load_map()
        self.x, self.y = 3 * 64, 64

    def draw_map(self, surface):
        surface.blit(self.map_surface, (self.x, self.y))

    def load_map(self):
        self.map_surface.fill(utils.BLACK)
        for tile in self.tiles:
            tile.draw(self.map_surface)
            # pygame.draw.rect(self.map_surface, (0, 0, 255), tile.rect, 1)

    def read_csv(self, filename):
        mapa = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                mapa.append(list(row))
        return mapa

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
                        self.entrances['up'] = tiles[-1]
                    if tiles[-1].rect.x / 64 == 7 and tiles[-1].rect.y / 64 == 10:
                        self.entrances['down'] = tiles[-1]
                    if tiles[-1].rect.x / 64 == 1 and tiles[-1].rect.y / 64 == 6:
                        self.entrances['left'] = tiles[-1]
                    if tiles[-1].rect.x / 64 == 13 and tiles[-1].rect.y / 64 == 6:
                        self.entrances['right'] = tiles[-1]
                if int(tile) in utils.wall_list:
                    self.wall_list.append(tiles[-1])
                x += self.tile_size
            y += self.tile_size
        return tiles

    def is_screen_center(self):
        if self.x == 3 * 64 and self.y == 64:
            return True

    def move_room_to_screen_center(self):
        if self.y < 0:
            self.y += 16
        elif self.y > utils.world_size[1]:
            self.y -= 16
        elif self.x > utils.world_size[0]:
            self.x -= 16
        elif self.x < 0:
            self.x += 16

    def animation(self, wall, game):
        if wall == 'up':
            self.y += 16
        elif wall == 'down':
            self.y -= 16
        elif wall == 'right':
            self.x += 32
        elif wall == 'left':
            self.x -= 32

        self.load_level(game, wall)

    def load_level(self, game, direction):
        if direction == 'up':
            game.x -= 1
            game.player.rect.y += 7 * 64
        elif direction == 'down':
            game.x += 1
            game.player.rect.y -= 7 * 64
        elif direction == 'right':
            game.y += 1
            game.player.rect.x -= 10 * 64 + 30
        elif direction == 'left':
            game.y -= 1
            game.player.rect.x += 10 * 64 + 30
        game.room = game.world[game.x][game.y]
        game.room_image = game.room.room_image
        game.player.can_move = True
        self.x, self.y = 3 * 64, 64

    def next_level(self, game, player):
        for wall in self.entrances:
            collide_points = (player.hitbox.midbottom, player.hitbox.bottomleft, player.hitbox.bottomright)
            for collide_point in collide_points:
                if self.entrances[wall].rect.collidepoint(collide_point):
                    player.can_move = False
                    self.load_level(game, wall)
                    break  # as to not check other collide_point
                    # self.animation(wall, game, wall[1])
