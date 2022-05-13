import csv
# world_size = namedtuple('Size', ['width','length'])
import os
import pygame
import sys

from collections import namedtuple

world_size = (21 * 64, 14 * 64)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
basic_entity_size = (64, 64)
# wall_list = (135, 15, 17, 60, 61, 62, 63, 1, 18, 3, 46, 45, 40, 42, 47, 0, 30, 2, 32, 33, 3)
wall_list = (1, 2, 3, 33, 34, 35, 67, 99, 224, 227, 225, 226, 256, 257, 258, 259, 288, 289)
floor_tiles = [129, 130, 131, 161, 162, 163, 193, 194]
font = './assets/font/Minecraft.ttf'
wall_side_left, wall_side_right = 256, 257
wall_side_left_top, wall_side_right_top = 224, 225
wall_side_front_left, wall_side_front_right = 288, 289
map_center = []


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def read_csv(filename):
    mapa = []
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            mapa.append(list(row))
            mapa.append(list(row))
    return mapa


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


def time_passed(time, amount):
    if pygame.time.get_ticks() - time > amount:
        time = pygame.time.get_ticks()
        return True
