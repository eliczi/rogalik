import pygame
from player import Player
import utils
from map import Spritesheet, get_map
from map_generator import map_generator

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
        self.map = None
        self.map2 = None
        self.particles = []
        self.particle_surface = None
        self.running = True
        self.world = None
        self.current_map = None

    def init_all(self):
        self.bullet_list = pygame.sprite.Group()
        self.display = pygame.display.set_mode(self.SIZE)
        self.screen = pygame.Surface(self.SIZE)
        self.player = Player(self)
        self.clock = pygame.time.Clock()
        # self.particle_surface = pygame.Surface((1200 // 4, 600 // 4), pygame.SRCALPHA).convert_alpha()

        ss = Spritesheet('../assets/spritesheet/dungeon_.png.')
        num_of_rooms = 2
        world_width, world_height = 2, 1
        self.world, start_map = map_generator(num_of_rooms, world_width, world_height, ss)
        self.current_map = [start_map.x, start_map.y]
        #self.map = get_map(self.world, self.current_map).room_image
        self.map = self.world[start_map.x][start_map.y].room_image


    def collided(self, sprite, other):
        """Check if the hitbox of one sprite collides with rect of another sprite."""
        return sprite.hitbox.colliderect(other.rect)

    def game_over(self):
        self.init_all()
        pygame.display.flip()
        self.run_game()

    def update_groups(self):
        self.player.update()
        self.bullet_list.update()

    def draw_groups(self):
        self.map.load_map()
        self.player.draw(self.map.map_surface)
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
        if self.map.x == 0 and self.map.y == 0:
            self.player.can_move = True
        self.map.next_level(self,self.player, self.current_map, self.world)
        self.map = self.world[self.current_map[0]][self.current_map[1]].room_image


    def run_game(self):
        self.init_all()
        while self.running:
            self.clock.tick(60)
            self.screen.fill(utils.BLACK)
            self.screen.fill((0, 0, 0))
            # self.particle_surface.fill((0, 0, 0, 0))
            self.map.draw_map(self.screen)
            if self.map2 is not None:
                self.map2.load_map()
                self.map2.draw_map(self.screen)
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

            x, y = 0, 0
            self.display.blit(self.screen, (0, 0))
            pygame.display.update()

        pygame.quit()
        print("Exited the game loop. Game will quit...")
        quit()
