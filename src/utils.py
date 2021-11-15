import csv
# world_size = namedtuple('Size', ['width','length'])
import os
import pygame
from collections import namedtuple

world_size = (21 * 64, 14 * 64)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
basic_entity_size = (64, 64)
# wall_list = (135, 15, 17, 60, 61, 62, 63, 1, 18, 3, 46, 45, 40, 42, 47, 0, 30, 2, 32, 33, 3)
wall_list = (1, 2, 3,33, 34, 35,67, 99, 224,227, 225,226, 256, 257, 258, 259, 288, 289)
floor_tiles = (129, 130, 132,161, 162, 163, 193, 194)
font = '../assets/font/Minecraft.ttf'
wall_side_left, wall_side_right = 256, 257
wall_side_left_top, wall_side_right_top = 224, 225
wall_side_front_left, wall_side_front_right = 288, 289


def read_csv(filename):
    mapa = []
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            mapa.append(list(row))
            mapa.append(list(row))
    return mapa


def collided(sprite, other):
    """Check if the hitbox of one sprite collides with rect of another sprite."""
    return sprite.hitbox.colliderect(other.rect)


def draw_text(self, text, size, x, y):
    font_main = pygame.font.SysFont('Comic Sans MS', size)
    text_surface = font_main.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    self.screen.blit(text_surface, text_rect)


def collided2(sprite, other):
    """Check if the hitbox of one sprite collides with rect of another sprite."""
    return sprite.hitbox.colliderect(other.hitbox)


def get_mask_rect(surf, top=0, left=0):
    """Returns minimal bounding rectangle of an image"""
    surf_mask = pygame.mask.from_surface(surf)
    rect_list = surf_mask.get_bounding_rects()
    if rect_list:
        surf_mask_rect = rect_list[0].unionall(rect_list)
        surf_mask_rect.move_ip(top, left)
        return surf_mask_rect


def wait(mil_sec, game):
    ticks = mil_sec / 16
    if game.counter == game.counter + ticks:
        return True


class PlayerInfo:
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        self.coordinates = None
        self.space_between = 20

        self.hp_text = None
        self.enemy_count_text = None
        self.weapon_text = None
        self.damage_text = None
        self.stamina_text = None
        self.time_text = None

        self.hp_text_rect = None
        self.stamina_text_rect = None
        self.weapon_text_rect = None
        self.damage_text_rect = None
        self.time_text_rect = None
        self.enemy_count_text_rect = None
        self.score_img = pygame.image.load('../assets/score.png')
        self.score_img = pygame.transform.scale(self.score_img, (200, 100))

    def render(self):
        """

        :return:
        :rtype:
        """
        self.game.screen.blit(self.score_img, (0, 0))
        self.game.screen.blit(self.coordinates, (25, 25))
        self.game.screen.blit(self.hp_text, self.hp_text_rect)
        self.game.screen.blit(self.weapon_text, self.weapon_text_rect)
        self.game.screen.blit(self.damage_text, self.damage_text_rect)
        self.game.screen.blit(self.stamina_text, self.stamina_text_rect)
        self.game.screen.blit(self.time_text, self.time_text_rect)
        self.game.screen.blit(self.enemy_count_text, self.enemy_count_text_rect)

    def update(self):
        """

        :return:
        :rtype:
        """
        self.coordinates = self.game.my_font.render('SCORE: ' + str(self.game.player.score), False, (255, 255, 255))
        self.hp_text = self.game.my_font.render("HP: " + str(self.game.player.hp),
                                                False, self.game.GREEN)
        self.weapon_text = self.game.my_font.render("Weapon: " + str(self.game.player.weapon.name),
                                                    False, self.game.GREEN)
        self.damage_text = self.game.my_font.render("Damage: " + str(self.game.player.weapon.damage),
                                                    False, self.game.GREEN)
        self.stamina_text = self.game.my_font.render("Stamina: " + str(self.game.player.current_stamina),
                                                     False, self.game.GREEN)
        self.time_text = self.game.my_font.render("Time: " + f"{round(self.game.last_shot / 1000, 1)}s",
                                                  False, self.game.GREEN)
        self.enemy_count_text = self.game.my_font.render("Enemy count: " + str(len(self.game.all_enemy)),
                                                         False, self.game.GREEN)

        self.hp_text_rect = self.weapon_text.get_rect(center=(self.pos[0], self.pos[1]))
        self.stamina_text_rect = self.weapon_text.get_rect(center=(self.pos[0], self.pos[1] + self.space_between))
        self.weapon_text_rect = self.weapon_text.get_rect(center=(self.pos[0], self.pos[1] + 2 * self.space_between))
        self.damage_text_rect = self.weapon_text.get_rect(center=(self.pos[0], self.pos[1] + 3 * self.space_between))
        self.time_text_rect = self.time_text.get_rect(center=(self.pos[0], self.pos[1] + 4 * self.space_between))
        self.enemy_count_text_rect = self.enemy_count_text.get_rect(
            center=(self.pos[0], self.pos[1] + 5 * self.space_between))


class FPSCounter:
    def __init__(self, game, surface, font_main, clock, pos):
        self.game = game
        self.surface = surface
        self.font = font_main
        self.clock = clock
        self.pos = pos
        self.fps_text = self.font.render(str(self.game.clock.get_fps()) + "FPS", False, (0, 0, 0))
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))

    def render(self):
        """

        :return:
        :rtype:
        """
        self.surface.blit(self.fps_text, self.fps_text_rect)

    def update(self):
        """

        :return:
        :rtype:
        """
        text = f"{self.game.clock.get_fps():2.0f} FPS"
        self.fps_text = self.font.render(text, False, WHITE)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))
