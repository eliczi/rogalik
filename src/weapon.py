import math
import pygame
from pygame.math import Vector2

from utils import get_mask_rect


class Weapon:
    def __init__(self, game, room, damage, name):
        self.game = game
        self.room = room
        self.damage = damage
        self.name = name
        self.player = None
        self.original_image = None
        self.image = None
        self.image_picked = None
        self.rect = None
        self.hitbox = None
        self.image_size = (16, 108)
        self.load_image()
        self.angle = 0
        self.offset = Vector2(0, -50)
        self.counter = 0
        self.swing_side = 1
        self.sound = True

    def load_image(self):  # Change name of the function
        """Load weapon image and initialize instance variables"""
        self.original_image = pygame.image.load(f'../assets/weapon/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (36, 90))
        self.image_picked = pygame.image.load(f'../assets/weapon/picked_{self.name}.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, (36, 90))
        self.hitbox = get_mask_rect(self.original_image, 0, 0)
        # self.hitbox = pygame.mask.from_surface(self.original_image)
        # self.rect = self.hitbox.get_rect()
        self.image = self.image_picked
        #self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 300

    def detect_collision(self, player):
        if self.game.player.hitbox.colliderect(self.rect):
            self.image = self.image_picked
        else:
            self.image = self.original_image

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

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # pygame.draw.rect(self.surface, (255, 0, 12), self.rect, 1)
        # pygame.draw.rect(self.game.screen, (255, 123, 12), self.hitbox, 2)
        # surface.blit(self.image, self.rect)

    def update(self):
        """Update weapon position and state"""
        # If player attacks with weapon, it rotates
        if self.rect.y >= 280:
            self.rect.y += 5
        elif self.rect.y < 300:
            self.rect.y -= 5
        if self.player:
            if self.counter == 10:
                self.game.player.attacking = False
                self.game.player.attacked = True
                self.counter = 0
            # Animation/mask hitbox
            if self.game.player.attacking and self.counter <= 10:
                self.swing()
            else:
                self.rotate()
                self.game.player.attacked = True

    def swing(self):
        self.angle += 20 * self.swing_side
        position = self.game.player.hitbox.center
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        offset_rotated = self.offset.rotate(-self.angle)
        self.rect = self.image.get_rect(center=position + offset_rotated)
        # self.rect_mask = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox = pygame.mask.from_surface(self.image)
        self.counter += 1
