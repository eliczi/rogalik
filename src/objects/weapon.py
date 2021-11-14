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
        if self.line_length <= self.text_length * 8 and self.time_passed(self.time, 40):
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
        mx -= 128  # because we are rendering player on map_surface
        my -= 64
        dx = mx - self.weapon.player.hitbox.centerx
        dy = my - self.weapon.player.hitbox.centery

        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx)
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) - 200

        position = self.weapon.player.hitbox.center
        # Rotate the image.
        self.weapon.image = pygame.transform.rotozoom(self.weapon.original_image, self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(-self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.weapon.rect = self.weapon.image.get_rect(center=position + offset_rotated)
        # Update hitbox
        # self.hitbox = pygame.mask.from_surface(self.image)

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
            if self.weapon.rect.y >= 300:
                self.hover_value = -5
            elif self.weapon.rect.y < 295:
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

    def load_image(self):
        """Load weapon image and initialize instance variables"""
        self.size = tuple(3 * x for x in Image.open(f'../assets/weapon/{self.name}/{self.name}.png').size)
        self.original_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.image_picked = pygame.image.load(f'../assets/weapon/{self.name}/picked_{self.name}.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, self.size)
        self.hud_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}_hud.png').convert_alpha()
        self.hitbox = get_mask_rect(self.original_image, 0, 0)
        self.image = self.original_image
        self.rect = self.image.get_rect()

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
