import pygame
import src.utils as utils
from .animation import load_animation_sprites, EntityAnimation
from src.utils import get_mask_rect
from src.particles import DeathAnimation


class Entity:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.path = f'./assets/characters/{self.name}'
        self.animation_database = load_animation_sprites(f'{self.path}/')
        self.image = pygame.transform.scale(pygame.image.load(f'{self.path}/idle/idle0.png'),
                                            utils.basic_entity_size).convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.velocity = [0, 0]
        self.hurt = False
        self.dead = False
        self.direction = 'right'
        self.can_move = True
        self.entity_animation = EntityAnimation(self)
        self.time = 0
        self.can_get_hurt = True

    def __repr(self):
        return self.name

    def __str__(self):
        return f'{id(self)}, {self.name}'

    def set_velocity(self, new_velocity):
        self.velocity = new_velocity

    def drop_items(self):
        pass

    def detect_death(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.entity_animation.animation_frame = 0
            self.can_move = False
            self.velocity = [0, 0]
        if self.death_counter == 0:
            self.drop_items()
            position = (self.rect.x, self.rect.y)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position, self))
            if self.room:
                self.room.enemy_list.remove(self)

    def basic_update(self):
        self.detect_death()
        self.update_hitbox()
        self.entity_animation.update()
        self.rect.move_ip(self.velocity)
        self.hitbox.move_ip(self.velocity)

    def wall_collision(self):
        test_rect = self.hitbox.move(*self.velocity)  # Position after moving, change name later
        collide_points = (test_rect.midbottom, test_rect.bottomleft, test_rect.bottomright)
        for wall in self.game.world_manager.current_map.wall_list:
            if any(wall.hitbox.collidepoint(point) for point in collide_points):
                self.velocity = [0, 0]

    def update_hitbox(self):
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    def moving(self):
        return self.velocity[0] != 0 or self.velocity[1] != 0

    def draw_shadow(self, surface, dimension=50, size=(0, 0, 15, 7), vertical_shift=-5, horizontal_shift=-1):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((dimension, dimension), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, size)
        shape_surf = pygame.transform.scale(shape_surf, (2 * dimension, 2 * dimension))
        position = [self.hitbox.bottomleft[0] + horizontal_shift, self.hitbox.bottomleft[1] + vertical_shift]
        surface.blit(shape_surf, position)
