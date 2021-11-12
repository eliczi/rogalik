import pygame
from entities.player import Player
import utils
from map_generator import World
from mini_map import MiniMap
from entities.enemy import add_enemies, EnemyManager
from menu import MainMenu
from particles import ParticleManager

pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.display = pygame.display.set_mode(utils.world_size)
        self.screen = None
        self.player = None
        self.clock = None
        self.enemy_manager = EnemyManager(self)
        self.particle_manager = ParticleManager(self)
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
        # self.music = pygame.mixer.music.load('../assets/sound/music.wav',)
        # pygame.mixer.music.play(-1)

    def init_all(self):
        self.bullet_list = pygame.sprite.Group()
        self.screen = pygame.Surface(utils.world_size)
        self.player = Player(self)
        self.clock = pygame.time.Clock()
        num_of_rooms = 6
        world_width, world_height = 3, 3
        self.world = World(num_of_rooms, world_width, world_height)
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
        self.enemy_manager.update_enemies()
        self.player.update()

    def draw_groups(self):
        self.room_image.clear_map()
        if self.next_room:
            self.next_room_image.clear_map()
            self.player.draw(self.next_room_image.map_surface)
        else:
            self.player.draw(self.room_image.map_surface)

        self.enemy_manager.draw_enemies()
        self.room_image.draw_map(self.screen)

        if self.next_room:
            self.next_room_image.draw_map(self.screen)

        text_surface = pygame.font.Font(utils.font, 15).render(self.room.type, False, (255, 255, 255))
        self.screen.blit(text_surface, (500, 500))
        self.mini_map.draw(self.screen)

    def input(self):
        self.player.input()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            self.game_over()
        if pressed[pygame.K_TAB]:
            self.mini_map.draw(self.screen)
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
        fps = []
        while self.running:
            # self.menu.show(self.display)
            self.clock.tick(60)
            self.screen.fill(utils.BLACK)
            self.input()
            self.update_groups()
            self.draw_groups()
            self.particle_manager.update_particles()
            self.particle_manager.draw_particles()
            self.enemy_manager.test()
            self.next_level()
            self.mini_map.current_room(self.room)
            self.display.blit(self.screen, (0, 0))
            fps.append(self.clock.get_fps())
            self.game_time = pygame.time.get_ticks()
            pygame.display.update()
        print(f'Average FPS: {sum(fps) / len(fps)}')
        pygame.quit()
        print("Exited the game loop. Game will quit...")

        quit()
