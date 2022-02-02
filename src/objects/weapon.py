import math
import pygame
from pygame.math import Vector2
from utils import get_mask_rect
import utils
from PIL import Image
from .object import Object
from particles import ParticleManager, Fire


class WeaponSwing:
    left_swing = 10
    right_swing = -190

    def __init__(self, weapon):
        self.weapon = weapon
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.offset_rotated = Vector2(0, -25)
        self.counter = 0
        self.swing_side = 1
        self.hover_value = 5
        self.up = False
        self.shadow_width = self.weapon.hitbox.width
        self.shadow_position = pygame.Rect(0, 0, 0, 0)

    def reset(self):
        self.counter = 0

    def rotate(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.weapon.player.hitbox.centerx  # - 64
        dy = my - self.weapon.player.hitbox.centery  # - 32
        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx) + self.left_swing
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) + self.right_swing

        position = self.weapon.player.hitbox.center
        self.weapon.image = pygame.transform.rotozoom(self.weapon.original_image, self.angle, 1)
        offset_rotated = self.offset.rotate(-self.angle)
        self.weapon.rect = self.weapon.image.get_rect(center=position + offset_rotated)
        self.weapon.hitbox = pygame.mask.from_surface(self.weapon.image)
        self.offset_rotated = Vector2(0, -35).rotate(-self.angle)

    def swing(self):
        self.angle += 20 * self.swing_side
        position = self.weapon.player.hitbox.center
        self.weapon.image = pygame.transform.rotozoom(self.weapon.original_image, self.angle, 1)
        offset_rotated = self.offset.rotate(-self.angle)
        self.weapon.rect = self.weapon.image.get_rect(center=position + offset_rotated)
        # self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        self.weapon.hitbox = pygame.mask.from_surface(self.weapon.image)
        self.counter += 1

    def update_shadow_position(self):
        self.shadow_position = [self.weapon.rect.midbottom[0] - 14, self.weapon.rect.midbottom[1]]
        if not self.up:
            self.shadow_position = [self.weapon.rect.midbottom[0] - 18, self.weapon.rect.midbottom[1] - 5]

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        if self.up:
            pygame.draw.ellipse(shape_surf, color, (0, 0, self.shadow_width / 2, 10))
        else:
            pygame.draw.ellipse(shape_surf, color, (0, 0, self.shadow_width / 2 + 4, 12))
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        self.shadow_position.center = self.weapon.rect.midbottom
        surface.blit(shape_surf, self.shadow_position)

    def hovering(self):
        # self.update_shadow_position()
        if self.weapon.player is None:
            if self.counter % 30 == 0:
                self.weapon.rect.y += self.hover_value
                self.up = self.hover_value < 0
            if pygame.time.get_ticks() % 1000 < 500:
                self.hover_value = -5
            elif pygame.time.get_ticks() % 1000 > 500:
                self.hover_value = 5
            self.counter += 1


