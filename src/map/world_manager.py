from .map_generator import World
import src.utils as utils
import pygame


class WorldManager:
    number_of_rooms = 10  # add random values?
    world_width = 4
    world_height = 4
    level = 1

    def __init__(self, game):
        self.game = game
        self.world = None
        self.x, self.y = None, None
        self.current_room = None
        self.current_map = None
        self.next_room = None
        self.next_room_map = None
        self.switch_room = None
        self.direction, self.value = None, None
        self.new_level = False
        self.move_current_room = False
        self.load_world_manager()

    def load_world_manager(self):
        self.world = World(self, self.game, self.number_of_rooms, self.world_width, self.world_height)
        self.x, self.y = self.world.starting_room.x, self.world.starting_room.y
        self.current_room = self.world.starting_room
        self.current_map = self.current_room.tile_map
        self.next_room = None
        self.next_room_map = None
        self.switch_room = False
        self.direction, self.value = None, None

    def set_current_room(self, room):
        self.current_room = room
        self.current_map = room.tile_map

    def set_next_room(self, room=None):
        self.next_room = room
        if room:
            self.next_room_map = room.tile_map

    def draw_map(self, surface):
        self.current_map.draw_map(surface)
        if self.next_room:
            self.next_room_map.draw_map(surface)

    def move_entities(self, direction, value, anim_speed=30):
        if direction in ('up', 'down'):
            self.game.player.rect.y -= value * anim_speed
        else:
            self.game.player.rect.x -= value * anim_speed

    def move_rooms(self, direction, value):
        anim_speed = 30
        if direction in ('up', 'down'):
            self.current_map.y -= value * anim_speed
            self.next_room_map.y -= value * anim_speed
        else:
            self.current_map.x -= value * anim_speed
            self.next_room_map.x -= value * anim_speed
        self.end_condition()

    def update(self):
        self.detect_next_room()
        if self.switch_room:
            self.move_rooms(self.direction, self.value)
            self.move_entities(self.direction, self.value)
        if self.new_level:
            self.move_room()
        if self.move_current_room:
            self.move_current_rom()

    def detect_next_room(self):  # checks if player goes through one of 4 possible doors
        if not self.switch_room and self.game.player and self.game.player.falling is False and not self.move_current_room:
            player = self.game.player
            if player.rect.y <= 96:
                self.initialize_room_change('up', -1)
            elif player.rect.y >= 11 * 64:
                self.initialize_room_change('down', 1)
            elif player.rect.x <= 3 * 64:
                self.initialize_room_change('left', -1)
            elif player.rect.x > 17 * 64:
                self.initialize_room_change('right', 1)

    def initialize_room_change(self, direction, value):
        self.direction, self.value = direction, value
        self.initialize_next_room(direction)
        self.switch_room = True
        self.game.player.can_move = False
        self.game.player.interaction = False
        self.game.object_manager.interaction = False
        self.game.sound_manager.play_passage()

    def initialize_next_room(self, direction):
        if direction == 'up':
            self.set_next_room(self.world.world[self.x - 1][self.y])
            self.next_room_map.y = -13 * 64  # hard code
            self.game.player.rect.y = -3.3 * 64
        elif direction == 'down':
            self.set_next_room(self.world.world[self.x + 1][self.y])
            self.next_room_map.y = utils.world_size[1]
            self.game.player.rect.y = 16 * 64
        elif direction == 'right':
            self.set_next_room(self.world.world[self.x][self.y + 1])
            self.next_room_map.x = utils.world_size[0]
            self.game.player.rect.x = utils.world_size[0] + 3.3 * 64
        elif direction == 'left':
            self.set_next_room(self.world.world[self.x][self.y - 1])
            self.next_room_map.x = -19 * 64
            self.game.player.rect.x = -2.3 * 64

    def end_condition(self):
        if self.next_room_map.x <= 0 and self.direction == 'right':
            self.stop_room_change()
        if self.next_room_map.x >= 0 and self.direction == 'left':
            self.stop_room_change()
        if self.next_room_map.y <= 0 and self.direction == 'down':
            self.stop_room_change()
        if self.next_room_map.y >= 0 and self.direction == 'up':
            self.stop_room_change()

    def change_room(self):
        self.current_map.correct_map_position()
        self.next_room_map.correct_map_position()
        self.set_current_room(self.world.world[self.x][self.y])
        self.set_next_room()
        self.game.player.can_move = True
        self.game.player.interaction = True
        self.game.object_manager.interaction = True

    def stop_room_change(self):
        self.switch_room = False
        self.x, self.y = self.next_room.x, self.next_room.y
        self.change_room()

    def move_room(self):
        anim_speed = 30
        self.current_map.x += anim_speed
        self.end_conditi()

    def end_conditi(self):
        if self.current_map.x > 1100:
            self.new_level = False
            self.level += 1
            self.load_world_manager()
            self.current_map.x = -20 * 64
            self.move_current_room = True
            self.game.player.fall(-300)
            self.game.enemy_manager.add_enemies()
            self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Intro.wav'))

    def move_current_rom(self):
        anim_speed = 30
        self.current_map.x += anim_speed
        self.end_cod()

    def end_cod(self):
        if self.current_map.x >= 0:
            self.move_current_room = False
            self.current_map.correct_map_position()

    def load_new_level(self):
        self.new_level = True
        self.game.enemy_manager.damage_multiplier += 0.2
        self.game.enemy_manager.health_multiplier += 0.2
        self.game.player.floor_value = self.game.player.rect.y
        self.game.player.fall(-1000)
