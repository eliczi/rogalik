import pygame
from player import Player
import utils
from map import Spritesheet
from map_generator import World
from mini_map import MiniMap
from enemy import Enemy, add_enemies
from background import BackgroundCircle
from menu import MainMenu
pygame.init()
pygame.mixer.init()


class Game:
    def __init__(self):
        self.SIZE = utils.world_size
        self.display = pygame.display.set_mode(self.SIZE)
        self.screen = None
        self.counter = 0
        self.my_font = pygame.font.Font('../assets/font/Minecraft.ttf', 15)
        self.player = None
        self.clock = None
        self.enemy_list = []
        self.bullet_list = None
        self.room = None
        self.room_image = None
        self.next_room = None
        self.particles = []
        self.particle_surface = None
        self.running = True
        self.world = None
        self.x = None
        self.y = None
        self.directions = None
        self.mini_map = None
        self.next_room_image = None
        self.game_time = None
        self.particle_manager = None
        self.menu = MainMenu(self)
        self.music = pygame.mixer.music.load('../assets/sound/music.wav',)
        #pygame.mixer.music.play(-1)

    def init_all(self):
        self.bullet_list = pygame.sprite.Group()
        self.screen = pygame.Surface(self.SIZE)
        self.player = Player(self)
        self.clock = pygame.time.Clock()
        self.particle_surface = pygame.Surface((utils.world_size[0] // 4, utils.world_size[1] // 4),
                                               pygame.SRCALPHA).convert_alpha()
        num_of_rooms = 1
        world_width, world_height = 4, 4
        #self.world, start_map = map_generator(num_of_rooms, world_width, world_height, ss)
        self.world = World(num_of_rooms, world_width, world_height)
        for row in self.world.world:
            for room in row:
                if room is not None and room.type == 'starting_room':
                    self.x, self.y = room.x, room.y
                    self.room = room

        #self.x, self.y = start_map.x, start_map.y
        #self.room = self.world[start_map.x][start_map.y]
        self.room_image = self.room.tile_map
        self.next_room = None
        self.directions = None
        self.mini_map = MiniMap(world_width, world_height)

    def game_over(self):
        self.init_all()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        for e in self.enemy_list:
            e.update()
        self.player.update()
        self.bullet_list.update()

    def draw_enemies(self):
        for e in self.enemy_list:
            e.draw()

    def draw_groups(self):
        self.room_image.load_map()
        for enemy in self.enemy_list:
            enemy.draw_shadow(self.room_image.map_surface)
        if self.next_room:
            self.next_room_image.load_map()
            self.player.draw(self.next_room_image.map_surface)
        else:
            self.player.draw(self.room_image.map_surface)
        self.draw_enemies()
        for bullet in self.bullet_list:
            bullet.draw()
        self.room_image.draw_map(self.screen)

        if self.next_room:
            self.next_room_image.draw_map(self.screen)
        text_surface = self.my_font.render(self.room.type, False, (255, 255, 255))
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

    def update_particles(self):
        for particle in self.particles:
            particle.update()

    def draw_particles(self):
        for particle in self.particles:
            particle.draw()

    def next_level(self):
        if self.directions is None:
            self.directions = self.room_image.detect_passage(self.player)
        if self.directions:
            self.player.can_move = False
            self.room_image.load_level(self, *self.directions)

    def update_enemy_list(self):
        if self.next_room:
            self.enemy_list = self.next_room.enemy_list
        else:
            self.enemy_list = self.room.enemy_list

    def run_game(self):
        self.init_all()
        add_enemies(self)
        while self.running:
            #self.menu.show(self.display)
            self.clock.tick(60)
            self.screen.fill(utils.BLACK)
            self.particle_surface.fill((0, 0, 0, 0))
            self.input()
            self.update_groups()
            self.update_enemy_list()
            # for i in range(25):
            #     for y in range(20):
            #         pygame.draw.line(self.screen, (255, 255, 255), (0 + i * 64, 0), (0 + i * 64, 1600), 1)
            #         pygame.draw.line(self.screen, (255, 255, 255), (0,0 + i * 64), (1600,0 + i * 64), 1)
            for enemy in self.enemy_list:
                # if 0.6 second has passed
                if pygame.sprite.collide_mask(enemy, self.player) and self.player.hurt is False and pygame.time.get_ticks() - self.player.time > 600:
                    self.player.time = self.game_time
                    self.player.hurt = True
                    pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/hit.wav'))
                if pygame.sprite.collide_mask(self.player.weapon, enemy) and self.player.attacking and self.game_time - enemy.time > 200 and enemy.dead is False:
                    pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/hit.wav'))
                    enemy.time = self.game_time
                    enemy.hurt = True
                    enemy.hp -= self.player.weapon.damage

            self.draw_groups()
            self.update_particles()
            self.draw_particles()
            self.screen.blit(pygame.transform.scale(self.particle_surface, self.SIZE), (0, 0))
            self.next_level()
            self.mini_map.current_room(self.room)
            self.counter += 1
            self.display.blit(self.screen, (0, 0))
            #print(self.clock.get_fps())
            self.game_time = pygame.time.get_ticks()
            pygame.display.update()
        pygame.quit()
        print("Exited the game loop. Game will quit...")

        quit()
