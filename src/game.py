import pygame
from player import Player
import utils
from map import Spritesheet
from map_generator import map_generator
from utils import FPSCounter
from enemy import Enemy

successes, failures = pygame.init()
print(f"Initializing pygame: {successes} successes and {failures} failures.")


class Game:
    def __init__(self):
        self.counter = 0
        self.FPS = 60
        self.SIZE = utils.world_size
        self.myfont = pygame.font.Font('../assets/font/Minecraft.ttf', 15)
        self.player = None
        self.screen = None
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

    def init_all(self):
        self.bullet_list = pygame.sprite.Group()
        self.display = pygame.display.set_mode(self.SIZE)
        self.screen = pygame.Surface(self.SIZE)
        self.player = Player(self)
        self.clock = pygame.time.Clock()
        # self.particle_surface = pygame.Surface((1200 // 4, 600 // 4), pygame.SRCALPHA).convert_alpha()
        ss = Spritesheet('../assets/spritesheet/dungeon_.png.')
        num_of_rooms = 4
        world_width, world_height = 2, 2
        self.world, start_map = map_generator(num_of_rooms, world_width, world_height, ss)
        self.x, self.y = start_map.x, start_map.y
        self.room = self.world[start_map.x][start_map.y]
        self.room_image = self.room.room_image
        self.next_room = None
        self.directions = None


    def game_over(self):
        self.init_all()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        self.player.update()
        self.bullet_list.update()

    def draw_groups(self):
        self.room_image.load_map()
        if self.next_room:
            self.next_room.load_map()
            self.player.draw(self.next_room.map_surface)
        else:
            self.player.draw(self.room_image.map_surface)
        for bullet in self.bullet_list:
            bullet.draw()
        self.room_image.draw_map(self.screen)
        if self.next_room:
            self.next_room.draw_map(self.screen)

    def input(self):
        self.player.input()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            self.game_over()
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
        if self.directions is None:
            self.directions = self.room_image.detect_passage(self.player)
        if self.next_room:
            self.room_image.load_level(self, *self.directions)
        elif self.directions:
            self.player.can_move = False
            self.room_image.load_level(self, *self.directions)


    def run_game(self):
        self.init_all()
        while self.running:
            self.clock.tick(60)
            self.screen.fill(utils.BLACK)
            # self.particle_surface.fill((0, 0, 0, 0))

            self.input()
            # for enemy in self.enemy_list:  # Why not self.all_enemy???
            #     enemy.move(dt)
            #     for bullet in self.bullet_list:
            #         bullet.collision_enemy(enemy)
            #     if enemy.hp > 0:
            #         enemy.draw_health(self.screen)
            #
            #     else:
            #         enemy.kill()
            #         self.enemy_list.remove(enemy)
            #         self.particles.append(DeathParticle(self, *tuple(ti / 4 for ti in enemy.rect.center)))
            self.update_groups()
            # for enemy in self.enemy_list:
            #     if pygame.sprite.collide_mask(enemy, self.player):
            #         self.player.hp -= 10
            #     if pygame.sprite.collide_mask(self.player.weapon, enemy) and self.player.attacking:
            #         enemy.hurt = True
            #         enemy.hp -= self.player.weapon.damage
            self.draw_groups()
            # Update and draw particles,
            # self.update_particles()
            # self.draw_particles()
            # self.screen.blit(pygame.transform.scale(self.particle_surface, self.SIZE), (0, 0))

            self.next_level()
            self.counter += 1
            # pygame.draw.line(self.screen, (255, 25, 125), (0,0), (0 + self.counter * 3, 1600), 3)
            x, y = 0, 0
            self.display.blit(self.screen, (0, 0))
            pygame.display.update()

        pygame.quit()
        print("Exited the game loop. Game will quit...")

        quit()
