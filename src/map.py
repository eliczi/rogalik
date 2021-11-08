import csv
import os
import pygame

import utils
from collections import namedtuple


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
    def __init__(self, filename, spritesheet):
        self.map_width = len(filename[0]) + 2  # offset
        self.map_height = len(filename) + 2
        self.map_size = (self.map_width * 64, self.map_height * 64)

        self.tile_size = 64
        self.spritesheet = spritesheet
        self.wall_list = []
        self.door = namedtuple('Door', ['direction', 'value', 'tile'])
        self.entrances = []
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface(self.map_size)
        self.map_surface.set_colorkey((0, 0, 0))
        self.x, self.y = 3 * 64, 64  # position of screen surface

    def draw_map(self, surface):
        surface.blit(self.map_surface, (self.x, self.y))

    def load_map(self):
        self.map_surface.fill(utils.BLACK)
        for tile in self.tiles:
            tile.draw(self.map_surface)
            # pygame.draw.rect(self.map_surface, (0, 0, 255), tile.rect, 1)

    @staticmethod
    def get_location(number):
        a = number // 15
        b = number % 15
        return b * 16, a * 16

    def add_entrance(self, tile):
        if tile.rect.y == 128:
            self.entrances.append(self.door('up', -1, tile))
        if tile.rect.y == 640:
            self.entrances.append(self.door('down', 1, tile))
        if tile.rect.x == 64:
            self.entrances.append(self.door('left', -1, tile))
        if tile.rect.x == 832:
            self.entrances.append(self.door('right', 1, tile))

    def load_tiles(self, filename):
        tiles = []
        room_map = filename
        x, y = 0, 64
        for row in room_map:
            x = 64
            for tile in row:
                tiles.append(Tile((*self.get_location(int(tile)), 16, 16), x, y, self.spritesheet))
                if int(tile) in (-1, 75):
                    self.add_entrance(tiles[-1])
                if int(tile) in utils.wall_list:
                    self.wall_list.append(tiles[-1])
                x += self.tile_size
            y += self.tile_size
        return tiles

    @staticmethod
    def initialise_next_room(game, value, direction):
        if direction in ('up', 'down'):
            game.next_room = game.world[game.x + value][game.y].room_image
            game.next_room.y += value * 12 * 64
            game.player.rect.y -= value * 7 * 64
        else:
            game.next_room = game.world[game.x][game.y + value].room_image
            game.next_room.x += value * 17 * 64
            game.player.rect.x -= value * 10.5 * 64
        game.next_room.load_map()

    def move_rooms(self, direction, value, game):
        if direction in ('up', 'down'):
            self.y -= value * 30
            if game.next_room:
                game.next_room.y -= value * 30
        else:
            self.x -= value * 30
            if game.next_room:
                game.next_room.x -= value * 30

    def animation(self, direction, game, value):
        if direction == 'up' and self.y < utils.world_size[1] + 64:
            self.move_rooms(direction, value, game)
            if self.y + self.map_height * 64 - 64 > utils.world_size[1] and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        elif direction == 'down' and self.y > - 13 * 64:
            self.move_rooms(direction, value, game)
            if self.y < - 64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        elif direction == 'right' and self.x + 64 > 0 - 17 * 64:
            self.move_rooms(direction, value, game)
            if self.x < -64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        elif direction == 'left' and self.x < utils.world_size[0] + 64:
            self.move_rooms(direction, value, game)
            if self.x > 5 * 64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        else:
            if direction in ('up', 'down'):
                game.x += value
            elif direction in ('right', 'left'):
                game.y += value
            game.directions = None
            self.change_room(game)

    def change_room(self, game):
        game.room = game.world[game.x][game.y]
        game.room_image = game.room.room_image
        game.player.can_move = True
        self.x, self.y = 3 * 64, 64
        game.next_room = None

    def load_level(self, game, direction, value):
        self.animation(direction, game, value)

    def detect_passage(self, player):
        collide_points = (player.hitbox.midbottom, player.hitbox.bottomleft, player.hitbox.bottomright)
        for door in self.entrances:
            if any(door.tile.rect.collidepoint(point) for point in collide_points):
                return door.direction, door.value
