import math
import pygame
from pygame.math import Vector2
from utils import get_mask_rect
import utils
from PIL import Image
from .object import Object
from particles import ParticleManager, Fire


class WeaponSwing:
    def __init__(self, weapon):
        self.weapon = weapon
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.offset_rotated = Vector2(0, -25)
        self.counter = 0
        self.swing_side = 1
        self.hover_value = 5

    def reset(self):
        self.counter = 0

    def rotate(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.weapon.player.hitbox.centerx  # - 64
        dy = my - self.weapon.player.hitbox.centery  # - 32
        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx) + 10
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) - 190

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

    def hovering(self):
        if self.weapon.player is None:
            if self.counter % 30 == 0:
                self.weapon.rect.y += self.hover_value
                self.weapon.shadow += 5 / self.hover_value
                self.weapon.up = self.hover_value < 0
            if pygame.time.get_ticks() % 1000 < 500:
                self.hover_value = -5
            elif pygame.time.get_ticks() % 1000 > 500:
                self.hover_value = 5
            self.counter += 1


class SlashImage:
    def __init__(self, weapon):
        self.weapon = weapon
        self.slash = []
        self.load_slash_images()
        self.original_slash_image = self.slash[2]
        self.slash_image = self.slash[2]
        self.slash_rect = None
        self.weapon = weapon
        self.counter = 0
        self.rotate = False

    def load_slash_images(self):
        for i in range(5):
            self.slash.append(
                pygame.transform.scale(pygame.image.load(f'../assets/vfx/slash/slash{i}.png').convert_alpha(),
                                       (int(57 * 2.5), int(32 * 2.5))))

    def rotate_slash(self, side):
        if side == -1 and self.rotate is False:
            self.rotate = True
            self.original_slash_image = pygame.transform.flip(self.original_slash_image, 1, 0)
        elif side == 1 and self.rotate is True:
            self.rotate = False
            self.original_slash_image = pygame.transform.flip(self.original_slash_image, 1, 0)

    def weapon_slash(self, side):
        self.rotate_slash(side)
        offset = Vector2(-0, -side * 70)

        self.slash_image = pygame.transform.rotozoom(self.original_slash_image,
                                                     self.weapon.weapon_swing.angle - side * 100, 1)
        offset_rotated = offset.rotate(-(self.weapon.weapon_swing.angle - 100))
        self.slash_rect = self.slash_image.get_rect(center=self.weapon.game.player.hitbox.center + offset_rotated)

    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()
        if self.weapon.player and not self.weapon.player.attacking:
            self.weapon_slash(self.weapon.weapon_swing.swing_side)
            self.counter = 0
        if self.weapon.player and self.weapon.player.attacking:
            mouse_vector = Vector2(mx - self.weapon.player.hitbox.x - 64, my - self.weapon.player.hitbox.y).normalize()
            self.slash_rect.x += mouse_vector[0] * 2
            self.slash_rect.y += mouse_vector[1] * 2
            surface.blit(self.slash_image, self.slash_rect)
            self.counter += 0.3
        if self.counter > 3:
            self.counter = 0


class Weapon(Object):
    def __init__(self, game, name=None, size=None, room=None, position=None):
        self.scale = 3
        Object.__init__(self, game, name, 'weapon', size, room, position)
        self.size = size
        self.player = None
        self.shadow = 0
        self.load_image()
        if position:
            self.rect.x, self.rect.y = position[0], position[1]
        self.time = 0
        self.weapon_swing = WeaponSwing(self)
        self.starting_position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1]]
        self.slash_image = SlashImage(self)
        self.enemy_list = []

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

    def enlarge(self):
        self.scale *= 1.01
        self.load_image()
        self.weapon_swing.offset *= 1.01

    def unlarge(self):
        self.scale /= 1.01
        self.load_image()
        self.weapon_swing.offset /= 1.01

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

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, self.shadow_width / 2 - 2, 12))
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        surface.blit(shape_surf, (self.hitbox.midbottom[0], self.hitbox.midbottom[1]))

    def draw(self):
        surface = self.room.tile_map.map_surface
        if self.player:
            surface = self.game.screen
        # self.slash_image.draw(surface)
        # self.weapon_swing.draw_shadow(surface)
        surface.blit(self.image, self.rect)
        if self.interaction:
            self.show_name.draw(surface, self.rect)


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

    def update(self):
        self.burning()
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
        # self.special_effect()

    def special_effect(self):
        print(self.enemy_list)

    def burning(self):
        x, y = self.weapon_swing.offset_rotated.xy
        x = self.rect.center[0] + x
        y = self.rect.center[1] + y
        if self.game.world_manager.switch_room is False:
            self.game.particle_manager.add_fire_particle(Fire(self.game, x / 4, y / 4))
