import pygame, csv, os
import utils


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


def update_player_position():
    pass


class TileMap():
    def __init__(self, filename, spritesheet):
        self.tile_size = 64
        self.spritesheet = spritesheet
        self.wall_list = []
        self.entrance = []
        self.start_x, self.start_y = 0, 0
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface(utils.world_size)
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()

    def draw_map(self, surface):

        for entrance in self.entrance:
            pygame.draw.rect(self.map_surface, (255, 0, 0), entrance.rect, 2)
        surface.blit(self.map_surface, (0, 0))

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
        room_map = filename
        x, y = 0, 0
        for row in room_map:
            x = -0
            for tile in row:
                tiles.append(Tile((*self.location(int(tile)), 16, 16), x, y, self.spritesheet))
                if int(tile) == -1:
                    self.entrance.append(tiles[-1])
                if int(tile) in (135, 15, 17, 60, 61, 62, 63, 1, 18, 3, 46, 45, 40, 42, 47):
                    self.wall_list.append(tiles[-1])
                x += 64
            y += 64
        return tiles
