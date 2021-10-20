import random
import csv
import copy
from map import TileMap


class Room:
    def __init__(self, x, y, starting):
        self.x = x
        self.y = y
        self.starting = starting  # starting room
        self.neighbours = []  # neighbouring rooms coordinates
        self.doors = []  # door locations
        self.type = None  # type of the room, to be added
        self.room_map = None  # csv-like file
        self.room_image = None  # TileMap

    def __repr__(self):
        return f'({self.x}, {self.y})' # str(self)?

    def __str__(self):
        return f'({self.x}, {self.y})'

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

    def door_position(self):
        if len(self.neighbours) == 1:  # if only 1 neighbour, there must be a door to that neighbour
            position = [self.x - self.neighbours[0][0], self.y - self.neighbours[0][1]]
            self.position_to_direction(position)  # add position to door list
        else:
            for neighbour in self.neighbours:
                position = [self.x - neighbour[0], self.y - neighbour[1]]
                self.position_to_direction(position)


def map_generator(num_of_rooms, width, height, spritesheet):
    """Generate specified number of room in a world of specified size and connection between them"""
    spritesheet = spritesheet
    world_width, world_height = width, height  # world size
    world = [[None for x in range(world_width)] for y in range(world_height)]

    x, y = random.randint(0, world_width - 1), random.randint(0, world_height - 1)

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
    while room_counter < num_of_rooms:
        if first_room:
            world[x][y] = Room(x, y, True)
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
                    room.door_position()  # generates doors

    def add_room_map():
        with open('../maps/test_map.csv', newline='') as f:  # load room template
            reader = csv.reader(f)
            basic_map = list(reader)

        for row in world:  # make passage through rooms
            for room in row:
                if isinstance(room, Room):
                    room_map = copy.deepcopy(basic_map)
                    for door in room.doors:
                        if door == 'left':
                            room_map[5][0] = -1
                        if door == 'right':
                            room_map[5][20] = -1
                        if door == 'up':
                            # room_map[0][10] = -1
                            room_map[1][10] = -1
                        if door == 'down':
                            room_map[10][10] = -1
                        room.room_map = room_map

    def add_graphics():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    room.room_image = TileMap(room.room_map, spritesheet)

    def print_world():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print('')

    add_neighbors()
    add_room_map()
    add_graphics()
    print_world()
    # print_nei()

    return world
