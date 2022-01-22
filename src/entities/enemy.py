import pygame
import random
from map.map_generator import Room
from particles import DeathAnimation
from .entity import Entity
from bullet import Bullet
from .boss import Boss


def draw_health_bar(surf, pos, size, border_c, back_c, health_c, progress):
    pygame.draw.rect(surf, back_c, (*pos, *size))
    pygame.draw.rect(surf, border_c, (*pos, *size), 1)
    inner_pos = (pos[0] + 1, pos[1] + 1)
    inner_size = ((size[0] - 2) * progress, size[1] - 2)
    rect = (round(inner_pos[0]), round(inner_pos[1]), round(inner_size[0]), round(inner_size[1]))
    pygame.draw.rect(surf, health_c, rect)


class Enemy(Entity):
    def __init__(self, game, speed, max_hp, room, name):
        Entity.__init__(self, game, name)
        self.max_hp = max_hp  # maximum hp
        self.hp = self.max_hp  # current hp
        self.room = room  # room in which monster resides
        self.speed = random.randint(100, 150) / 10  # movement speed
        self.death_counter = 1
        self.type = None
        self.move_time = 0
        self.damage = 10
        self.cool_down = 0

    def spawn(self):
        self.rect.x = random.randint(200, 1000)
        self.rect.y = random.randint(200, 600)

    def attack(self):
        if pygame.time.get_ticks() - self.cool_down > 1000:
            self.cool_down = pygame.time.get_ticks()
            return True

    def update(self):
        self.detect_death()
        # self.move_towards_player()
        self.move()
        self.wall_collision()
        self.entity_animation.update()

    def get_move(self):
        if self.time_passed(self.move_time, 2000):
            self.move_time = pygame.time.get_ticks()
            self.speed = random.randint(100, 150) / 10
            return True

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
            self.room.enemy_list.remove(self)
            position = (self.rect.x, self.rect.y)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position))

    def time_passed(self, time, amount):
        """Wait 'amount' amount of time"""
        if pygame.time.get_ticks() - time > amount:
            return True

    def draw_health(self, surf):
        if self.hp < self.max_hp:
            health_rect = pygame.Rect(0, 0, 20, 5)
            health_rect.midbottom = self.rect.centerx, self.rect.top
            health_rect.midbottom = self.rect.centerx, self.rect.top
            draw_health_bar(surf, health_rect.topleft, health_rect.size,
                            (1, 0, 0), (255, 0, 0), (0, 255, 0), self.hp / self.max_hp)

    def draw(self):  # if current room or the next room
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        self.draw_health(self.room.tile_map.map_surface)


class Imp(Enemy):
    def __init__(self, game, speed, max_hp, room, name):
        Enemy.__init__(self, game, speed, max_hp, room, name)
        self.bullets = pygame.sprite.Group()
        self.moved = False
        self.position = [self.rect.x, self.rect.y]
        self.old_position = None
        self.destination_position = None

    def shoot(self):
        if not sum(self.velocity) and self.time_passed(self.time, 1000):
            self.time = pygame.time.get_ticks()
            self.bullets.add(
                Bullet(self, self.game, self.hitbox.midbottom[0], self.hitbox.midbottom[1],
                       self.game.player.hitbox.midbottom))

    def update(self):
        self.detect_death()
        self.shoot()
        self.move()
        self.entity_animation.update()

    def draw(self):  # if current room or the next room
        self.draw_shadow(self.room.tile_map.map_surface)
        self.room.tile_map.map_surface.blit(self.image, self.rect)
        self.draw_health(self.room.tile_map.map_surface)
        for bullet in self.bullets:
            bullet.update()
            bullet.draw()

    def move_away_from_player(self):
        distance_to_player = pygame.math.Vector2(self.game.player.hitbox.x - self.hitbox.x,
                                                 self.game.player.hitbox.y - self.hitbox.y).length()
        if self.destination_position:
            vector = pygame.math.Vector2(self.game.player.hitbox.x - self.destination_position[0],
                                         self.game.player.hitbox.y - self.destination_position[1]).length()
            if vector < 300:
                self.pick_random_spot()
        if distance_to_player < 300:
            if not self.destination_position:
                self.pick_random_spot()
            dir_vector = pygame.math.Vector2(self.destination_position[0] - self.hitbox.x,
                                             self.destination_position[1] - self.hitbox.y)
            if dir_vector.length_squared() > 0:
                dir_vector.normalize_ip()
                dir_vector.scale_to_length(self.speed / 4)
                self.set_velocity(dir_vector)
            else:
                self.pick_random_spot()
        else:
            self.set_velocity([0, 0])

    def pick_random_spot(self):
        min_x, max_x = 196, 1082
        min_y, max_y = 162, 586
        pick = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
        vector = pygame.math.Vector2(self.game.player.hitbox.x - pick[0],
                                     self.game.player.hitbox.y - pick[1])
        while vector.length() < 300:
            pick = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
            vector = pygame.math.Vector2(self.game.player.hitbox.x - pick[0],
                                         self.game.player.hitbox.y - pick[1])
        self.destination_position = pick

    def move(self):
        if not self.dead and self.hp > 0:
            self.move_away_from_player()
            self.wall_collision()
            self.rect.move_ip(self.velocity)
            self.hitbox.move_ip(self.velocity)
            self.update_hitbox()
            self.old_position = self.position
            self.position = [self.rect.x, self.rect.y]


