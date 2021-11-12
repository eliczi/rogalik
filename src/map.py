import csv
import os
import pygame

import utils
from collections import namedtuple


class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def image_at(self, rectangle, colorkey=None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        # if colorkey is not None:
        #     if colorkey is -1:
        #         colorkey = image.get_at((0, 0))
        #     colorkey = (0, 0, 0)
        # image.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, rectangle, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.image_at(rectangle).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class TileMap:
    def __init__(self, room, filename, spritesheet, ):
        self.room = room
        self.map_width = len(filename[0][0]) + 2  # offset
        self.map_height = len(filename[0]) + 2
        self.map_size = (self.map_width * 64, self.map_height * 64)
        self.tile_size = 64
        self.spritesheet = spritesheet
        self.wall_list = []
        self.door = namedtuple('Door', ['direction', 'value', 'tile'])
        self.entrances = []
        self.tiles = []
        self.load_tiles(filename)
        self.original_map_surface = pygame.Surface(self.map_size).convert_alpha()
        self.original_map_surface.set_colorkey((0, 0, 0))
        self.map_surface = None
        # self.map_surface = pygame.Surface(self.map_size).convert_alpha()
        # self.map_surface.set_colorkey((0, 0, 0))
        self.x, self.y = 2 * 64, 64  # position of screen surface
        self.load_map()

    def correct_map_position(self):
        if self.y != 64:
            self.y = 64
        if self.x != 2 * 64:
            self.x = 128

    def draw_map(self, surface):
        for o in self.room.objects:
            o.draw()
        surface.blit(self.map_surface, (self.x, self.y))

    def clear_map(self):
        self.map_surface = self.original_map_surface.copy()

    def load_map(self):
        self.original_map_surface.fill(utils.BLACK)
        for layer in self.tiles:
            for tile in layer:
                tile.draw(self.original_map_surface)
        self.map_surface = self.original_map_surface

    @staticmethod
    def get_location(number):
        a = number // 32
        b = number % 32
        return b * 16, a * 16

    def add_entrance(self, tile):
        if tile.rect.y == 128:
            self.entrances.append(self.door('up', -1, tile))
        if tile.rect.y == 640:
            self.entrances.append(self.door('down', 1, tile))
        if tile.rect.x == 64:
            self.entrances.append(self.door('left', -1, tile))
        if tile.rect.x > 700:
            self.entrances.append(self.door('right', 1, tile))

    def load_tiles(self, filename):
        for file in filename:
            tiles = []
            x, y = 0, 64
            for row in file:
                x = 64
                for tile in row:
                    tiles.append(Tile((*self.get_location(int(tile)), 16, 16), x, y, self.spritesheet))
                    if int(tile) in (-10, 75, 163):
                        self.add_entrance(tiles[-1])
                    if int(tile) in utils.wall_list:
                        self.wall_list.append(tiles[-1])
                    x += self.tile_size
                y += self.tile_size
            self.tiles.append(tiles)

    @staticmethod
    def initialise_next_room(game, value, direction):
        if direction == 'up':
            game.next_room = game.world.world[game.x + value][game.y]
            game.next_room_image = game.next_room.tile_map
            game.next_room_image.y = -13 * 64
            game.player.rect.y -= value * 7 * 64
        elif direction == 'down':
            game.next_room = game.world.world[game.x + value][game.y]
            game.next_room_image = game.next_room.tile_map
            game.next_room_image.y = utils.world_size[1]
            game.player.rect.y -= value * 7 * 64
        elif direction == 'right':
            game.next_room = game.world.world[game.x][game.y + value]
            game.next_room_image = game.next_room.tile_map
            game.next_room_image.x = utils.world_size[0]
            game.player.rect.x = 112
        elif direction == 'left':
            game.next_room = game.world.world[game.x][game.y + value]
            game.next_room_image = game.next_room.tile_map
            game.next_room_image.x = 0 - 17 * 64
            game.player.rect.x = 910

    # game.next_room_image.load_map()

    def move_rooms(self, direction, value, game):
        anim_speed = 832 / 12  # 12
        if direction in ('up', 'down'):
            self.y -= value * anim_speed
            if game.next_room:
                game.next_room_image.y -= value * anim_speed
        else:
            self.x -= value * anim_speed
            if game.next_room:
                game.next_room_image.x -= value * anim_speed

    def animation(self, direction, game, value):
        if direction == 'up' and self.y < utils.world_size[1] + 64:
            if self.y + self.map_height * 64 + 64 > utils.world_size[1] and game.next_room is None:  # + 64 is of offset
                self.initialise_next_room(game, value, direction)  # to bottom edge
            self.move_rooms(direction, value, game)

        elif direction == 'down' and self.y > - 13 * 64:
            if self.y < 0 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
            self.move_rooms(direction, value, game)

        elif direction == 'right' and self.x + 64 > - 17 * 64:
            if self.x < 0 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
            self.move_rooms(direction, value, game)

        elif direction == 'left' and self.x < utils.world_size[0] + 64:
            if self.x > 5 * 64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
            self.move_rooms(direction, value, game)

        else:
            if direction in ('up', 'down'):
                game.x += value
            elif direction in ('right', 'left'):
                game.y += value
            game.directions = None
            self.change_room(game)

    def change_room(self, game):
        game.room = game.world.world[game.x][game.y]
        game.room_image = game.room.tile_map
        game.player.can_move = True
        self.x, self.y = 2 * 64, 64
        game.next_room = None
        game.room_image.correct_map_position()

    def load_level(self, game, direction, value):
        self.animation(direction, game, value)

    def detect_passage(self, player):
        collide_points = (player.hitbox.midbottom, player.hitbox.bottomleft, player.hitbox.bottomright)
        for door in self.entrances:
            if any(door.tile.rect.collidepoint(point) for point in collide_points):
                return door.direction, door.value
