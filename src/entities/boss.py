import pygame
import random
from utils import get_mask_rect
import utils
import os
from particles import DeathAnimation
from bullet import Bullet


def load_animation_sprites(path):
    """Loads animation frames(.png files) from specified directory to a dictionary"""

    animation_data = {"IDLE": [], "WALK": [], "RUN": [], 'HURT': [], 'DEAD': []}
    animation_states = os.listdir(path)  # Lists all the subdirectories in specified path
    for state in animation_states:
        sub_states = os.listdir(path + state)
        for sub_state in sub_states:
            key = state.upper()  # key to dictionary
            animation_image = pygame.image.load(path + state + '/' + sub_state).convert_alpha()
            animation_image = pygame.transform.scale(animation_image, (96, 96))
            animation_data[key].append(animation_image)
    return animation_data


class BossAnimation:
    def __init__(self, entity):
        self.entity = entity
        self.animation_direction = 'right'
        self.animation_frame = 0

    def moving(self) -> bool:
        """s"""
        return bool(sum(self.entity.velocity))

    def get_direction(self):
        self.animation_direction = 'right' if self.entity.velocity[0] <= 0 else 'left'

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
        self.animation_frame += 1.0 / 10
        if self.animation_frame >= 8:
            self.entity.death_counter = 0
        state = 'HURT' if self.animation_frame < 1 else 'DEAD'
        if self.animation_frame <= 8:
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


class Boss:
    def __init__(self, game, room):
        self.game = game
        self.room = room
        self.name = 'boss'
        self.animation_database = load_animation_sprites(f'../assets/{self.name}/')
        self.image = pygame.transform.scale(pygame.image.load(f'../assets/{self.name}/idle/idle0.png'),
                                            (96, 96)).convert_alpha()
        self.rect = self.image.get_rect(center=(512, 400))
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.boss_animation = BossAnimation(self)
        self.velocity = [0, 0]
        self.hurt = False
        self.dead = False
        self.direction = 'right'
        self.can_move = True
        self.counter = 0
        self.time = 0
        self.speed = 10
        self.death_counter = 15
        self.hp = 100
        self.bullets = pygame.sprite.Group()
        self.cool_down = 0

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((100, 100), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 30, 14))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (200, 200))
        position = [self.hitbox.bottomleft[0] + 3, self.hitbox.bottomleft[1] - 10]
        surface.blit(shape_surf, position)

    def set_velocity(self, new_velocity):
        self.velocity = new_velocity

    def attack(self):
        if pygame.time.get_ticks() - self.cool_down > 1000:
            self.cool_down = pygame.time.get_ticks()
            return True

    def wall_collision(self):
        test_rect = self.hitbox.move(*self.velocity)  # Position after moving, change name later
        collide_points = (test_rect.midbottom, test_rect.bottomleft, test_rect.bottomright)
        for wall in self.game.world_manager.current_map.wall_list:
            if any(wall.hitbox.collidepoint(point) for point in collide_points):
                self.velocity = [0, 0]

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    def spawn(self):
        self.rect.x = 800
        self.rect.y = 300
        # self.rect.x = random.randint(200, 1000)
        # self.rect.y = random.randint(200, 600)

    def update(self):
        self.detect_death()
        self.move()
        self.shoot()
        self.wall_collision()
        self.boss_animation.update()

    def move(self):
        if not self.dead and self.hp > 0:
            self.move_towards_player()
            self.rect.move_ip(self.velocity)
            self.hitbox.move_ip(self.velocity)
            self.update_hitbox()

    def move_towards_player(self):
        dir_vector = pygame.math.Vector2(self.game.player.hitbox.x - self.hitbox.x,
                                         self.game.player.hitbox.y - self.hitbox.y)
        if dir_vector.length_squared() > 0:  # cant normalize vector of length 0
            dir_vector.normalize_ip()
            dir_vector.scale_to_length(self.speed / 4)
        self.set_velocity(dir_vector)

    def detect_death(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.boss_animation.animation_frame = 0
        if self.death_counter == 0:
            self.room.enemy_list.remove(self)
            position = (self.rect.x, self.rect.y)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position, entity='boss'))

    def time_passed(self, time, amount):
        """Wait 'amount' amount of time"""
        if pygame.time.get_ticks() - time > amount:
            return True

    def shoot(self):
        if self.time_passed(self.time, 1000):
            self.time = pygame.time.get_ticks()
            self.bullets.add(
                Bullet(self, self.game, self.hitbox.center[0], self.hitbox.center[1], self.game.player.hitbox.center,
                       'boss'))

    def half_circle_shoot(self):
        

    def draw(self):
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.update()
            bullet.draw()
