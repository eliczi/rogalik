import random
from dataclasses import dataclass


class Room:
    def __init__(self, x, y, starting):
        self.x = x
        self.y = y
        self.starting = starting
        self.neighbours = []

    def add_neighbor(self, room):
        self.neighbours.append(room)


def generator(num_of_rooms):
    world_width, world_height = 5, 5  # world size
    world = [[0 for x in range(world_width)] for y in range(world_height)]

    x, y = random.randint(0, world_width - 1), random.randint(0, world_height - 1)

    def get_direction(x, y):
        directions = {'up': x + 1,
                      'down': x - 1,
                      'left': y - 1,
                      'right': y + 1
                      }
        return direction

    room_counter
    while room_counter != num_of_rooms:
        world[x][y] = Room(x, y, False)
        get_direction(x, y)

        room_counter += 1



    def print_world():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print('')

    print_world()


generator(5)
