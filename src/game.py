import pygame
from player import Player
import utils
from map_generator import Room
from map import Spritesheet, TileMap
from map_generator import map_generator


successes, failures = pygame.init()
print(f"Initializing pygame: {successes} successes and {failures} failures.")


class Game:
    def __init__(self):
        self.counter = 0
        self.FPS = 60
        self.SIZE = utils.world_size
        self.myfont = pygame.font.Font('../assets/font/Minecraft.ttf', 15)
        self.all_enemy = None
        self.all_player = None
        self.player = None
        self.screen = None
        self.clock = None
        self.fps_counter = None
        self.player_info = None
        self.enemy_list = []
        self.bullet_list = None
        self.weapon_group = None
        self.map = None
        self.particles = []
        self.bg = None
        self.entity_size = (64, 64)  # size of the characters(player, enemy)
        self.particle_surface = None
        self.running = True

    def init_all(self):
        self.all_enemy = pygame.sprite.Group()
        self.all_player = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.weapon_group = pygame.sprite.Group()
        self.display = pygame.display.set_mode(self.SIZE)
        self.screen = pygame.Surface(self.SIZE)
        self.player = Player(self, self.all_player)
        self.clock = pygame.time.Clock()
        # self.particle_surface = pygame.Surface((1200 // 4, 600 // 4), pygame.SRCALPHA).convert_alpha()

        ss = Spritesheet('../assets/spritesheet/dungeon_.png.')
        num_of_rooms = 10
        world_width, world_height = 3, 3
        self.world, start = map_generator(num_of_rooms, world_width, world_height, ss)
        self.current_map = [start.x, start.y]


        self.map = self.world[self.current_map[0]][self.current_map[1]].room_image

        self.bg = pygame.Surface((1200, 600), pygame.SRCALPHA).convert_alpha()
        self.bg.fill((0, 0, 0, 100))

    def collided(self, sprite, other):
        """Check if the hitbox of one sprite collides with rect of another sprite."""
        return sprite.hitbox.colliderect(other.rect)

    def game_over(self):
        self.init_all()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        self.all_enemy.update()
        self.all_player.update()
        self.bullet_list.update()
        self.weapon_group.update()

    def draw_groups(self):
        self.all_enemy.draw(self.screen)
        self.all_player.draw(self.screen)
        self.weapon_group.draw(self.screen)
        self.player.render()
        for bullet in self.bullet_list:
            bullet.draw()

    def input(self):
        self.player.input()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            self.game_over()
        if pressed[pygame.K_q]:
            self.map.x -= 100
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
        self.map.next_level(self.player, self.current_map)
        self.map = self.world[self.current_map[0]][self.current_map[1]].room_image

    def run_game(self):


        self.init_all()
        while self.running:
            dt = self.clock.tick(60)
            #dt = dt / 400
            self.screen.fill(utils.BLACK)
            self.screen.fill((0, 0, 0))
            # self.particle_surface.fill((0, 0, 0, 0))
            self.map.draw_map(self.screen)
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
            # self.counter += 1

            # self.screen.blit(self.bg, (0, 0))
            x, y = 0, 0
            self.display.blit(self.screen, (0, 0))
            pygame.display.update()

        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
