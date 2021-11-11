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


# def entity_animation(entity):

class EntityAnimation:
    def __init__(self, entity):
        self.entity = entity

    def moving(self) -> bool:
        """s"""
        if sum(self.entity.velocity):
            return True
        return False

    def update_animation_direction(self):
        if self.entity.direction == 'RIGHT':
            self.entity.animation_direction = 'right'
        elif self.entity.direction == 'LEFT':
            self.entity.animation_direction = 'left'

    def update_animation_frame(self):
        """sss"""
        self.entity.animation_frame += 1.5 / 15
        if self.entity.animation_frame >= 4:
            self.entity.animation_frame = 0

    def idle_animation(self, state):
        """Animation if idle"""
        self.update_animation_frame()
        if self.entity.animation_direction == 'left':
            self.entity.image = self.entity.animation_database[state][int(self.entity.animation_frame)]
        elif self.entity.animation_direction == 'right':
            self.entity.image = self.entity.animation_database[state][int(self.entity.animation_frame)]
            self.entity.image = pygame.transform.flip(self.entity.image, 1, 0)

    def death_animation(self):
        state = 'DEAD'
        self.entity.animation_frame += 1.0 / 15
        if self.entity.animation_frame >= 4:
            self.entity.death_counter = 0
        if self.entity.animation_frame < 1:
            state = 'HURT'
        else:
            state = 'DEAD'
        if self.entity.animation_frame <= 4:
            if self.entity.animation_direction == 'left':
                self.entity.image = self.entity.animation_database[state][int(self.entity.animation_frame)]
            elif self.entity.animation_direction == 'right':
                self.entity.image = self.entity.animation_database[state][int(self.entity.animation_frame)]
                self.entity.image = pygame.transform.flip(self.entity.image, 1, 0)

    def animation(self):
        """s"""
        if self.entity.dead:
            self.death_animation()
        elif self.entity.hurt:
            self.entity.animation_frame = 0
            self.idle_animation('HURT')
            # if 0.3 seconds have passed
            if pygame.time.get_ticks() - self.entity.time > 300:
                self.entity.hurt = False
        elif self.moving():
            self.idle_animation('WALK')
        else:
            self.idle_animation('IDLE')

    def update(self):
        self.update_animation_direction()
        self.animation()


# return update

