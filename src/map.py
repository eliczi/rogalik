import pygame, csv, os
import random
import copy
from map_generator import map_generator, Room


class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey=None):
        "Loads image from x,y,x+offset,y+offset"
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
        # Manual load in: self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def map_size(self, game):
        self.image_size = (64, 64)
        self.image_size = tuple(int(game.zoom_level * x) for x in self.image_size)
        self.image = pygame.transform.scale(self.image, self.image_size)

    def update(self, game):
        self.map_size(game)
        c = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = c


def testing():
    game_world = map_generator(3, 3, 3)  # generate world
    with open('../maps/test_map.csv', newline='') as f:  # load room template
        reader = csv.reader(f)
        basic_map = list(reader)

    for row in game_world:  # make passage through rooms
        for room in row:
            if isinstance(room, Room):
                room_map = copy.deepcopy(basic_map)
                for door in room.doors:
                    if door == 'left':
                        room_map[5][0] = -1
                    if door == 'right':
                        room_map[5][20] = -1
                    if door == 'up':
                        room_map[0][10] = -1
                        room_map[1][10] = -1
                    if door == 'down':
                        room_map[10][10] = -1
                    room.room_map = room_map
    return game_world


class TileMap():
    def __init__(self, game, filename, spritesheet):
        self.game = game
        self.tile_size = 64
        self.spritesheet = spritesheet
        self.wall_list = []
        self.entrance = []
        self.start_x, self.start_y = 0, 0
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface(self.game.SIZE)
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()
        # map structure = map layers, entrances, exits, wall_list,

    def draw_map(self, surface):
        if self.game.zoom_level != 1.0:
            self.update_tiles()
            self.map_surface.fill((0, 0, 0))
            self.load_map()

        surface.blit(self.map_surface, (0, 0))

    def update_tiles(self):
        for tile in self.tiles:
            tile.update(self.game)

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)

    def read_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map

    def location(self, number):
        a = number // 15
        b = number % 15
        x = b * 16, a * 16
        return x

    def load_tiles(self, filename):
        tiles = []
        map = filename
        x, y = 0, 0
        for row in map:
            x = -0
            for tile in row:
                tiles.append(Tile((*self.location(int(tile)), 16, 16), x, y, self.spritesheet))
                if int(tile) == -1:
                    self.entrance.append(tiles[-1])
                if int(tile) in (135, 15, 17, 60, 61, 62, 63, 1, 18, 3, 46, 45, 40, 42, 47):
                    self.wall_list.append(tiles[-1])
                # Move to next tile in current row
                x += 64
            # Move to next row
            y += 64
            # Store the size of the tile map
        return tiles
