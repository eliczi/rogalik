import pygame


# pokoje naokoło,
# jak tab, to cala odkryta mapa
class MiniMap:
    room_height = 20
    room_width = 40
    room_dimensions = (room_width, room_height)

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.current_x, self.current_y = 0, 0
        self.offset_x = 10
        self.offset_y = 10
        self.color = (150, 148, 153)
        self.rooms = []

    def add_room(self):
        pass
    def current_room(self, room):
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
        # self.draw_perimeters(surface)
        for x in range(self.width):
            for y in range(self.height):
                position = (self.offset_x + x * self.room_width * 1.2, self.offset_y + y * self.room_height * 1.2)
                if x == self.current_y and y == self.current_x:
                    pygame.draw.rect(surface, self.color, (*position, *self.room_dimensions))
                    #pygame.draw.rect(surface, self.color, (*position, *self.room_dimensions), 4)
                else:
                    pygame.draw.rect(surface, self.color, (*position, *self.room_dimensions), 4)
