import random


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
