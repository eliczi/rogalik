import pygame
import time
import utils
from entities.enemy import add_enemies, EnemyManager
from entities.player import Player
from map_generator import World
from menu import MainMenu
from mini_map import MiniMap
from particles import ParticleManager, Fire
from hud import Hud
import random

pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.display = pygame.display.set_mode(utils.world_size)
        self.screen = None
        self.player = None
        self.clock = None
        self.enemy_manager = None
        self.particle_manager = None
        self.room = None
        self.room_image = None
        self.next_room = None
        self.next_room_image = None
        self.running = True
        self.world = None
        self.x, self.y = None, None
        self.directions = None
        self.mini_map = None
        self.game_time = None
        self.menu = MainMenu(self)
        self.fps = 60
        # self.music = pygame.mixer.music.load('../assets/sound/music.wav',)
        # pygame.mixer.music.play(-1)
        self.can_open_chest = False
        self.hud = Hud(self)
        self.fps_counter = 0
        self.draw_map = False


    def init_all(self):
        self.screen = pygame.Surface(utils.world_size)
        self.enemy_manager = EnemyManager(self)
        self.particle_manager = ParticleManager(self)
        self.player = Player(self)
        self.clock = pygame.time.Clock()
        num_of_rooms = 30
        world_width, world_height = 7,7
        self.world = World(self, num_of_rooms, world_width, world_height)
        self.x, self.y = self.world.starting_room.x, self.world.starting_room.y
        self.room = self.world.starting_room
        self.room_image = self.room.tile_map
        self.next_room = None
        self.directions = None
        self.mini_map = MiniMap(self, world_width, world_height)


    def game_over(self):
        self.init_all()
        pygame.display.flip()
        print('----------------------')
        self.run_game()

    def update_groups(self):
        self.enemy_manager.update_enemy_list()
        self.enemy_manager.test()
        self.enemy_manager.update_enemies()
        self.player.update()
        self.particle_manager.update_particles()
        self.mini_map.set_current_room(self.room)
        self.mini_map.update()

    def draw_groups(self):
        self.room_image.clear_map()
        for o in self.room.objects:
            o.detect_collision(self.player)
            o.update()
            o.draw(self.room_image.map_surface)
        if self.next_room:
            self.next_room_image.clear_map()
            self.player.draw(self.next_room_image.map_surface)
        else:
            self.player.draw(self.room_image.map_surface)

        self.enemy_manager.draw_enemies()
        self.room_image.draw_map(self.screen)
        if self.next_room:
            self.next_room_image.draw_map(self.screen)
        if not self.draw_map:
            self.mini_map.draw(self.screen)
        self.particle_manager.draw_particles(self.screen)

    def input(self):
        self.player.input()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            self.game_over()
        if pressed[pygame.K_TAB]:
            self.draw_map = True
            self.mini_map.draw_all(self.screen)
        else:
            self.draw_map = False
        if pressed[pygame.K_ESCAPE]:
            self.running = False

    def next_level(self):
        if self.directions is None:
            self.directions = self.room_image.detect_passage(self.player)
        if self.directions:
            self.player.can_move = False
            self.room_image.load_level(self, *self.directions)

    def run_game(self):
        self.init_all()
        add_enemies(self)
        while self.running:
            # self.menu.show(self.display)
            self.clock.tick(self.fps)
            self.screen.fill(utils.BLACK)
            self.input()
            self.update_groups()
            self.draw_groups()
            self.next_level()
            self.hud.draw()
            self.game_time = pygame.time.get_ticks()
            pygame.display.update()
            self.display.blit(self.screen, (0, 0))
        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
