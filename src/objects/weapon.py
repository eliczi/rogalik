import math
import pygame
from pygame.math import Vector2

from utils import get_mask_rect
import utils
from PIL import Image


class ShowName:
    # TODO drawing animation dependent on player position
    def __init__(self, weapon):
        self.weapon = weapon
        self.line_length = 0
        self.time = 0
        # Format weapon display name
        self.text = self.weapon.name.replace("_", " ").title()
        self.text_length = len(self.text)
        self.text_position = None
        self.counter = 0
        self.drawing_speed = 10

    @staticmethod
    def time_passed(time, amount):
        """Wait 'amount' amount of time"""
        if pygame.time.get_ticks() - time > amount:
            return True

    def draw(self, surface, rect):
        self.draw_text_line(surface, rect)
        self.draw_text(surface)

    def draw_text(self, surface):
        text_surface = pygame.font.Font(utils.font, 15).render(self.text[:self.counter], True, (255, 255, 255))
        surface.blit(text_surface, self.text_position)

    def draw_text_line(self, surface, rect):
        starting_position = [rect.topleft[0], rect.topleft[1]]  # starting position of diagonal line
        for _ in range(5):  # we draw rectangles in diagonal line, so the line looks pixelated
            starting_position[0] -= 5
            starting_position[1] -= 5
            pygame.draw.rect(surface, (255, 255, 255), (starting_position[0], starting_position[1], 5, 5))

        starting_position[1] += 2  # adjustment of vertical position
        end_position = [starting_position[0] - self.line_length, starting_position[1]]
        pygame.draw.line(surface, (255, 255, 255), starting_position, end_position, 5)
        if self.line_length <= self.text_length * 8 and self.time_passed(self.time, self.drawing_speed):
            self.time = pygame.time.get_ticks()
            self.line_length += 8
            self.counter += 1
        self.text_position = (end_position[0], end_position[1] - 20)

    def reset_line_length(self):
        self.line_length = 0
        self.counter = 0


class WeaponSwing:
    def __init__(self, weapon):
        self.weapon = weapon
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.counter = 0
        self.swing_side = 1
        self.hover_value = 5

    def rotate(self):
        mx, my = pygame.mouse.get_pos()
        mx -= 64  # because we are rendering player on map_surface
        my -= 32
        dx = mx - self.weapon.player.hitbox.centerx
        dy = my - self.weapon.player.hitbox.centery
        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx) + 10
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) - 190

        position = self.weapon.player.hitbox.center
        # Rotate the image.
        self.weapon.image = pygame.transform.rotozoom(self.weapon.original_image, self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(-self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.weapon.rect = self.weapon.image.get_rect(center=position + offset_rotated)
        # Update hitbox
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


class Weapon:
    def __init__(self, game, damage, name, size, room=None, position=None):
        self.game = game
        self.damage = damage
        self.name = name
        self.size = size
        self.room = room
        self.player = None
        self.original_image = None
        self.image_picked = None
        self.hud_image = None
        self.image = None
        self.rect = None
        self.hitbox = None
        self.load_image()
        if position:
            self.rect.x, self.rect.y = position[0], position[1]
        self.interaction = False
        self.time = 0
        self.show_name = ShowName(self)
        self.weapon_swing = WeaponSwing(self)
        self.update_hitbox()
        self.shadow = 0
        self.starting_position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1]]
        self.slash = []
        self.load_slash()
        self.slash_counter = 0
        self.original_slash_image = self.slash[2]
        self.slash_image = self.slash[2]
        self.slash_rect = None
        self.dupa = None
        self.dupa_rect = None

    def load_slash(self):
        for i in range(5):
            self.slash.append(
                pygame.transform.scale(pygame.image.load(f'../assets/vfx/slash/slash{i}.png').convert_alpha(),
                                       (128, 64)))

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color,
                            (0, 0, - 2 * self.shadow + 15, - 2 * self.shadow + 7))  # - self.animation_frame % 4
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        # position = [self.hitbox.bottomleft[0] - 1, self.hitbox.bottomleft[1] - 5]
        surface.blit(shape_surf, self.starting_position)

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

    def __repr__(self):
        return self.name

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
        if not self.player:
            self.slash_rect = self.slash_image.get_rect()

    def update_hitbox(self):
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    changed = False

    def weapon_slash(self, side):
        offset = Vector2(0, side * 100)
        if self.weapon_swing.swing_side == 1:
            offset = Vector2(0, -70)
            self.slash_image = pygame.transform.rotozoom(self.original_slash_image, self.weapon_swing.angle - 100, 1)
            offset_rotated = offset.rotate(-(self.weapon_swing.angle - 100))
            self.slash_rect = self.slash_image.get_rect(center=self.game.player.hitbox.center + offset_rotated)
        elif self.weapon_swing.swing_side == -1:
            offset = Vector2(0, 70)
            self.slash_image = pygame.transform.rotozoom(self.original_slash_image, self.weapon_swing.angle + 100, 1)
            #self.slash_image = pygame.transform.flip(self.slash_image,1, 0)
            offset_rotated = offset.rotate(-(self.weapon_swing.angle - 100))
            self.slash_rect = self.slash_image.get_rect(center=self.game.player.hitbox.center + offset_rotated)

    def draw(self, surface):
        # if self.player and not self.player.attacking:
        if self.player and not self.player.attacking:
            self.weapon_slash(self.weapon_swing.swing_side)
        if self.player and self.player.attacking:
            self.dupa = self.slash_image
            self.dupa_rect = self.slash_rect
            surface.blit(self.dupa, self.dupa_rect)

        surface.blit(self.image, self.rect)
        #surface.blit(self.slash_image, self.slash_rect)
        #pygame.draw.rect(surface, (255, 255, 255), self.hitbox, 3)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
        mx, my = pygame.mouse.get_pos()
        mx -= 64  # because we are rendering player on map_surface
        my -= 32
        #pygame.draw.line(surface, (255, 255, 255), self.game.player.rect.center, (mx, my), 3)
