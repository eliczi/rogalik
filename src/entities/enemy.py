import pygame
import random
import typing
import time
import utils
from animation import load_animation_sprites, EntityAnimation  # entity_animation
from map_generator import Room
from particles import DeathParticle
from .entity import Entity


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
        self.speed = speed  # movement speed
        self.death_counter = 30
        self.sound = pygame.mixer.Sound('../assets/sound/hit.wav')
        self.spawn()

    def detect_collistion(self):
        pass

    def spawn(self):
        if self.game.player.direction == 'up':
            pass
        self.rect.x = random.randint(250, 600)
        self.rect.y = random.randint(250, 600)

    def update(self):
        self.collision()
        if not self.dead and self.hp > 0:
            self.move()
        self.wall_collision()
        if not self.dead and self.hp > 0:
            self.rect.move_ip(self.velocity)
            self.hitbox.move_ip(self.velocity)
        self.update_hitbox()
        self.entity_animation.update()
        self.can_move = True

    def move(self, dtick=0.06):
        if not self.dead and self.can_move:
            self.move_towards_player(self.game.player, dtick)  # zmiana

    def move_towards_player(self, player, dtick):
        # Find direction vector (dx, dy) between enemy and player.
        dir_vector = pygame.math.Vector2(player.rect.bottomleft[0] - self.rect.x,
                                         player.rect.bottomleft[1] - 50 - self.rect.y)

        self.direction = 'left' if dir_vector[0] < 0 else 'right'

        if dir_vector.length_squared() > 0:
            dir_vector.normalize()
            # Move along this normalized vector towards the player at current speed.
            dir_vector.scale_to_length(self.speed * 3 * dtick)
        self.set_velocity(dir_vector)

    def check_pair_collision(self):
        if any(self.rect.colliderect(enemy.rect) and self is not enemy for enemy in self.game.enemy_manager.enemy_list):
            self.velocity = [-x for x in self.velocity]

    def collision(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.entity_animation.animation_frame = 0
        if self.death_counter == 0:
            # pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/death.wav'))
            self.room.enemy_list.remove(self)
            position = ((self.rect.x) // 4 + 48, (self.rect.y) // 4 + 20)
            self.game.particle_manager.add_particle(DeathParticle(self.game, *position))
            del self

    def draw_health(self, surf):
        if self.hp < self.max_hp:
            health_rect = pygame.Rect(0, 0, 20, 5)
            health_rect.midbottom = self.rect.centerx, self.rect.top
            health_rect.midbottom = self.rect.centerx, self.rect.top
            draw_health_bar(surf, health_rect.topleft, health_rect.size,
                            (0, 0, 0), (255, 0, 0), (0, 255, 0), self.hp / self.max_hp)

    def draw_shadow(self, surface):  # draw shadows before self.image for all entities
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 15, 7))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1] - 20]
        surface.blit(shape_surf, position)

    def draw(self):  # if current room or the next room
        surface = self.room.tile_map.map_surface
        self.draw_shadow(surface)
        if self.room == self.game.room or self.room == self.game.next_room:
            self.draw_health(surface)
            surface.blit(self.image, self.rect)
            # pygame.draw.rect(surface, (255, 124, 32), self.rect, 2)
            # pygame.draw.rect(surface, (55, 124, 32), self.hitbox, 2)


class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemy_list = []
        self.sprites = None
        self.time = 0

    def update_enemy_list(self):
        self.enemy_list = self.game.room.enemy_list

    def draw_enemies(self):
        for enemy in self.enemy_list:
            enemy.draw()


    def update_enemies(self):
        for enemy in self.enemy_list:
            enemy.update()

    def test(self):
        self.debug()
        for enemy in self.enemy_list:
            # if 0.6 second has passed
            if pygame.sprite.collide_mask(enemy,
                                          self.game.player) and self.game.player.hurt is False and pygame.time.get_ticks():
                self.game.player.time = self.game.game_time
                self.game.player.hurt = True
                # pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/hit.wav'))
            if self.game.player.weapon:
                if pygame.sprite.collide_mask(self.game.player.weapon,
                                              enemy) and self.game.player.attacking and self.game.game_time - enemy.time > 200 and enemy.dead is False:
                    # pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/hit.wav'))
                    # self.game.fps = 30
                    # self.game.fps_counter += 1
                    enemy.time = self.game.game_time
                    enemy.hurt = True
                    enemy.hp -= self.game.player.weapon.damage

    def add_enemies(self):
        for row in self.game.world.world:
            for room in row:
                if isinstance(room, Room) and room.type == 'normal':
                    room.enemy_list.append(Enemy(self.game, 15, 100, room, 'demon'))

    def debug(self):
        if pygame.mouse.get_pressed()[2] and pygame.time.get_ticks() - self.time > 100:
            self.time = pygame.time.get_ticks()
            mx, my = pygame.mouse.get_pos()
            mx -= 64  # because we are rendering player on map_surface
            my -= 32
            self.game.room.enemy_list.append(Enemy(self.game, 15, 100, self.game.room, 'demon'))
            self.game.room.enemy_list[-1].rect.topleft = (mx, my)


def add_enemies(game):
    for row in game.world.world:
        for room in row:
            if isinstance(room, Room) and room.type == 'normal':
                room.enemy_list.append(Enemy(game, 15, 100, room, 'demon'))
                room.enemy_list.append(Enemy(game, 15, 100, room, 'demon'))
