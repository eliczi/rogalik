import pygame
import random
import os
from src.particles import DeathAnimation
from src.bullet import BossBullet, MachineGunBullet
from src.objects.flask import RedFlask, GreenFlask
from src.objects.coin import Coin
from src.entities.animation import EntityAnimation, load_animation_sprites
from src.entities.enemy import Enemy


class Boss(Enemy):
    name = "boss"
    max_hp = 1000
    hp = max_hp
    damage = 25
    bullet_damage = 15
    speed = 14
    size = (96, 96)

    def __init__(self, game, room):
        super().__init__(game, max_hp=self.max_hp, room=room, name=self.name)
        self.room = room
        self.image = pygame.transform.scale(pygame.image.load(f'./assets/characters/{self.name}/idle/idle0.png'),
                                            self.size).convert_alpha()
        self.rect = self.image.get_rect(center=(512, 400))
        self.rect.midbottom = (21 * 64 / 2, 7.25 * 64)
        self.bullets = pygame.sprite.Group()
        self.shooter = Shooting(self)
        self.animation_database = load_animation_sprites(f'./assets/characters/{self.name}/', self.size)
        self.entity_animation = EntityAnimation(self, 8, 10)
        self.items = [RedFlask(self.game, self.room)]
        self.add_treasure()

    def spawn(self):
        self.rect.x = 800
        self.rect.y = 300

    def update(self):
        self.basic_update()
        if not self.dead and not self.game.player.dead:
            if self.can_move:
                self.move()
            else:
                self.velocity = [0, 0]
            self.wall_collision()
            self.shooter.update()
        else:
            self.velocity = [0, 0]

    def move(self):
        if not self.dead and self.hp > 0:
            self.move_towards_player()

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
            self.velocity = [0, 0]
        if self.death_counter == 0:
            self.drop_items()
            self.room.enemy_list.remove(self)
            position = (self.rect.x - 36, self.rect.y - 64)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position, self))

    def draw(self):
        self.draw_shadow(self.room.tile_map.map_surface, size=(0, 0, 30, 14), dimension=100, vertical_shift=-10,
                         horizontal_shift=3)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        self.draw_health(self.room.tile_map.map_surface)


class Shooting:

    def __init__(self, boss):
        self.boss = boss
        self.game = self.boss.game
        self.shoot_time = 0
        self.machine_time = 0
        self.circle_time = 0
        self.can_move_timer = 0
        self.normal_shooting_timer = 0
        self.normal_shooting = True
        self.circle_shooting_timer = 1000 - self.boss.game.world_manager.level * 100

    def update(self):
        self.moving_timer()
        self.other_timer()
        if self.boss.can_move and not self.boss.dead:
            if self.normal_shooting:
                self.shoot()
            else:
                self.machine_gun()
        else:
            self.half_circle_shoot()

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
            self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Impact5.wav'))
            self.boss.game.bullet_manager.add_bullet(BossBullet(self.boss.game, self.boss, self.boss.room,
                                                                self.boss.hitbox.center[0], self.boss.hitbox.center[1],
                                                                self.boss.game.player.hitbox.center))

    def machine_gun(self):
        if self.time_passed(self.machine_time, 100):
            self.machine_time = pygame.time.get_ticks()
            self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Impact5.wav'))
            self.boss.game.bullet_manager.add_bullet(MachineGunBullet(self.boss.game, self.boss, self.boss.room,
                                                                      self.boss.hitbox.center[0],
                                                                      self.boss.hitbox.center[1],
                                                                      self.boss.game.player.hitbox.center))

    def half_circle_shoot(self):
        if self.time_passed(self.circle_time, self.circle_shooting_timer):
            self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Impact1.wav'))
            self.circle_time = pygame.time.get_ticks()
            for i in range(-12, 12):
                self.boss.game.bullet_manager.add_bullet(BossBullet(self.boss.game, self.boss, self.boss.room,
                                                                    self.boss.hitbox.center[0],
                                                                    self.boss.hitbox.center[1],
                                                                    self.boss.game.player.hitbox.center, 15 * i))
