import pygame, csv, os
import utils
from player import Player


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


def get_map(world, position):
    return world[position[0]][position[1]]


class Tile(pygame.sprite.Sprite):
    def __init__(self, rectangle, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.image_at(rectangle)
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def new_image(self, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (64, 64))


class TileMap():
    def __init__(self, filename, spritesheet, map_size=(15 * 64, 11 * 64)):
        self.tile_size = 64
        self.spritesheet = spritesheet
        self.wall_list = []
        self.entrance = []
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface(map_size)
        self.map_surface.fill((0, 0, 0))
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()
        self.x, self.y = 3 * 64, 64
        self.previous = {'up': False,
                         'down': False,
                         'right': False,
                         'left': False}
        self.previous = False

    def animation(self):
        if self.x < 0:
            self.x += 21
        elif self.x > 0:
            self.x -= 21
        elif self.y > 0:
            self.y -= 16
        elif self.y < 0:
            self.y += 16

    # better animation
    def testing(self):
        if self.previous:
            self.x += 21
        else:
            self.animation()

    def draw_map(self, surface):
        #self.testing()

        surface.blit(self.map_surface, (self.x, self.y))

    def load_map(self):
        self.map_surface.fill(utils.BLACK)
        for tile in self.tiles:
            tile.draw(self.map_surface)
            #pygame.draw.rect(self.map_surface, (0, 0, 255), tile.rect, 1)

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
        return b * 16, a * 16

    def load_tiles(self, filename):
        tiles = []
        room_map = filename
        x, y = 0, 64
        for row in room_map:
            x = 64
            for tile in row:
                tiles.append(Tile((*self.location(int(tile)), 16, 16), x, y, self.spritesheet))
                if int(tile) in (-1, 75):
                    self.entrance.append(tiles[-1])
                if int(tile) in (135, 15, 17, 60, 61, 62, 63, 1, 18, 3, 46, 45, 40, 42, 47, 0, 30, 2, 32):
                    self.wall_list.append(tiles[-1])
                x += self.tile_size
            y += self.tile_size
        return tiles

    def next_level(self, game, player, current_map, world):
        for wall in self.entrance:
            if wall.rect.collidepoint(player.hitbox.midbottom) \
                    or wall.rect.collidepoint(player.hitbox.bottomleft) \
                    or wall.rect.collidepoint(player.hitbox.bottomright):
                self.previous = True
                player.can_move = False
                game.map2 = self
                if player.rect.y < 100:
                    current_map[0] -= 1
                    player.rect.y = 572
                    world[current_map[0]][current_map[1]].room_image.y -= 720
                elif player.rect.y > 500:
                    current_map[0] += 1
                    player.rect.y = 64
                    world[current_map[0]][current_map[1]].room_image.y += 720
                elif player.rect.x > 600:
                    current_map[1] += 1
                    player.rect.x = 50
                    world[current_map[0]][current_map[1]].room_image.x += 21 * 64
                elif player.rect.x < 100:
                    current_map[1] -= 1
                    player.rect.x = 1228
                    world[current_map[0]][current_map[1]].room_image.x = -21 * 64
