import pygame

import utils
from animation import load_animation_sprites, EntityAnimation
from utils import get_mask_rect


class Entity:
    def __init__(self, game, name):
        self.game = game
        self.animation_database = load_animation_sprites(f'../assets/{name}/')
        self.image = pygame.transform.scale(pygame.image.load(f'../assets/{name}/idle/idle0.png').convert_alpha(),
                                            utils.basic_entity_size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(512, 400))
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.velocity = [0, 0]
        self.hurt = False
        self.dead = False
        self.direction = 'right'
        self.can_move = True
        self.entity_animation = EntityAnimation(self)
        self.counter = 0
        self.time = 0

    def set_velocity(self, new_velocity):
        self.velocity = new_velocity

    def wall_collision(self):
        """Sets player's velocity to zero if it would collide with walls
           In other words, prevents player from colliding with walls"""

        test_rect = self.hitbox.move(*self.velocity)  # Position after moving, change name later
        collide_points = (test_rect.midbottom, test_rect.bottomleft, test_rect.bottomright)
        for wall in self.game.room_image.wall_list:
            if any(wall.hitbox.collidepoint(point) for point in collide_points):
                self.velocity = [0, 0]
        for obj in self.game.room.objects:
            if any(obj.hitbox.collidepoint(point) for point in collide_points):
                self.velocity = [0, 0]


    def update_hitbox(self):
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 15, 7))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1] - 5]
        surface.blit(shape_surf, position)