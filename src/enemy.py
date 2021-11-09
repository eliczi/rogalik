import random
import pygame
import math
import os
from map_generator import Room
from animation import load_animation_sprites, entity_animation
import typing
from particles import DeathParticle


def draw_health_bar(surf, pos, size, border_c, back_c, health_c, progress):
    pygame.draw.rect(surf, back_c, (*pos, *size))
    pygame.draw.rect(surf, border_c, (*pos, *size), 1)
    inner_pos = (pos[0] + 1, pos[1] + 1)
    inner_size = ((size[0] - 2) * progress, size[1] - 2)
    rect = (round(inner_pos[0]), round(inner_pos[1]), round(inner_size[0]), round(inner_size[1]))
    pygame.draw.rect(surf, health_c, rect)


class Enemy:
    def __init__(self, game, speed, max_hp, room):
        self.animation_database = load_animation_sprites('../assets/goblin/')
        self.game = game
        self.max_hp = max_hp
        self.room = room
        self.hp = self.max_hp

        self.image_size = (64, 64)
        self.image = pygame.transform.scale(pygame.image.load("../assets/goblin/idle/idle0.png").convert_alpha(),
                                            self.image_size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.mask.get_rect()
        self.hitbox = None  # Get rect of some size as 'image'.
        self.speed = speed
        self.velocity = [0, 0]
        self.old_velocity = [0, 0]
        self.step = 400
        self.direction = "UP"
        self.hurt = False
        self.dead = False
        self.counter = 0
        self.animation_frame = 0
        self.animation_direction = 'right'
        self.enemy_animation = entity_animation(self)
        self.counter = 0
        self.death_counter = 30
        self.spawn()

    @staticmethod
    def get_mask_rect(surf, top: int = 0, left: int = 0) -> None:
        surf_mask = pygame.mask.from_surface(surf)
        rect_list = surf_mask.get_bounding_rects()
        surf_mask_rect = rect_list[0].unionall(rect_list)
        surf_mask_rect.move_ip(top, left)
        return surf_mask_rect

    def set_side(self):
        return self.max_hp / 10

    def spawn(self):
        self.rect.x = 350
        self.rect.y = 350
        self.hitbox = self.get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox = self.hitbox

    def update(self):
        self.collision()
        if not self.dead:
            self.move()
            self.hitbox = pygame.Rect(self.rect.x + 19, self.rect.y + 26, 37, 52)
        self.enemy_animation()

    def move(self, dtick=0.06):
        self.old_velocity = self.velocity
        threshold = random.randrange(1, 20)
        if self.step >= 1:
            # self.velocity[0] = random.randint(-self.speed, self.speed) * dtick
            # self.velocity[1] = random.randint(-self.speed, self.speed) * dtick
            self.move_towards_player(self.game.player, dtick)  # zmiana
            self.step = 0
            # self.find_target(dtick, self.game.player)
        self.step += 1

    def move_towards_player(self, player, dtick):
        # Find direction vector (dx, dy) between enemy and player.
        dirvect = pygame.math.Vector2(player.rect.x - self.rect.x,
                                      player.rect.y - self.rect.y)

        self.animation_direction = 'left' if dirvect[0] < 0 else 'right'
        self.velocity = dirvect
        if dirvect.length_squared() > 0:
            dirvect.normalize()
            # Move along this normalized vector towards the player at current speed.
            dirvect.scale_to_length(self.speed * 3 * dtick)
        self.rect.move_ip(dirvect)
        self.hitbox.move_ip(dirvect)

    def find_target(self, dtick, target):
        dist_to_target_x = target.rect.x - self.rect.x
        dist_to_target_y = target.rect.x - self.rect.y

        self.velocity[0] = dist_to_target_x / self.speed * dtick * 10
        self.velocity[1] = dist_to_target_y / self.speed * dtick * 10

    def collision(self):
        if self.hp < 0 and self.animation_frame == 0:
            self.dead = True
            self.animation_frame = 0
        if self.death_counter == 0:
            self.game.enemy_list.remove(self)
            position = ((self.rect.x + 256) // 4, (self.rect.y + 1.5 * 64) // 4)
            self.game.particles.append(DeathParticle(self.game, *position))
            del self

    def draw_health(self, surf):
        if self.hp < self.max_hp:
            health_rect = pygame.Rect(0, 0, 20, 5)
            health_rect.midbottom = self.rect.centerx, self.rect.top
            draw_health_bar(surf, health_rect.topleft, health_rect.size,
                            (0, 0, 0), (255, 0, 0), (0, 255, 0), self.hp / self.max_hp)

    def draw(self):  # if current room or the next room
        if self.room == self.game.room or self.room == self.game.next_room:
            self.draw_health(self.room.room_image.map_surface)
            self.room.room_image.map_surface.blit(self.image, self.rect)


class EnemySlow(Enemy):
    def __init__(self, game, speed, max_hp, name, *groups):
        super().__init__(game, speed, max_hp, name, *groups)
        self.old_velocity = self.velocity

    def move(self, dtick):
        self.velocity[0] = random.randint(-(self.max_hp - self.hp), (self.max_hp - self.hp)) / 200
        self.velocity[1] = random.randint(-(self.max_hp - self.hp), (self.max_hp - self.hp)) / 200

    def set_side(self):
        return int(self.hp / 10)

    def update_size(self):
        pos_x = self.rect.x
        pos_y = self.rect.y
        self.image = pygame.transform.smoothscale(self.image, (self.set_side(), self.set_side()))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        self.update_size()
        self.rect.move_ip(*self.velocity)


def add_enemies(game):
    for row in game.world:
        for room in row:
            if isinstance(room, Room) and room.type == 'normal':
                room.enemy_list.append(Enemy(game, 10, 100, room))
