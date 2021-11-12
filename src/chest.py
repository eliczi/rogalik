import pygame
import utils


class Chest:
    def __init__(self, room):
        self.room = room
        self.image = self.load_image()
        self.rect = self.image.get_rect(center=(15 * 64 / 2, 7 / 2 * 64))
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.animation_frame = 0
        self.surface = self.room.tile_map.map_surface

    @staticmethod
    def load_image():
        image = pygame.image.load(f'../assets/chest/full/chest_full0.png').convert_alpha()
        image = pygame.transform.scale(image, utils.basic_entity_size)
        return image

    def update(self):
        self.image = pygame.image.load(f'../assets/chest/full/chest_full{self.animation_frame}.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, utils.basic_entity_size)

    def draw(self):
        self.surface.blit(self.image, self.rect)
        pygame.draw.rect(self.surface, (255, 123, 234), self.rect, 2)

    def detect_collision(self, player):
        if player.rect.colliderect(self.rect):
            self.update_animation_frame()
            self.update()
            print('dupa')

    def update_animation_frame(self):
        self.animation_frame = 2

    def __repr__(self):
        return f'Chest in room {self.room}'