class Weapon(Object):
    def __init__(self, game, name=None, size=None, room=None, position=None):
        self.scale = 3
        Object.__init__(self, game, name, 'weapon', size, room, position)
        self.size = size
        self.player = None
        self.load_image()
        if position:
            self.rect.x, self.rect.y = position[0], position[1]
        self.time = 0
        self.weapon_swing = WeaponSwing(self)
        self.starting_position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1]]
        # self.slash_image = SlashImage(self)
        self.up = False

    def load_image(self):
        """Load weapon image and initialize instance variables"""
        self.size = tuple(self.scale * x for x in Image.open(f'../assets/weapon/{self.name}/{self.name}.png').size)
        self.original_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.image_picked = pygame.image.load(f'../assets/weapon/{self.name}/picked_{self.name}.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, self.size)
        self.hud_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}_hud.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.original_image, *self.rect.topleft)

    def detect_collision(self):
        if self.game.player.hitbox.colliderect(self.rect):
            self.image = self.image_picked
            self.interaction = True
        else:
            self.image = self.original_image
            self.interaction = False
            self.show_name.reset_line_length()

    def interact(self):
        self.weapon_swing.reset()
        self.player = self.game.player
        self.player.items.append(self)
        if not self.player.weapon:
            self.player.weapon = self
        if self.room == self.game.world_manager.current_room:
            self.room.objects.remove(self)
        self.interaction = False
        self.show_name.reset_line_length()

    def drop(self):
        self.room = self.game.world_manager.current_room
        self.player.items.remove(self)
        self.player.weapon = None
        self.game.world_manager.current_room.objects.append(self)
        if self.player.items:
            self.player.weapon = self.player.items[-1]
        self.load_image()
        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.rect.x = self.player.rect.x
        self.rect.y = self.player.rect.y
        self.player = None
        self.weapon_swing.offset_rotated = Vector2(0, -25)

    def update(self):
        self.weapon_swing.hovering()
        self.show_price.update()
        if self.player:
            self.interaction = False
            if self.weapon_swing.counter == 10:
                self.original_image = pygame.transform.flip(self.original_image, 1, 0)
                self.player.attacking = False
                self.weapon_swing.counter = 0
            if self.player.attacking and self.weapon_swing.counter <= 10:
                self.weapon_swing.swing()
            else:
                self.weapon_swing.rotate()
        self.update_bounce()
        self.update_hitbox()

    def draw(self):
        surface = self.room.tile_map.map_surface
        if self.player:
            surface = self.game.screen
        else:
            self.weapon_swing.draw_shadow(surface)
        surface.blit(self.image, self.rect)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
        self.show_price.draw(surface)


class Staff(Weapon):
    name = 'staff'
    damage = 10
    size = (30, 96)

    def __init__(self, game, room=None, position=None):
        super().__init__(game, self.name, self.size, room, position)
        self.value = 150


class AnimeSword(Weapon):
    name = 'anime_sword'
    damage = 40
    size = (36, 90)

    def __init__(self, game, room=None, position=None):
        super().__init__(game, self.name, self.size, room, position)
        self.value = 100


class FireSword(Weapon):
    name = 'fire_sword'
    damage = 30
    size = (36, 90)

    def __init__(self, game, room=None, position=None):
        super().__init__(game, self.name, self.size, room, position)
        self.value = 150
        self.burning_enemies = []

    class Burn:
        def __init__(self, game, enemy, weapon):
            self.game = game
            self.enemy = enemy
            self.weapon = weapon
            self.counter = 0
            self.tick = 0

        def get_enemy(self):
            return self.enemy

        def update(self):
            if self.tick == 30 and self.counter < 5:
                self.enemy.hp -= 5
                self.tick = 0
                self.counter += 1
            self.tick += 1
            if self.counter == 5:
                self.unburn()

        def unburn(self):
            self.weapon.burning_enemies.remove(self)

        def draw(self):
            self.game.particle_manager.add_fire_particle(
                Fire(self.game, self.enemy.rect.center[0] / 4, self.enemy.rect.center[1] / 4, 'enemy'))

    def special_effect(self, enemy):
        self.burning_enemies.append(self.Burn(self.game, enemy, self))

    def update(self):
        self.burning()
        self.show_price.update()
        self.weapon_swing.hovering()
        if self.player:
            self.interaction = False
            if self.weapon_swing.counter == 10:
                self.original_image = pygame.transform.flip(self.original_image, 1, 0)
                self.player.attacking = False
                self.weapon_swing.counter = 0
            if self.player.attacking and self.weapon_swing.counter <= 10:
                self.weapon_swing.swing()
            else:
                self.weapon_swing.rotate()
        self.update_hitbox()
        for e in self.burning_enemies:
            e.update()
            e.draw()

    def burning(self):
        x, y = self.weapon_swing.offset_rotated.xy
        x = self.rect.center[0] + x
        y = self.rect.center[1] + y
        if self.game.world_manager.switch_room is False:
            self.game.particle_manager.add_fire_particle(Fire(self.game, x / 4, y / 4))
