import pygame
import copy


class MiniMap:
    room_height = 25
    room_width = 36
    room_dimensions = (room_width, room_height)
    offset_x = 1150
    offset_y = 10

    def __init__(self, game):
        self.game = game
        self.current_room = None
        self.current_x, self.current_y = None, None
        self.color = (150, 148, 153)
        self.rooms = []
        self.adjacent_rooms = []
        self.visited_rooms = []
        self.draw_mini_map = True

    def add_room(self, room):
        if [room.x, room.y] not in self.visited_rooms:
            self.visited_rooms.append([room.x, room.y])

    def set_current_room(self, room):
        self.add_room(room)
        if self.current_room is not room:
            self.current_room = room
            self.current_x = self.current_room.x
            self.current_y = self.current_room.y
            self.set_adjacent_rooms()

    def set_adjacent_rooms(self):
        self.adjacent_rooms = copy.deepcopy(self.current_room.neighbours)

    def update(self):
        self.set_current_room(self.game.world_manager.current_room)
        self.positions()

    def positions(self):
        while self.current_x != 1 or self.current_y != 1:
            if self.current_x < 1:
                self.current_x += 1
                for room in self.adjacent_rooms:
                    room[0] += 1
            elif self.current_x > 1:
                self.current_x -= 1
                for room in self.adjacent_rooms:
                    room[0] -= 1
            if self.current_y < 1:
                self.current_y += 1
                for room in self.adjacent_rooms:
                    room[1] += 1
            elif self.current_y > 1:
                self.current_y -= 1
                for room in self.adjacent_rooms:
                    room[1] -= 1

    def draw_all(self, surface):
        for i, room in enumerate(self.visited_rooms):
            position = (self.offset_x + room[1] * self.room_width * 1.2,
                        self.offset_y + room[0] * self.room_height * 1.2)
            pygame.draw.rect(surface, self.color, (*position, *self.room_dimensions), 4)
        position = (self.offset_x + self.current_room.y * self.room_width * 1.2,
                    self.offset_y + self.current_room.x * self.room_height * 1.2)
        pygame.draw.rect(surface, (210, 210, 210,), (*position, *self.room_dimensions))

    def draw(self, surface):
        if self.draw_mini_map:
            for room in self.adjacent_rooms:
                position = (self.offset_x + room[1] * self.room_width * 1.2,
                            self.offset_y + room[0] * self.room_height * 1.2)
                pygame.draw.rect(surface, self.color, (*position, *self.room_dimensions), 4)
            position = (self.offset_x + self.current_y * self.room_width * 1.2,
                        self.offset_y + self.current_x * self.room_height * 1.2)
            pygame.draw.rect(surface, (210, 210, 210,), (*position, *self.room_dimensions))
