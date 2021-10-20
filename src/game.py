import pygame
from enemy import Enemy, EnemySlow
from maploader import MapLoader
from player import Player
from utils import PlayerInfo, FPSCounter
from bullet import Bullet
from item_bar import Items_bar
from particles import DeathParticle
from math import sqrt, pow
from map_generator import Room
import sys
from map import Spritesheet, TileMap, testing
import random
import csv
import copy

successes, failures = pygame.init()
print(f"Initializing pygame: {successes} successes and {failures} failures.")


class Game:
    def __init__(self):
        self.counter = 0
        self.FPS = 60
        self.SIZE = (1312, 720)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.myfont = pygame.font.Font('../assets/font/Minecraft.ttf', 15)

        self.all_enemy = None
        self.all_environment = None
        self.all_wall = None
        self.all_player = None
        self.player = None
        self.screen = None
        self.clock = None
        self.screen_rect = None
        self.fps_counter = None
        self.player_info = None
        self.wall_list = []
        self.enemy_list = []
        self.bullet_list = None
        self.weapon_group = None
        self.map = None
        self.particles = []
        self.last_shot = None
        self.items_menu = None
        self.bg = None
        self.floor = None
        self.entity_size = (64, 64)  # size of the characters(player, enemy)
        self.flame = None
        self.particle_surface = None
        self.running = True
        self.zoom_level = 1.0
        self.entrance = []

    def init_all(self):
        self.wall_list = []
        self.all_enemy = pygame.sprite.Group()
        self.all_environment = pygame.sprite.Group()
        self.all_wall = pygame.sprite.Group()
        self.all_player = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.weapon_group = pygame.sprite.Group()

        # self.screen = pygame.display.set_mode(self.SIZE, pygame.RESIZABLE)
        self.display = pygame.display.set_mode(self.SIZE)
        self.screen = pygame.Surface((self.SIZE))
        self.player = Player(self, self.all_player)
        self.clock = pygame.time.Clock()
        self.screen_rect = self.screen.get_rect()
        self.particle_surface = pygame.Surface((1200 // 4, 600 // 4), pygame.SRCALPHA).convert_alpha()

        self.fps_counter = FPSCounter(self, self.screen, self.myfont, self.clock, (150, 200))
        self.player_info = PlayerInfo(self, (800, 10))

        ss = Spritesheet('../assets/spritesheet/dungeon_.png.')
        num_of_rooms = 4
        world_width, world_height = 3, 3
        self.world = testing()  # mapa 3 na 3  z 3 pokojami

        for row in self.world:
            for room in row:
                if isinstance(room, Room):
                    room.room_image = TileMap(self, room.room_map, ss)

        for row in self.world:
            for room in row:
                if isinstance(room, Room):
                    if room.starting:
                        self.current_map = [room.x, room.y]

        self.map = self.world[self.current_map[0]][self.current_map[1]].room_image

        self.wall_list = self.map.wall_list
        self.entrance = self.map.entrance
        self.enemy_list = []

        for _ in range(1):
            self.enemy_list.append(Enemy(self, 20, 50, "Ryszard", self.all_enemy))
        for _ in range(0):
            self.enemy_list.append(Enemy(self, 50, 50, "Zbigniew", self.all_enemy))
        for _ in range(0):
            self.enemy_list.append(EnemySlow(self, 5, 1000, "Janusz", self.all_enemy))

        self.items_menu = Items_bar(self)
        self.bg = pygame.Surface((1200, 600), pygame.SRCALPHA).convert_alpha()
        self.bg.fill((0, 0, 0, 100))

    def draw_text(self, text, size, x, y):

        font = pygame.font.SysFont('Comic Sans MS', size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def collided(self, sprite, other):
        """Check if the hitbox of one sprite collides with rect of another sprite."""
        return sprite.hitbox.colliderect(other.rect)

    def game_over(self):
        self.init_all()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        self.all_enemy.update()
        self.all_environment.update()
        self.all_player.update()
        self.all_wall.update()
        self.bullet_list.update()
        self.weapon_group.update()

    def draw_groups(self):

        self.all_environment.draw(self.screen)
        self.all_enemy.draw(self.screen)
        self.all_player.draw(self.screen)
        self.weapon_group.draw(self.screen)
        self.all_wall.draw(self.screen)
        self.player.render()
        for bullet in self.bullet_list:
            bullet.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.player.direction = 'UP'
        if pressed[pygame.K_s]:
            self.player.direction = 'DOWN'
        if pressed[pygame.K_a]:
            self.player.direction = 'LEFT'
        if pressed[pygame.K_d]:
            self.player.direction = 'RIGHT'

        constant_dt = 0.06
        vel_up = [0, -self.player.speed * constant_dt]
        vel_up = [i * pressed[pygame.K_w] for i in vel_up]
        vel_down = [0, self.player.speed * constant_dt]
        vel_down = [i * pressed[pygame.K_s] for i in vel_down]
        vel_left = [-self.player.speed * constant_dt, 0]
        vel_left = [i * pressed[pygame.K_a] for i in vel_left]
        vel_right = [self.player.speed * constant_dt, 0]
        vel_right = [i * pressed[pygame.K_d] for i in vel_right]
        vel = zip(vel_up, vel_down, vel_left, vel_right)
        vel_list = [sum(item) for item in vel]

        x = sqrt(pow(vel_list[0], 2) + pow(vel_list[1], 2))

        if 0 not in vel_list:
            z = x / (abs(vel_list[0]) + abs(vel_list[1]))
            vel_list_fixed = [item * z for item in vel_list]
            self.player.set_velocity(vel_list_fixed)
        else:
            self.player.set_velocity(vel_list)

        if pygame.mouse.get_pressed()[0] and self.counter > 30:
            self.player.attacking = True
            self.player.attacked = False
            # self.player.weapon.counter = 0
            self.player.weapon.swing_side *= (-1)  # self.player.weapon.swing_side * (-1) + 1
            # bullet = Bullet(self, self.player.gun_point()[0],
            #                 self.player.gun_point()[1])  # adding bullet at the end of rifle
            # self.bullet_list.add(bullet)
            self.counter = 0
        if pressed[pygame.K_SPACE]:
            self.player.attacking = True
        if pressed[pygame.K_r]:
            self.game_over()
        if pressed[pygame.K_q]:
            self.zoom_level += 0.01
        if pressed[pygame.K_e]:
            self.zoom_level -= 0.01
        if pressed[pygame.K_F5]:
            for i in range(100):
                self.enemy_list.append(Enemy(self, 20, 50, "Ryszard", self.all_enemy))
                pos = [(random.randrange(100, 1500), random.randrange(100, 500)) for i in range(1)]
                print(pos)
                self.enemy_list[-1].rect.center = tuple(pos)

        if pressed[pygame.K_1]:
            if self.player.weapon.name != 'katana':
                self.items_menu.weapon = 'katana'
        if pressed[pygame.K_2]:
            self.weapon_group.sprites()
        if pressed[pygame.K_ESCAPE]:
            self.running = False

    def update_particles(self):
        for particle in self.particles:
            particle.update()

    def draw_particles(self):
        for particle in self.particles:
            particle.draw()

    def main_menu(self):
        pass

    def next_level(self):
        for wall in self.entrance:
            if wall.rect.collidepoint(self.player.rect.midbottom) or wall.rect.collidepoint(
                    self.player.rect.bottomleft) or wall.rect.collidepoint(self.player.rect.bottomright):
                print('hej')
                self.current_map += 1
                self.map = self.map_list[self.current_map]
                self.wall_list = self.map.wall_list
                self.entrance = self.map.entrance
                self.player.rect.center = (600, 300)

    def run_game(self):
        self.init_all()

        while self.running:
            dt = self.clock.tick(60)
            dt = dt / 400
            self.last_shot = pygame.time.get_ticks()
            self.screen.fill(self.BLACK)  # Fill the screen with background color.
            self.screen.fill((0, 0, 0))
            self.particle_surface.fill((0, 0, 0, 0))
            self.map.draw_map(self.screen)
            # self.map2.draw_map(self.screen)
            # Get the input from the player
            self.input()

            for enemy in self.enemy_list:  # Why not self.all_enemy???
                enemy.move(dt)
                for bullet in self.bullet_list:
                    bullet.collision_enemy(enemy)
                if enemy.hp > 0:
                    enemy.draw_health(self.screen)
                else:
                    enemy.kill()
                    self.enemy_list.remove(enemy)
                    self.particles.append(DeathParticle(self, *tuple(ti / 4 for ti in enemy.rect.center)))

            # Updates elements in groups, see function
            self.update_groups()
            # Detects collision of enemies and player with walls

            for enemy in self.enemy_list:
                if pygame.sprite.collide_mask(enemy, self.player):
                    self.player.hp -= 10
                if pygame.sprite.collide_mask(self.player.weapon, enemy) and self.player.attacking:
                    enemy.hurt = True
                    enemy.hp -= self.player.weapon.damage

            self.draw_groups()

            # Update and draw particles,
            self.update_particles()
            self.draw_particles()
            self.screen.blit(pygame.transform.scale(self.particle_surface, self.SIZE), (0, 0))
            self.next_level()
            self.counter += 1

            # self.screen.blit(self.bg, (0, 0))

            # przechodzenie z mapy do mapy
            # for wall in self.entrance:
            #     if self.player.hitbox.colliderect(wall.rect):
            #         self.entrance.pop()
            #         self.map = TileMap(self, '../maps/map3_Tile Layer 1.csv', self.ss)
            #         self.player.rect.y = 500
            # Screen shake
            self.fps_counter.render()
            x, y = 0, 0
            if (self.player.attacking):
                x = random.randint(-6, 6)
                y = random.randint(-6, 6)
            self.display.blit(self.screen, (x, y))
            pygame.display.update()

        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
