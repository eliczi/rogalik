import math
import pygame
from pygame.math import Vector2
from utils import get_mask_rect
import utils
from PIL import Image
from .object import Object


class WeaponSwing:
    def __init__(self, weapon):
        self.weapon = weapon
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.counter = 0
        self.swing_side = 1
        self.hover_value = 5
        self.bottom_boundary = None
        self.top_boundary = None

    def rotate(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.weapon.player.hitbox.centerx - 64
        dy = my - self.weapon.player.hitbox.centery - 32
        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx) + 10
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) - 190

        position = self.weapon.player.hitbox.center
        self.weapon.image = pygame.transform.rotozoom(self.weapon.original_image, self.angle, 1)
        offset_rotated = self.offset.rotate(-self.angle)
        self.weapon.rect = self.weapon.image.get_rect(center=position + offset_rotated)
        self.weapon.hitbox = pygame.mask.from_surface(self.weapon.image)

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
            if self.weapon.rect.y > 300:
                self.hover_value = -5
            elif self.weapon.rect.y <= 295:
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
    def __init__(self, game, damage, name, size, room=None, position=None):
        Object.__init__(self, game, name, 'weapon', size, room, position)
        self.damage = damage
        self.size = size
        self.player = None
        self.load_image()
        if position:
            self.rect.x, self.rect.y = position[0], position[1]
        self.time = 0
        self.weapon_swing = WeaponSwing(self)
        self.update_hitbox()
        self.shadow = 0
        self.starting_position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1]]
        self.slash_image = SlashImage(self)

    def load_image(self):
        """Load weapon image and initialize instance variables"""
        self.size = tuple(3 * x for x in Image.open(f'../assets/weapon/{self.name}/{self.name}.png').size)
        self.original_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.image_picked = pygame.image.load(f'../assets/weapon/{self.name}/picked_{self.name}.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, self.size)
        self.hud_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}_hud.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.original_image, *self.rect.topleft)

    def detect_collision(self, player):
        if self.game.player.rect.colliderect(self.rect):
            self.image = self.image_picked
            self.interaction = True
        else:
            self.image = self.original_image
            self.interaction = False
            self.show_name.reset_line_length()

    def interact(self):
        self.weapon_swing.counter = 0
        self.player = self.game.player
        self.player.items.append(self)
        if not self.player.weapon:
            self.player.weapon = self
        if self.room == self.game.room:
            self.room.objects.remove(self)
        self.interaction = False
        self.show_name.reset_line_length()

    def drop(self):
        self.room = self.game.room
        self.rect.x = self.player.rect.x
        self.rect.y = self.player.rect.y
        self.player.items.remove(self)
        self.player.weapon = None
        self.game.room.objects.append(self)
        if self.player.items:
            self.player.weapon = self.player.items[-1]
        self.player = None

    def update(self):
        """Update weapon position and state"""
        self.weapon_swing.hovering()
        if self.player:
            if self.weapon_swing.counter == 10:
                self.original_image = pygame.transform.flip(self.original_image, 1, 0)
                self.player.attacking = False
                self.weapon_swing.counter = 0
            if self.player.attacking and self.weapon_swing.counter <= 10:
                self.weapon_swing.swing()
            else:
                self.weapon_swing.rotate()
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    def draw(self, surface):
        #self.slash_image.draw(surface)
        surface.blit(self.image, self.rect)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
