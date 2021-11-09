import os
import pygame
import utils


def load_animation_sprites(path):
    """Loads animation frames(.png files) from specified directory to a dictionary"""

    animation_data = {"IDLE": [], "WALK": [], "RUN": [], 'HURT': [], 'DEAD': []}

    animation_states = os.listdir(path)  # Lists all the subdirectories in specified path
    for state in animation_states:
        sub_states = os.listdir(path + state)
        for sub_state in sub_states:
            key = state.upper()  # key to dictionary
            animation_image = pygame.image.load(path + state + '/' + sub_state).convert_alpha()
            animation_image = pygame.transform.scale(animation_image, utils.basic_entity_size)
            animation_data[key].append(animation_image)

    return animation_data


def entity_animation(entity):
    def moving() -> bool:
        """s"""
        if sum(entity.velocity):
            return True
        return False

    def update_animation_direction():
        if entity.direction == 'RIGHT':
            entity.animation_direction = 'right'
        elif entity.direction == 'LEFT':
            entity.animation_direction = 'left'

    def update_animation_frame():
        """sss"""
        entity.animation_frame += 1.5 / 15
        if entity.animation_frame >= 4:
            entity.animation_frame = 0

    def idle_animation(state):
        """Animation if idle"""
        update_animation_frame()
        if entity.animation_direction == 'left':
            entity.image = entity.animation_database[state][int(entity.animation_frame)]
        elif entity.animation_direction == 'right':
            entity.image = entity.animation_database[state][int(entity.animation_frame)]
            entity.image = pygame.transform.flip(entity.image, 1, 0)

    def death_animation(state):
        entity.animation_frame += 0.8 / 15
        if entity.animation_frame >= 4:
            entity.death_counter = 0
            entity.animation_frame = 0
        if entity.animation_direction == 'left':
            entity.image = entity.animation_database[state][int(entity.animation_frame)]
        elif entity.animation_direction == 'right':
            entity.image = entity.animation_database[state][int(entity.animation_frame)]
            entity.image = pygame.transform.flip(entity.image, 1, 0)

    def animation():
        """s"""
        if entity.dead:
            death_animation('DEAD')
        elif entity.hurt:
            entity.animation_frame = 0
            entity.counter += 1
            if entity.counter > 15:
                entity.hurt = False
                entity.counter = 0
            idle_animation('HURT')
        elif moving():
            idle_animation('WALK')
        else:
            idle_animation('IDLE')

    def update():
        update_animation_direction()
        animation()

    return update


def map_animation():
    def initialise_next_room(self, game, value, direction):
        if direction in ('up', 'down'):
            game.next_room = game.world[game.x + value][game.y].room_image
            game.next_room.y += value * 12 * 64
            game.player.rect.y -= value * 7 * 64
        else:
            game.next_room = game.world[game.x][game.y + value].room_image
            game.next_room.x += value * 17 * 64
            game.player.rect.x = 120
        game.next_room.load_map()

    def move_rooms(self, direction, value, game):
        if direction in ('up', 'down'):
            self.y -= value * 30
            if game.next_room:
                game.next_room.y -= value * 30
        else:
            self.x -= value * 30
            if game.next_room:
                game.next_room.x -= value * 30

    def animation(self, direction, game, value):
        if direction == 'up' and self.y < utils.world_size[1] + 64:
            self.move_rooms(direction, value, game)
            if self.y + self.map_height * 64 - 64 > utils.world_size[1] and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        elif direction == 'down' and self.y > - 13 * 64:
            self.move_rooms(direction, value, game)
            if self.y < - 64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        elif direction == 'right' and self.x + 64 > 0 - 17 * 64:
            self.move_rooms(direction, value, game)
            if self.x < -64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        elif direction == 'left' and self.x < utils.world_size[0] + 64:
            self.move_rooms(direction, value, game)
            if self.x > 5 * 64 and game.next_room is None:
                self.initialise_next_room(game, value, direction)
        else:
            if direction in ('up', 'down'):
                game.x += value
            elif direction in ('right', 'left'):
                game.y += value
            game.directions = None
            self.change_room(game)

    def change_room(self, game):
        game.room = game.world[game.x][game.y]
        game.room_image = game.room.room_image
        game.player.can_move = True
        self.x, self.y = 3 * 64, 64
        game.next_room = None
