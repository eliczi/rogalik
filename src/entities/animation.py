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


class EntityAnimation:
    def __init__(self, entity):
        self.entity = entity
        self.animation_direction = 'right'
        self.animation_frame = 0

    def moving(self) -> bool:
        """s"""
        return bool(sum(self.entity.velocity))

    def get_direction(self):
        self.animation_direction = 'right' if self.entity.velocity[0] >= 0 else 'left'

    def update_animation_frame(self):
        """sss"""
        self.animation_frame += 1.5 / 15
        if self.animation_frame >= 4:
            self.animation_frame = 0

    def idle_animation(self, state):
        """Animation if idle"""
        self.update_animation_frame()
        self.get_direction()
        if self.animation_direction == 'left':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
        elif self.animation_direction == 'right':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            self.entity.image = pygame.transform.flip(self.entity.image, 1, 0)

    def death_animation(self):
        state = 'DEAD'
        self.animation_frame += 1.0 / 15
        if self.animation_frame >= 4:
            self.entity.death_counter = 0
        state = 'HURT' if self.animation_frame < 1 else 'DEAD'
        if self.animation_frame <= 4:
            if self.entity.direction == 'left':
                self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            elif self.entity.direction == 'right':
                self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
                self.entity.image = pygame.transform.flip(self.entity.image, 1, 0)

    def animation(self):
        """s"""
        if self.entity.dead:
            self.death_animation()
        elif self.entity.hurt:
            self.animation_frame = 0
            self.idle_animation('HURT')
            # if 0.3 seconds have passed
            if pygame.time.get_ticks() - self.entity.time > 300:
                self.entity.hurt = False
        elif self.moving():
            self.idle_animation('WALK')
        else:
            self.idle_animation('IDLE')

    def update(self):
        self.animation()
