import math
import pygame
from pygame.math import Vector2

from utils import get_mask_rect
import utils


class ShowName:
    def __init__(self, weapon):
        self.weapon = weapon
        self.line_length = 0
        self.maximum_line_length = None
        self.time = 0
        self.text = self.weapon.name
        self.text_position = None

    @staticmethod
    def time_passed(time, amount):
        """Wait 'amount' amount of time"""
        if pygame.time.get_ticks() - time > amount:
            return True

    def draw(self, surface, rect):
        self.draw_text_line(surface, rect)
        self.draw_text(surface)

    def draw_text(self, surface):
        length = len(self.text)
        text_surface = pygame.font.Font(utils.font, 15).render(self.text, False, (255, 255, 255))
        surface.blit(text_surface, self.text_position)

    def draw_text_line(self, surface, rect):
        starting_position = [rect.topleft[0], rect.topleft[1]]  # starting position of diagonal line
        for _ in range(5):  # we draw rectangle in diagonal line, so the line looks pixelated
            starting_position[0] -= 5
            starting_position[1] -= 5
            pygame.draw.rect(surface, (255, 255, 255), (starting_position[0], starting_position[1], 5, 5))

        starting_position[1] += 2  # adjustment of vertical position
        end_position = [starting_position[0] - self.line_length, starting_position[1]]
        pygame.draw.line(surface, (255, 255, 255), starting_position, end_position, 5)
        if self.line_length <= 65 and self.time_passed(self.time, 60):
            self.time = pygame.time.get_ticks()
            self.line_length += 15
        self.text_position = (end_position[0], end_position[1] - 20)

    def reset_line_length(self):
        self.line_length = 0


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
        self.image_size = (16, 108)
        self.text_bottom = None
        self.load_image()
        if position:
            self.rect.x, self.rect.y = position[0], position[1]
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.counter = 0
        self.swing_side = 1
        self.sound = True
        self.value = 2
        self.counter = 0
        self.states = ('not_picked', 'picked', 'hovering')
        # self.state = namedtuple('State', ['picked', 'not_picked', 'hovering'])
        self.interaction = False
        self.time = 0
        self.show_name = ShowName(self)

    def load_image(self):  # Change name of the function
        """Load weapon image and initialize instance variables"""
        self.original_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.image_picked = pygame.image.load(f'../assets/weapon/{self.name}/picked_{self.name}.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, self.size)
        self.hud_image = pygame.image.load(f'../assets/weapon/{self.name}/{self.name}_hud.png').convert_alpha()
        self.text_bottom = pygame.image.load(f'../assets/weapon/text_bottom.png').convert_alpha()
        self.hitbox = get_mask_rect(self.original_image, 0, 0)
        # self.hitbox = pygame.mask.from_surface(self.original_image)
        # self.rect = self.hitbox.get_rect()
        self.image = self.image_picked
        # self.image = self.original_image
        self.rect = self.image.get_rect()

    def detect_collision(self, player):
        if self.game.player.hitbox.colliderect(self.rect):
            self.image = self.image_picked
            self.interaction = True
        else:
            self.image = self.original_image
            self.interaction = False
            self.show_name.reset_line_length()

    def rotate(self):
        mx, my = pygame.mouse.get_pos()
        mx -= 256  # because we are rendering player on map_surface
        my -= 128
        dx = mx - self.game.player.hitbox.centerx
        dy = my - self.game.player.hitbox.centery
        if self.swing_side == 1:
            self.angle = (180 / math.pi) * math.atan2(-self.swing_side * dy, dx)
        else:
            self.angle = (180 / math.pi) * math.atan2(self.swing_side * dy, dx) - 200

        position = self.game.player.hitbox.center
        # Rotate the image.
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        # Rotate the offset vector.
        offset_rotated = self.offset.rotate(-self.angle)
        # Create a new rect with the center of the sprite + the offset.
        self.rect = self.image.get_rect(center=position + offset_rotated)
        # Update hitbox
        # self.hitbox = pygame.mask.from_surface(self.image)

    @staticmethod
    def time_passed(time, amount):
        """Wait 'amount' amount of time"""
        if pygame.time.get_ticks() - time > amount:
            return True

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
            # self.show_name.draw_text_line(surface, self.rect)
            # position = (self.rect.topleft[0], self.rect.topleft[1])
            # text_positoin = (self.rect.topleft[0] - 64, self.rect.topleft[1] - 45)
            # surface.blit(self.text_surface, text_positoin)
            # surface.blit(self.text_bottom, position)
        # pygame.draw.rect(self.surface, (255, 0, 12), self.rect, 1)
        # pygame.draw.rect(self.game.screen, (255, 123, 12), self.hitbox, 2)
        # surface.blit(self.image, self.rect)

    def interact(self):
        self.counter = 0
        self.player = self.game.player
        self.player.items.append(self)
        if self.player.weapon is None:
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

    def hovering(self):
        if self.player is None:
            if self.counter % 30 == 0:
                self.rect.y += self.value
            if self.rect.y >= 305:
                self.value = -5
            elif self.rect.y < 295:
                self.value = 5
            self.counter += 1

    def update(self):
        """Update weapon position and state"""
        self.hovering()
        if self.player:
            if self.counter == 10:
                self.player.attacking = False
                self.counter = 0
            # Animation/mask hitbox
            if self.player.attacking and self.counter <= 10:
                self.swing()
            else:
                self.rotate()

    def swing(self):
        self.angle += 20 * self.swing_side
        position = self.player.hitbox.center
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        offset_rotated = self.offset.rotate(-self.angle)
        self.rect = self.image.get_rect(center=position + offset_rotated)
        # self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox = pygame.mask.from_surface(self.image)
        self.counter += 1

    def __repr__(self):
        return self.name
