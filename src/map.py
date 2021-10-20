import pygame, csv, os
import random
import copy

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


class Room:
    def __init__(self, x, y, starting):
        self.x = x
        self.y = y
        self.starting = starting
        self.neighbours = []
        # we need to specify side from which it is possible to get to the neighbour
        self.doors = []

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __str__(self):
        return f'({self.x}, {self.y})'

    def position_to_side(self, position):
        direction = None
        if position[0] == 1:
            direction = 'up'
        elif position[0] == -1:
            direction = 'down'
        elif position[1] == 1:
            direction = 'left'
        elif position[1] == -1:
            direction = 'right'

        self.doors.append(direction)

    def door_position(self):
        if len(self.neighbours) == 1:  # if only 1 neighbour, there must be a door to that neighbour
            position = [self.x - self.neighbours[0][0], self.y - self.neighbours[0][1]]
            self.position_to_side(position)  # add position to door list
        else:
            for neighbour in self.neighbours:
                position = [self.x - neighbour[0], self.y - neighbour[1]]
                self.position_to_side(position)


def map_generator(num_of_rooms, width, height):
    """Generate specified number of room in a world of specified size and connection between them"""
    world_width, world_height = width, height  # world size
    world = [[None for x in range(world_width)] for y in range(world_height)]

    x, y = random.randint(0, world_width - 1), random.randint(0, world_height - 1)
    print(x, y)

    def check_boundary(x, world_param):  # checks if x doesnt exceed world boundary
        if x >= world_param or x < 0:
            return False
        else:
            return True

    def check_free_space():  # returns free neighbouring spaces
        free_space = []
        for i in range(-1, 2, 2):
            if check_boundary(x + i, world_height) and world[x + i][y] is None:
                free_space.append([x + i, y])
        for q in range(-1, 2, 2):
            if check_boundary(y + q, world_width) and world[x][y + q] is None:
                free_space.append([x, y + q])
        return free_space

    def reset_world():  # resets game world
        for i in range(world_height):
            for y in range(world_width):
                world[i][y] = None

    room_counter = 0
    first_room = True
    start_room = None
    while room_counter < num_of_rooms:
        if first_room:
            start_room = world[x][y] = Room(x, y, True)
            first_room = False
        else:
            world[x][y] = Room(x, y, False)
        free_room = check_free_space()
        if free_room:
            move = random.choice(free_room)
            x, y = move[0], move[1]
            room_counter += 1
        else:
            reset_world()
            first_room = True
            room_counter = 0

    def add_neighbors():  # appends neighbours of every room
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    for i in range(-1, 2, 2):  # up/down
                        if check_boundary(room.x + i, world_height) and world[room.x + i][room.y] is not None:
                            room.neighbours.append([room.x + i, room.y])
                    for q in range(-1, 2, 2):  # left/right
                        if check_boundary(room.y + q, world_width) and world[room.x][room.y + q] is not None:
                            room.neighbours.append([room.x, room.y + q])
                    room.door_position()

    def print_world():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print('')

    def print_nei():
        for row in world:
            for room in row:
                if isinstance(room, Room):

                    print(room, room.neighbours, room.doors)

    # add_neighbors()
    # print_world()
    # print_nei()

    return world

def map_loader(num_room):
    numer = num_room
    map_info = generator()
    with open('../maps/test_map.csv', newline='') as f:
        reader = csv.reader(f)
        basic_map = list(reader)

    def get_direction(numer):
        start_b = [k for k, v in map_info[numer][1].items() if v]
        direction = start_b[0]
        # Tu zmienic zeby mapa sie dobrze ladowala
        return direction


    direction = get_direction(numer)
    map = copy.deepcopy(basic_map)
    if direction == 'left':
        map[5][0] = -1
    if direction == 'right':
        map[5][20] = -1
    if direction == 'up':
        map[0][10] = -1
        map[1][10] = -1
    if direction == 'down':
        map[10][10] = -1

    return map


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
        # for tile in self.tiles:
        #     pygame.draw.rect(self.game.screen, (255, 0, 0), tile.rect, 1)

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
        map = filename  # self.read_csv(filename)
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
