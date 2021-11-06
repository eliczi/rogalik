import os
import pygame
import utils

def load_animation_sprites(path):
    """Loads animation frames(.png files) from specified directory to a dictionary"""

    animation_data = {"IDLE": [],
                      "WALK": []
                    }

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
        entity.animation_frame += 1.0 / 15
        if entity.animation_frame >= 4:
            entity.animation_frame = 0

    def idle_animation():
        """Animation if idle"""
        update_animation_frame()
        if entity.animation_direction == 'left':
            entity.image = entity.animation_database["IDLE"][int(entity.animation_frame)]
        elif entity.animation_direction == 'right':
            entity.image = entity.animation_database["IDLE"][int(entity.animation_frame)]
            entity.image = pygame.transform.flip(entity.image, 1, 0)

    def walking_animation():
        """s"""
        update_animation_frame()
        if entity.animation_direction == 'left':
            entity.image = entity.animation_database["WALK"][int(entity.animation_frame)]
        elif entity.animation_direction == "right":
            entity.image = pygame.transform.flip(entity.animation_database["WALK"][int(entity.animation_frame)], True,
                                               False)

    def animation():
        """s"""
        if moving():
            walking_animation()
        else:
            idle_animation()

    update_animation_direction()
    animation()
