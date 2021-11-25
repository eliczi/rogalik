from .map_generator import World
import utils


class WorldManager:
    number_of_rooms = 6
    world_width = 4
    world_height = 4
    map_width = 13
    map_height = 19

    def __init__(self, game):
        self.game = game
        self.world = World(self, self.number_of_rooms, self.world_width, self.world_height)
        self.x, self.y = self.world.starting_room.x, self.world.starting_room.y  #
        self.current_room = self.room = self.world.starting_room
        self.current_map = self.current_room.tile_map
        self.next_room = None
        self.next_room_map = None

    def set_current_room(self, room):
        self.current_room = room
        self.current_map = room.tile_map

    def set_next_room(self, room):
        self.next_room = room
        self.next_room_map = room.tile_map

    def draw_map(self, surface):
        self.current_map.draw(surface)
        if self.next_room:
            self.next_room.draw(surface)

    def update(self):
        self.detect_next_room()

    def detect_next_room(self):  # checks if player goes through one of 4 possible doors
        player = self.game.player
        direction = None
        value = None
        if player.can_move:
            if player.rect.y <= 96:
                direction = 'up'
                value = -1
            elif player.rect.y >= 11 * 64:
                direction = 'down'
                value = 1
            elif player.rect.x <= 3 * 64:
                direction = 'left'
                value = -1
            elif player.rect.x > 17 * 64:
                direction = 'right'
                value = 1
                player.can_move = False
                self.initialize_next_room(direction)
                self.move_rooms(direction, value)

    def initialize_next_room(self, direction):
        if direction == 'up':
            self.next_room = self.world.world[self.x - 1][self.y]
            self.next_room_map.y = -13 * 64
        elif direction == 'down':
            self.next_room = self.world.world[self.x + 1][self.y]
            self.next_room_map.y = utils.world_size[1]
        elif direction == 'right':
            self.set_next_room(self.world.world[self.x][self.y + 1])
            self.next_room_map.x = utils.world_size[0]
        elif direction == 'left':
            self.next_room = self.world.world[self.x][self.y - 1]
            self.next_room_map.x = 0 - 17 * 64

        self.next_room_map = self.next_room.tile_map

    def move_rooms(self, direction, value):
        anim_speed = 832 / 12
        if direction in ('up', 'down'):
            self.current_map.y -= value * anim_speed
            self.next_room_map.y -= value * anim_speed
        else:
            self.current_map.x -= value * anim_speed
            self.next_room_map.x -= value * anim_speed

    def change_room(self):
        self.current_map.correct_map_position()
        self.set_current_room(self.world.world[self.x][self.y])
        self.game.player.can_move = True
        self.next_room = None
