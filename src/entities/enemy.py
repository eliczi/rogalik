import random
import pygame
import utils
from animation import load_animation_sprites, EntityAnimation  # entity_animation
import typing
from map_generator import Room
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
        self.animation_database = load_animation_sprites('../assets/demon/')
        self.game = game
        self.max_hp = max_hp  # maximum hp
        self.hp = self.max_hp  # current hp
        self.room = room  # room in which monster resides
        self.image = pygame.transform.scale(pygame.image.load("../assets/demon/idle/idle0.png").convert_alpha(),
                                            utils.basic_entity_size)
        self.mask = pygame.mask.from_surface(self.image)  # mask for calculating collisions
        self.rect = self.mask.get_rect()  # image rectangle, size
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)  # enemy hitbox, minimal bounding rectangle
        self.speed = speed  # movement speed
        self.velocity = [0, 0]  # displacement vector
        self.old_velocity = [0, 0]
        self.direction = "UP"
        self.hurt = False
        self.dead = False
        self.enemy_animation = EntityAnimation(self)
        self.death_counter = 30
        self.time = 0
        self.sound = pygame.mixer.Sound('../assets/sound/hit.wav')
        self.spawn()

    def spawn(self):
        self.rect.x = random.randint(250, 600)
        self.rect.y = random.randint(250, 600)

    def update_hitbox(self):
        self.hitbox = utils.get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    def update(self):
        self.collision()
        if not self.dead:
            self.move()
            self.update_hitbox()
        self.enemy_animation.update()

    def move(self, dtick=0.06):
        self.old_velocity = self.velocity
        self.move_towards_player(self.game.player, dtick)  # zmiana

    def move_towards_player(self, player, dtick):
        # Find direction vector (dx, dy) between enemy and player.
        dir_vector = pygame.math.Vector2(player.rect.bottomleft[0] - self.rect.x,
                                         player.rect.bottomleft[1] - 50 - self.rect.y)

        self.direction = 'LEFT' if dir_vector[0] < 0 else 'RIGHT'
        self.velocity = dir_vector
        if dir_vector.length_squared() > 0:
            dir_vector.normalize()
            # Move along this normalized vector towards the player at current speed.
            dir_vector.scale_to_length(self.speed * 3 * dtick)
        self.rect.move_ip(dir_vector)
        self.hitbox.move_ip(dir_vector)

    def collision(self):
        if self.hp <= 0 and self.dead is False:
            self.dead = True
            self.enemy_animation.animation_frame = 0
        if self.death_counter == 0:
            pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/death.wav'))
            self.game.enemy_list.remove(self)
            position = ((self.rect.x) // 4 + 48, (self.rect.y) // 4 + 20)
            self.game.particles.append(DeathParticle(self.game, *position))
            del self

    def draw_health(self, surf):
        if self.hp < self.max_hp:
            health_rect = pygame.Rect(0, 0, 20, 5)
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
        if self.room == self.game.room or self.room == self.game.next_room:
            self.draw_health(surface)
            surface.blit(self.image, self.rect)
            pygame.draw.rect(surface, (255, 124, 32), self.rect, 2)
            pygame.draw.rect(surface, (55, 124, 32), self.hitbox, 2)


class EnemyManager:
    def __init__(self, game):
        self.game = game

    def update_enemy_list(self):
        if self.game.next_room:
            self.game.enemy_list = self.game.next_room.enemy_list
        else:
            self.game.enemy_list = self.game.room.enemy_list


def add_enemies(game):
    for row in game.world.world:
        for room in row:
            if isinstance(room, Room) and room.type == 'normal':
                room.enemy_list.append(Enemy(game, 15, 100, room))
                room.enemy_list.append(Enemy(game, 15, 100, room))
