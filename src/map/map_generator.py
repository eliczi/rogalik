import copy
import csv
import random


from src.objects.chest import Chest
from .map import TileMap, Spritesheet
from src.objects.weapon import Weapon, AnimeSword, FireSword, Staff
from src.objects.flask import RedFlask, GreenFlask
from src.particles import Fire
from src.entities.boss import Boss
from src.objects.power_up import ShieldPowerUp, AttackPowerUp
from src.entities.merchant import Merchant
import src.utils as utils


class Room:
    def __init__(self, x, y):
        self.x = x  # position in game world
        self.y = y
        self.position = [x, y]
        self.neighbours = []  # neighbouring rooms coordinates
        self.doors = []  # door locations
        self.type = None  # type of the room
        self.room_map = []  # csv file of Tile identifiers
        self.tile_map = None  # TileMap
        self.discovered = False  # player been in this room
        self.enemy_list = []  # list of enemies at that room
        self.objects = []  # various objects like powerups or chests or weapons

    def __repr__(self):
        return f'({self.x}, {self.y}), {self.type})'  # str(self)?

    def __str__(self):
        return self.__repr__()

    def position_to_direction(self, position):
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

    def add_doors(self):
        # if len(self.neighbours) == 1:  # if only 1 neighbour, there must be a door to that neighbour
        #     position = [self.x - self.neighbours[0][0], self.y - self.neighbours[0][1]]
        #     self.position_to_direction(position)  # add position to door list
        # else:
        for neighbour in self.neighbours:
            position = [self.x - neighbour[0], self.y - neighbour[1]]
            self.position_to_direction(position)


