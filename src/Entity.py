import pygame
import os

'''Parent class for characters'''


class Entity(pygame.sprite.Sprite):
    def __init__(self, game, ):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.animation_database = {"IDLE_LEFT": [],
                                   "IDLE_RIGHT": [],
                                   "WALK_LEFT": [],
                                   "WALK_RIGHT": []}
        self.game = game
        self.image = None
        self.velocity = [0, 0]
        self.old_velocity = [0, 0]
        self.speed = None
        self.priority = None
        self.direction = None
        self.animation_index = 0
        self.hp = None
        # loading all animations associated with given entity

    '''Function that returns entity hitbox around its non-transparent pixels(.png)'''

    def getMaskRect(self, surf, top=0, left=0):
        """

        :param surf:
        :type surf:
        :param top:
        :type top:
        :param left:
        :type left:
        :return:
        :rtype:
        """
        surf_mask = pygame.mask.from_surface(surf)
        rect_list = surf_mask.get_bounding_rects()
        surf_mask_rect = rect_list[0].unionall(rect_list)
        surf_mask_rect.move_ip(top, left)
        return surf_mask_rect

    def load_animation(self, path):
        """

        :param path:
        :type path:
        :return:
        :rtype:
        """
        animation_states = os.listdir(path)
        for state in animation_states:
            substates = os.listdir(path + state)
            for ss in substates:
                image_loc = ss
                elements = image_loc.split('_')
                key = state.upper() + '_' + elements[0].upper()  # key to dictionary
                animation_image = pygame.image.load(path + state + '/' + image_loc).convert()
                animation_image = pygame.transform.scale(animation_image, self.image_size)
                self.animation_database[key].append(animation_image)
