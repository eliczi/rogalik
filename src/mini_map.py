import pygame
from collections import namedtuple
from dataclasses import dataclass


# pokoje naokoło,
# jak tab, to cala odkryta mapa

class MiniMap:
    room_height = 21
    room_width = 33
    room_dimensions = (room_width, room_height)
    room = namedtuple('Room', ['x', 'y', 'visited'])

    offset_x = 10
    offset_y = 10

    def __init__(self, width, height):
        self.height, self.width = height, width
        self.current_x, self.current_y = 0, 0
        self.color = (150, 148, 153)
        self.adjacent_rooms = []
        self.visited_rooms = set()

    def add_room(self, room):
        self.visited_rooms.add((room.x, room.y))

    def current_room(self, room):
        self.add_room(room)
        self.current_x, self.current_y = room.x, room.y

    def enlarge(self):
        self.room_width *= 2
        self.room_height *= 2

    def draw_perimeters(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                position = (self.offset_x + x * 60, self.offset_y + y * 30)
                perimeters = (x + 10 for x in self.room_dimensions)
                per_pos = (position[0] - 5, position[1] - 4)
                pygame.draw.rect(surface, (255, 255, 255), (*per_pos, *perimeters))

    def update(self, world, room):
        self.current_room(room)
        pass

    def draw_near(self):
        pass

    def draw(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                position = (self.offset_x + x * self.room_width * 1.2, self.offset_y + y * self.room_height * 1.2)
                if x == self.current_y and y == self.current_x:
                    pygame.draw.rect(surface, (210, 210, 210,), (*position, *self.room_dimensions))
                else:
                    pygame.draw.rect(surface, self.color, (*position, *self.room_dimensions), 4)
