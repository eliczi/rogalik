import random
import cProfile
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
from background import BackgroundEffects

pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.display = pygame.display.set_mode(utils.world_size)
        self.screen = pygame.Surface(utils.world_size).convert()
        self.player = Player(self)
        self.clock = pygame.time.Clock()
        self.enemy_manager = EnemyManager(self)
        self.particle_manager = ParticleManager(self)
        self.menu = MainMenu(self)
        self.hud = Hud(self)
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
        self.fps = 300

    def init_all(self):
        num_of_rooms = 10
        world_width, world_height = 4, 4
        self.world = World(self, num_of_rooms, world_width, world_height)
        self.x, self.y = self.world.starting_room.x, self.world.starting_room.y
        self.room = self.world.starting_room
        self.room_image = self.room.tile_map
        self.next_room = None
        self.directions = None
        self.mini_map = MiniMap(self, world_width, world_height)
        self.background = BackgroundEffects(0, 0)

    def game_over(self):
        self.__init__()
        pygame.display.flip()
        print('----------------------')
        self.run_game()

    def update_groups(self):
        for i in range(0):
            self.particle_manager.add_fire_particles(Fire(self, i * 10, 100))
        self.enemy_manager.update_enemy_list()
        self.enemy_manager.update_enemies()
        self.player.update()
        self.particle_manager.update_particles()
        self.mini_map.set_current_room(self.room)
        self.mini_map.update()
        self.background.update()

    def draw_groups(self):
        self.background.draw(self.screen)
        #self.room_image.clear_map()
        self.room_image.draw_map(self.screen)
        for o in self.room.objects:
            o.detect_collision(self.player)
            o.update()
            #o.draw(self.room_image.map_surface)
            o.draw(self.screen)
        if self.next_room:
            self.next_room_image.clear_map()
            self.player.draw(self.next_room_image.map_surface)
        else:
            #self.player.draw(self.room_image.map_surface)
            self.player.draw(self.screen)
        self.enemy_manager.draw_enemies(self.screen)

        if self.next_room:
            self.next_room_image.draw_map(self.screen)
        self.mini_map.draw(self.screen)
        self.hud.draw()
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
            self.mini_map.draw_all(self.screen)
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
        # add_enemies(self)
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill(utils.BLACK)
            self.input()
            self.update_groups()
            self.draw_groups()
            self.next_level()
            self.game_time = pygame.time.get_ticks()
            self.display.blit(self.screen, (0, 0))
            pygame.display.flip()
        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