class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemy_list = []
        self.sprites = None
        self.time = 0

    def draw_enemies(self, surface):
        for enemy in self.game.world_manager.current_room.enemy_list:
            enemy.draw()
        if self.game.world_manager.next_room:
            for enemy in self.game.world_manager.next_room.enemy_list:
                enemy.draw()

    def set_enemy_list(self):
        self.enemy_list.clear()  # unnecessary to clear and repopulate list every loop, but no better idea for now
        for enemy in self.game.world_manager.current_room.enemy_list:
            self.enemy_list.append(enemy)

    def update_enemies(self):
        self.set_enemy_list()
        for enemy in self.game.world_manager.current_room.enemy_list:
            enemy.update()
        self.debug()
        if not self.game.world_manager.switch_room:
            self.check_collide()

    def check_collide(self):
        for enemy in self.enemy_list:
            if enemy.hitbox.colliderect(
                    self.game.player.hitbox) and enemy.name != 'imp':  # and self.game.player.hurt is False:
                self.game.player.time = self.game.game_time
                self.game.player.calculate_collision(enemy)
            if (
                    self.game.player.weapon
                    and pygame.sprite.collide_mask(self.game.player.weapon, enemy)
                    and self.game.player.attacking
                    and self.game.game_time - enemy.time > 200
                    and enemy.dead is False
            ):
                enemy.time = self.game.game_time
                enemy.hurt = True
                enemy.hp -= self.game.player.weapon.damage

    def add_enemies(self):
        for row in self.game.world_manager.world.world:
            for room in row:
                if isinstance(room, Room) and room.type == 'normal':
                    self.add_normal_enemies(room)
                if isinstance(room, Room) and room.type == 'boss':
                    room.enemy_list.append(Boss(self.game, room))

    def add_normal_enemies(self, room):
        num_of_demons = random.randint(1, 4)
        num_of_imps = random.randint(0, 4)
        for _ in range(num_of_imps):
            room.enemy_list.append(Imp(self.game, random.randint(100, 150) / 10, 100, room, 'imp'))
            room.enemy_list[-1].spawn()
        for _ in range(num_of_demons):
            room.enemy_list.append(Enemy(self.game, 15, 100, room, 'demon'))
            room.enemy_list[-1].spawn()

    def debug(self):
        if pygame.mouse.get_pressed()[2] and pygame.time.get_ticks() - self.time > 100:
            self.time = pygame.time.get_ticks()
            mx, my = pygame.mouse.get_pos()
            mx -= 64  # because we are rendering player on map_surface
            my -= 32
            self.game.world_manager.current_room.enemy_list.append(
                # Enemy(self.game, random.randint(100, 150) / 10, 100, self.game.world_manager.current_room, 'demon'))
                Imp(self.game, random.randint(100, 150) / 10, 100, self.game.world_manager.current_room, 'imp'))
            self.game.world_manager.current_room.enemy_list[-1].rect.topleft = (mx, my)
