import pygame
import utils
from entities.enemy import EnemyManager
from entities.player import Player
from map.map_generator import World
from menu import MainMenu
from mini_map import MiniMap
from particles import ParticleManager
from hud import Hud
from background import BackgroundEffects
from map.world_manager import WorldManager
from objects.object_manager import ObjectManager
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
        self.object_manager = ObjectManager(self)
        self.menu = MainMenu(self)
        self.hud = Hud(self)
        self.running = True
        self.mini_map = None
        self.game_time = None
        self.fps = 60
        self.background = BackgroundEffects()

    def game_over(self):
        self.__init__()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        self.enemy_manager.update_enemies()
        self.player.update()
        self.particle_manager.update_particles()
        #self.mini_map.set_current_room(self.world_manager.current_room)
        #self.mini_map.update()
        self.background.update()
        self.object_manager.update()
        self.world_manager.update()

    def draw_groups(self):
        self.background.draw(self.screen)
        self.world_manager.draw_map(self.screen)
        self.object_manager.draw()
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

    def run_game(self):  # sourcery skip: extract-method
        self.enemy_manager.add_enemies()
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill(utils.BLACK)
            self.input()
            self.update_groups()
            self.draw_groups()
            self.game_time = pygame.time.get_ticks()
            self.display.blit(self.screen, (0, 0))
            pygame.display.flip()
        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
