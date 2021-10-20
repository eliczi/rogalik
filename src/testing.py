import random
from dataclasses import dataclass


class Room:
    def __init__(self, x, y, starting):
        self.x = x
        self.y = y
        self.starting = starting
        self.neighbours = list()

    def add_neighbor(self, room):
        self.neighbours.append(room)
        self.tidy_list()

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __str__(self):
        return f'({self.x}, {self.y})'

    def tidy_list(self):
        self.neighbours = self.neighbours[0]


def generator(num_of_rooms, width, height):
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

    def reset():  # resets game world
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
            reset()
            first_room = True
            room_counter = 0

    def neighbors(x, y):  # returns room neighbours
        neighbours = []
        for i in range(-1, 2, 2):
            if check_boundary(x + i, world_height) and world[x + i][y] is not None:
                neighbours.append([x + i, y])
        for q in range(-1, 2, 2):
            if check_boundary(y + q, world_width) and world[x][y + q] is not None:
                neighbours.append([x, y + q])

        return neighbours

    def print_world():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print('')

    print_world()

    def print_in_order():
        start = None
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    room.add_neighbor(neighbors(room.x, room.y))
                    print(room, "Neighbours: ", room.neighbours)

    print_in_order()


generator(num_of_rooms=5, width=3, height=3)
