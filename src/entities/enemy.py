import pygame
import random
from particles import DeathAnimation
from .entity import Entity
from bullet import Bullet
from objects.coin import Coin, Emerald, Ruby


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
        self.attack_cooldown = 0
        self.weapon_hurt_cooldown = 0
        self.items = []
        self.add_treasure()
        self.destination_position = None

    def add_treasure(self):
        for _ in range(random.randint(10, 20)):
            self.items.append(Coin(self.game, self.room, self))
        for _ in range(random.randint(2, 5)):
            self.items.append(Emerald(self.game, self.room, self))
        for _ in range(random.randint(0, 4)):
            self.items.append(Ruby(self.game, self.room, self))

    def drop_items(self):
        for item in self.items:
            item.rect.center = self.rect.center
            item.dropped = True
            item.activate_bounce()
            item.bounce.x = self.hitbox.center[0]
            item.bounce.y = self.hitbox.center[1]
            self.room.objects.append(item)
            self.items.remove(item)

    def spawn(self):
        self.rect.x = random.randint(200, 1000)
        self.rect.y = random.randint(200, 600)

    def can_attack(self):
        if pygame.time.get_ticks() - self.attack_cooldown > 1000:
            self.attack_cooldown = pygame.time.get_ticks()
            return True

    def can_get_hurt_from_weapon(self):
        if pygame.time.get_ticks() - self.weapon_hurt_cooldown > self.game.player.attack_cooldown:
            self.weapon_hurt_cooldown = pygame.time.get_ticks()
            return True

    def attack_player(self, player):
        if self.hitbox.colliderect(player.hitbox) and self.can_attack() and not self.game.world_manager.switch_room and not self.hurt:
            player.calculate_collision(self)
            # play attack sound

    def update(self):
        self.detect_death()
        self.change_speed()
        self.move()
        self.attack_player(self.game.player)  # enemy attacks player
        self.wall_collision()
        self.entity_animation.update()

    def change_speed(self): # changes speed every 1.5s
        if self.time_passed(self.move_time, 1500):
            self.move_time = pygame.time.get_ticks()
            self.speed = random.randint(100, 150) / 10
            return True

    def move(self):
        if not self.dead and self.hp > 0:
            if self.game.player.death_counter != 0:
                self.move_towards_player()
            else:
                self.move_away_from_player(radius=100)
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

    def move_away_from_player(self, radius):
        distance_to_player = pygame.math.Vector2(self.game.player.hitbox.x - self.hitbox.x,
                                                 self.game.player.hitbox.y - self.hitbox.y).length()
        if self.destination_position:
            vector = pygame.math.Vector2(self.game.player.hitbox.x - self.destination_position[0],
                                         self.game.player.hitbox.y - self.destination_position[1]).length()
            if vector < radius:
                self.pick_random_spot()
        if distance_to_player < radius:
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
        while vector.length() < 100:
            pick = [random.randint(min_x, max_x), random.randint(min_y, max_y)]
            vector = pygame.math.Vector2(self.game.player.hitbox.x - pick[0],
                                         self.game.player.hitbox.y - pick[1])
        self.destination_position = pick

    def detect_death(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.entity_animation.animation_frame = 0
        if self.death_counter == 0:
            self.drop_items()
            self.room.enemy_list.remove(self)
            position = (self.rect.x, self.rect.y)
            self.game.particle_manager.add_particle(DeathAnimation(self.game, *position, self))

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
        if self.image:
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
        if not sum(self.velocity) and self.time_passed(self.time, 750):
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
            bullet.draw(self.room.tile_map.map_surface)

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
