import os
import pygame
import src.utils as utils


def load_animation_sprites(path, size=utils.basic_entity_size):
    """Loads animation frames(.png files) from specified directory to a dictionary"""

    animation_data = {"IDLE": [], "WALK": [], "RUN": [], 'HURT': [], 'DEAD': []}
    animation_states = os.listdir(path)  # Lists all the subdirectories in specified path
    for state in animation_states:
        sub_states = os.listdir(path + state)
        for sub_state in sub_states:
            key = state.upper()  # key to dictionary
            animation_image = pygame.image.load(path + state + '/' + sub_state).convert_alpha()
            animation_image = pygame.transform.scale(animation_image, size)
            animation_data[key].append(animation_image)
    return animation_data


class EntityAnimation:
    def __init__(self, entity, death_anim=4, speed=25):
        self.entity = entity
        self.animation_direction = 'right'
        self.animation_frame = 0
        self.hurt_timer = 0
        self.death_animation_frames = death_anim
        self.speed = speed

    def moving(self) -> bool:
        """s"""
        return bool(sum(self.entity.velocity))

    def get_direction(self):
        self.animation_direction = 'right' if self.entity.velocity[0] >= 0 else 'left'

    def update_animation_frame(self):
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
        self.animation_frame += 1.0 / self.speed
        if self.animation_frame >= self.death_animation_frames:
            self.entity.death_counter = 0
        if self.animation_frame <= self.death_animation_frames:
            state = 'HURT' if self.animation_frame < 1 else 'DEAD'
            if self.entity.direction == 'left':
                self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            elif self.entity.direction == 'right':
                self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
                self.entity.image = pygame.transform.flip(self.entity.image, 1, 0)

    def hurt_animation(self):
        self.animation_frame = 0
        self.idle_animation('HURT')
        # if 0.3 seconds have
        if pygame.time.get_ticks() - self.hurt_timer > 300:
            self.hurt_timer = pygame.time.get_ticks()
            self.entity.hurt = False

    def animation(self):
        """s"""
        if self.entity.dead:
            self.death_animation()
        elif self.entity.hurt:
            self.hurt_animation()
        elif self.moving():
            self.idle_animation('WALK')
        else:
            self.idle_animation('IDLE')

    def update(self):
        self.animation()
