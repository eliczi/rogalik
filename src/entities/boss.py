import pygame
import random
from utils import get_mask_rect
import utils
import os
from particles import DeathAnimation
from bullet import BossBullet
from objects.flask import Flask
from objects.coin import Coin
from entities.enemy import Enemy, draw_health_bar
from entities.animation import EntityAnimation
from entities.enemy import Enemy
from objects.hole import Hole


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


class BossAnimation(EntityAnimation):
    def __init__(self, entity):
        super().__init__(entity)

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


class Boss(Enemy):
    name = "boss"
    max_hp = 100
    hp = max_hp
    damage = 25
    bullet_damage = 15
    speed = 10

    def __init__(self, game, room):
        super().__init__(game, speed=self.speed, max_hp=self.max_hp, room=room, name=self.name)
        self.room = room
        self.image = pygame.transform.scale(pygame.image.load(f'../assets/{self.name}/idle/idle0.png'),
                                            (96, 96)).convert_alpha()
        self.rect = self.image.get_rect(center=(512, 400))
        self.rect.midbottom = (21 * 64 / 2, 7.25 * 64)
        self.bullets = pygame.sprite.Group()
        self.shooter = Shooting(self)
        self.animation_database = load_animation_sprites(f'../assets/{self.name}/')
        self.entity_animation = BossAnimation(self)
        self.items = [Flask(self.game, self.room)]
        self.add_treasure()

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((100, 100), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 30, 14))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (200, 200))
        position = [self.hitbox.bottomleft[0] + 3, self.hitbox.bottomleft[1] - 10]
        surface.blit(shape_surf, position)

    def spawn(self):
        self.rect.x = 800
        self.rect.y = 300
        # self.rect.x = random.randint(200, 1000)
        # self.rect.y = random.randint(200, 600)

    def update(self):
        self.detect_death()
        if not self.dead:
            if self.can_move:
                self.move()
            else:
                self.velocity = [0, 0]
            self.wall_collision()
        self.entity_animation.update()
        self.shooter.update()


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
            self.entity_animation.animation_frame = 0
        if self.death_counter == 0:
            self.drop_items()

            #position = self.rect.center
            #self.room.objects.append(Hole(self.game, position, self.room))

            self.room.enemy_list.remove(self)
            position = (self.rect.x - 36, self.rect.y - 64)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position, self))

    def draw(self):
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        self.shooter.draw(self.room.tile_map.map_surface)
        self.draw_health(self.room.tile_map.map_surface)

    def add_coins(self, num_of_coins):
        for _ in range(num_of_coins):
            self.items.append(Coin(self.game, self.room))

    def drop_items(self):
        for item in self.items:
            item.rect.center = self.rect.center
            item.dropped = True
            item.activate_bounce()
            item.bounce.x = self.hitbox.center[0]
            item.bounce.y = self.hitbox.center[1]
            self.room.objects.append(item)
            self.items.remove(item)


class Shooting:

    def __init__(self, boss):
        self.boss = boss
        self.bullets = self.boss.bullets
        self.shoot_time = 0
        self.machine_time = 0
        self.circle_time = 0
        self.can_move_timer = 0
        self.normal_shooting_timer = 0
        self.normal_shooting = True

    def update(self):
        self.bullets.update()
        self.moving_timer()
        self.other_timer()
        if self.boss.can_move and not self.boss.dead:
            if self.normal_shooting:
                self.shoot()
            else:
                self.machine_gun()
        else:
            self.half_circle_shoot()

    def draw(self, surface):
        self.bullets.draw(surface)


    def time_passed(self, time, amount):
        """Wait 'amount' amount of time"""
        if pygame.time.get_ticks() - time > amount:
            return True

    def moving_timer(self):
        """Wait 'amount' amount of time before moving"""
        if pygame.time.get_ticks() - self.can_move_timer > 10000:
            self.can_move_timer = pygame.time.get_ticks()
            self.boss.can_move = not self.boss.can_move

    def other_timer(self):
        if pygame.time.get_ticks() - self.normal_shooting_timer > 20000:
            self.normal_shooting_timer = pygame.time.get_ticks()
            self.normal_shooting = not self.normal_shooting

    def shoot(self):
        if self.time_passed(self.shoot_time, 1000):
            self.shoot_time = pygame.time.get_ticks()
            self.boss.game.bullet_manager.add_bullet(BossBullet(self.boss.game, self.boss, self.boss.room,
                                                       self.boss.hitbox.center[0], self.boss.hitbox.center[1],
                                                       self.boss.game.player.hitbox.center))

    def machine_gun(self):
        if self.time_passed(self.machine_time, 100):
            self.machine_time = pygame.time.get_ticks()
            self.boss.game.bullet_manager.add_bullet(BossBullet(self.boss.game, self.boss, self.boss.room,
                                                                self.boss.hitbox.center[0], self.boss.hitbox.center[1],
                                                                self.boss.game.player.hitbox.center))

    def half_circle_shoot(self):
        if self.time_passed(self.circle_time, 1000):
            self.circle_time = pygame.time.get_ticks()
            for i in range(-12, 12):
                self.boss.game.bullet_manager.add_bullet(BossBullet(self.boss.game, self.boss, self.boss.room,
                                                                    self.boss.hitbox.center[0],
                                                                    self.boss.hitbox.center[1],
                                                                    self.boss.game.player.hitbox.center,15 * i))
