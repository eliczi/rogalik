import pygame
from utils import get_mask_rect
from PIL import Image
import utils


class ShowName:
    # TODO drawing animation dependent on player position
    def __init__(self, object):
        self.object = object
        self.line_length = 0
        self.time = 0
        # Format weapon display name
        self.text = self.object.name.replace("_", " ").title()
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
        if self.line_length <= self.text_length * 8 and self.time_passed(self.time, 10):
            self.time = pygame.time.get_ticks()
            self.line_length += 8
            self.counter += 1
        self.text_position = (end_position[0], end_position[1] - 20)

    def reset_line_length(self):
        self.line_length = 0
        self.counter = 0


class Object:
    def __init__(self, game, name, object_type, size, room=None, position=None):
        self.game = game
        self.room = room
        self.name = name
        self.object_type = object_type
        self.size = size
        self.original_image = None
        self.image_picked = None
        self.hud_image = None
        self.image = None
        self.load_image()
        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        if position:
            self.rect.x, self.rect.y = position[0], position[1]
        self.show_name = ShowName(self)
        self.interaction = False

    def __repr__(self):
        return self.name

    def load_image(self):
        """Load weapon image and initialize instance variables"""
        self.original_image = pygame.image.load(f'../assets/{self.object_type}/{self.name}.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, self.size)
        self.image_picked = pygame.image.load(f'../assets/{self.object_type}/{self.name}_picked.png').convert_alpha()
        self.image_picked = pygame.transform.scale(self.image_picked, self.size)
        self.hud_image = pygame.image.load(f'../assets/{self.object_type}/{self.name}_hud.png').convert_alpha()
        self.image = self.original_image

    def detect_collision(self, player):
        if self.game.player.hitbox.colliderect(self.rect):
            self.game.player.interaction = True
            self.image = self.image_picked
            self.interaction = True
        else:
            self.image = self.original_image
            self.interaction = False
            self.show_name.reset_line_length()

    def drop(self):
        self.room = self.game.room
        self.rect.x = self.game.player.rect.x
        self.rect.y = self.game.player.rect.y
        self.game.player.items.remove(self)
        self.game.player.weapon = None
        self.game.room.objects.append(self)
        if self.game.player.items:
            self.game.player.weapon = self.game.player.items[-1]

    def set_size(self, filepath):
        self.size = tuple(3 * x for x in Image.open(filepath).size)

    def update(self):
        pass

    def interact(self):
        pass

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x + 64, self.rect.y + 32))
        if self.interaction:
            self.show_name.draw(surface, self.rect)