class World:
    def __init__(self, wm, game, num_of_rooms, width, height):
        self.level = wm.level
        self.game = game
        self.num_of_rooms = num_of_rooms
        self.width = width
        self.height = height
        self.world = [[None for _ in range(width)] for _ in range(height)]  # populate world with
        self.x, self.y = random.randint(0, height - 1), random.randint(0, width - 1)  # current world coordinates
        self.starting_room = None
        self.create_world()

    def create_world(self):
        self.generate_rooms()
        self.assign_type()
        # self.add_neighbors()
        self.add_room_map('mapa4')
        self.add_room_map('mapa3')
        self.add_room_map('floor_layer')
        self.add_room_map('wall_layer')
        self.add_graphics()
        # self.print_world()
        self.assign_objects()

    @staticmethod
    def check_boundary(coordinate, world_param):  # checks if coordinate doesnt exceed world boundary
        return world_param > coordinate >= 0

    def check_free_space(self):  # returns free neighbouring spaces
        free_space = []
        for i in [-1, 1]:
            if self.check_boundary(self.x + i, self.height) and self.world[self.x + i][self.y] is None:
                free_space.append([self.x + i, self.y])
            if self.check_boundary(self.y + i, self.width) and self.world[self.x][self.y + i] is None:
                free_space.append([self.x, self.y + i])
        return free_space

    def reset_world(self):  # resets game world
        self.world = [[None for _ in range(self.width)] for _ in range(self.height)]

    def add_neighbour(self, target_room, room):
        target_room.neighbours.append(room)

    def generate_rooms(self):
        room_counter = 0  # counts current number of rooms - 1
        prev_room = [self.x, self.y]  # added
        current_room = None
        last_room = None
        num_monster_rooms = 2
        while room_counter < self.num_of_rooms:  # this while loop populates game world with one possible room-layout
            if room_counter == 0:
                self.starting_room = self.world[self.x][self.y] = current_room = Room(self.x, self.y)
                current_room.type = 'starting_room'
            else:
                self.world[self.x][self.y] = current_room = Room(self.x, self.y)
                if num_monster_rooms:
                    current_room.type = 'normal'
                    num_monster_rooms -= 1
                self.add_neighbour(current_room, prev_room)
                current_room.add_doors()
                prev_room = [self.x, self.y]
            empty_spaces = self.check_free_space()
            if empty_spaces:
                new_room = random.choice(empty_spaces)
                self.x, self.y = new_room[0], new_room[1]
                if room_counter != self.num_of_rooms - 1:
                    self.world[prev_room[0]][prev_room[1]].neighbours.append([self.x, self.y])
                else:
                    last_room = self.world[prev_room[0]][prev_room[1]]
                    last_room.type = 'boss'
                self.world[prev_room[0]][prev_room[1]].add_doors()
                room_counter += 1
            elif room_counter == self.width * self.height - 1:
                break
            else:
                self.reset_world()
                room_counter = 0

    def add_neighbors(self):  # appends neighbours of every room
        for row in self.world:
            for room in row:
                if isinstance(room, Room):
                    for i in [-1, 1]:  # up/down
                        if self.check_boundary(room.x + i, self.height) and self.world[room.x + i][room.y] is not None:
                            room.neighbours.append([room.x + i, room.y])
                        if self.check_boundary(room.y + i, self.width) and self.world[room.x][room.y + i] is not None:
                            room.neighbours.append([room.x, room.y + i])
                    room.add_doors()  # generates doors

    @staticmethod
    def shut_doors(doors, room_map, file):
        if 'left' not in doors:
            room_map[5][2] = 257
            room_map[6][2] = 257
            room_map[4][1] = -1
            room_map[5][1] = -1
            room_map[6][1] = -1
            room_map[7][1] = -1
            if file == 'floor_layer':
                room_map[5][2] = 130
                room_map[6][2] = 130
        if 'right' not in doors:
            room_map[5][16] = 256
            room_map[6][16] = 256
            room_map[5][17] = -1
            room_map[6][17] = -1
            room_map[4][17] = -1
            room_map[7][17] = -1
            if file == 'floor_layer':
                room_map[5][16] = 130
                room_map[6][16] = 130
        if 'up' not in doors:
            room_map[1][9] = 2
            room_map[2][9] = 33
            room_map[1][10] = 1
            room_map[1][9] = 1
            room_map[1][8] = 1
        if 'down' not in doors:
            room_map[9][9] = 2
            room_map[10][9] = 33
            room_map[10][8] = 33
            room_map[10][10] = 33
            room_map[11][8] = -1
            room_map[11][9] = -1
            room_map[11][10] = -1
            if file == 'floor_layer':
                room_map[9][9] = 130

    def random_floor_layout(self, room_map):
        w = [10, 1, 1, 1, 1, 0.2, 0.2, 0.2]
        floor_tiles = [129, 130, 131, 161, 162, 163, 193, 194]
        for x in range(len(room_map)):
            for y in range(len(room_map[0])):
                if int(room_map[x][y]) in utils.floor_tiles:
                    room_map[x][y] = random.choices(utils.floor_tiles, w, k=1)[0]

    def add_room_map(self, file):
        with open(f'./maps/{file}.csv', newline='') as f:  # load room template
            reader = csv.reader(f)
            basic_map = list(reader)

        for row in self.world:  # make passage through rooms
            for room in row:
                if isinstance(room, Room):
                    room_map = copy.deepcopy(basic_map)  # csv file
                    if file == 'floor_layer':
                        self.random_floor_layout(room_map)
                    self.shut_doors(room.doors, room_map, file)
                    room.room_map.append(room_map)

    def add_graphics(self):
        for row in self.world:
            for room in row:
                if isinstance(room, Room):
                    room.tile_map = TileMap(room, room.room_map, Spritesheet('./assets/misc/spritesheet.png'))

    def assign_objects(self):
        for row in self.world:
            for room in row:
                if isinstance(room, Room):
                    if room.type == 'chest':
                        room.objects.append(Chest(self.game, room))
                    elif room.type == 'starting_room' and self.level == 1:
                        room.objects.append(Staff(self.game, room, (650, 300)))
                        room.objects.append(AnimeSword(self.game, room, (550, 300)))
                        room.objects.append(FireSword(self.game, room, (750, 300)))
                    elif room.type == 'power_up':
                        power_ups = [ShieldPowerUp(self.game, room), AttackPowerUp(self.game, room)]
                        room.objects.append(random.choice(power_ups))
                    elif room.type == 'shop':
                        room.enemy_list.append(Merchant(self.game, room))

    def print_world(self):
        print('-' * 10)
        for row in self.world:
            for room in row:
                if isinstance(room, Room):
                    if room.type == 'starting_room':
                        print('x', end=' ')
                    else:
                        print(1, end=' ')
                else:
                    print(0, end=' ')
            print('')

    def assign_type(self):
        types = ['power_up', 'normal', 'chest', 'shop']
        ok_rooms = []
        for row in self.world:
            for room in row:
                if isinstance(room, Room) and room.type is None:
                    room.type = random.choices(types, weights=[2, 4, 1, 1], k=1)[0]
                    ok_rooms.append(room)
