import pygame
import utils
from entities.enemy import add_enemies, EnemyManager
from entities.player import Player
from map.map_generator import World
from menu import MainMenu
from mini_map import MiniMap
from particles import ParticleManager
from hud import Hud
from background import BackgroundEffects
from map.world_manager import WorldManager

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
        self.world_manager = WorldManager(self)
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
        self.fps = 60
        self.background = BackgroundEffects()

    def game_over(self):
        self.__init__()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        self.enemy_manager.update_enemy_list()
        self.enemy_manager.update_enemies()
        self.player.update()
        self.particle_manager.update_particles()
        #self.mini_map.set_current_room(self.world_manager.current_room)
        #self.mini_map.update()
        self.background.update()
        self.world_manager.update()

    def draw_groups(self):
        self.background.draw(self.screen)
        self.world_manager.draw_map(self.screen)
        self.player.draw(self.screen)
        self.enemy_manager.draw_enemies(self.screen)
        #self.mini_map.draw(self.screen)
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
        if pressed[pygame.K_f]:
            print(self.world_manager.direction, self.world_manager.switch_room)

    def run_game(self):  # sourcery skip: extract-method
        add_enemies(self)
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill(utils.BLACK)
            self.input()
            self.update_groups()
            self.draw_groups()
            self.game_time = pygame.time.get_ticks()
            pygame.draw.line(self.screen, (255, 255,255), (utils.world_size[0]/2, 0),(utils.world_size[0]/2, utils.world_size[1]), 2)
            pygame.draw.line(self.screen, (255, 255,255), (0,utils.world_size[1]/2),(utils.world_size[0], utils.world_size[1]/2), 2)
            self.display.blit(self.screen, (0, 0))
            pygame.display.flip()
        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
