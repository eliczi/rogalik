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


class EntityAnimation:

    def __init__(self, entity):
        self.entity = entity
