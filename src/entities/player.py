from math import sqrt
import pygame
from weapon import Weapon
from utils import get_mask_rect
import utils
from animation import load_animation_sprites, EntityAnimation  # entity_animation
from .entity import Entity


class Player(Entity):
    def __init__(self, game):
        Entity.__init__(self, game, 'player')
        self.speed = 100
        self.hp = 100
        self.weapon = Weapon(self.game, 25, 'sword')
        self.attacking = False
        self.attacked = False

    def input(self):
        """s"""
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.direction = 'up'
        if pressed[pygame.K_s]:
            self.direction = 'down'
        if pressed[pygame.K_a]:
            self.direction = 'left'
        if pressed[pygame.K_d]:
            self.direction = 'right'

        constant_dt = 0.06
        vel_up = [0, -self.speed * constant_dt]
        vel_up = [i * pressed[pygame.K_w] for i in vel_up]
        vel_down = [0, self.speed * constant_dt]
        vel_down = [i * pressed[pygame.K_s] for i in vel_down]
        vel_left = [-self.speed * constant_dt, 0]
        vel_left = [i * pressed[pygame.K_a] for i in vel_left]
        vel_right = [self.speed * constant_dt, 0]
        vel_right = [i * pressed[pygame.K_d] for i in vel_right]
        vel = zip(vel_up, vel_down, vel_left, vel_right)
        vel_list = [sum(item) for item in vel]

        x = sqrt(pow(vel_list[0], 2) + pow(vel_list[1], 2))

        if 0 not in vel_list:
            z = x / (abs(vel_list[0]) + abs(vel_list[1]))
            vel_list_fixed = [item * z for item in vel_list]
            self.set_velocity(vel_list_fixed)
        else:
            self.set_velocity(vel_list)

        if pygame.mouse.get_pressed()[0] and pygame.time.get_ticks() - self.time > 600:
            self.time = pygame.time.get_ticks()
            pygame.mixer.Sound.play(pygame.mixer.Sound('../assets/sound/sword.wav'))
            self.attacking = True
            self.attacked = False
            self.weapon.swing_side *= (-1)  # self.player.weapon.swing_side * (-1) + 1
            self.game.counter = 0

    def update(self) -> None:
        """s"""
        self.weapon.update()
        self.entity_animation.update()
        self.wall_collision()
        if self.can_move:
            self.rect.move_ip(*self.velocity)
            self.hitbox.move_ip(*self.velocity)
        self.update_hitbox()

    def draw(self, screen):
        """S"""
        self.draw_shadow(screen)
        screen.blit(self.image, self.rect)
        self.weapon.draw(screen)
        pygame.draw.rect(self.game.room_image.map_surface, (0, 255, 0), self.rect, 1)
        pygame.draw.rect(self.game.room_image.map_surface, (255, 0, 0), self.hitbox, 1)

    def render(self):  # Render weapon
        """s"""
        pass
        # start = pygame.math.Vector2(self.rect.midright)
        # mouse = pygame.mouse.get_pos()
        # end = start + (mouse - start).normalize() * self.gun_length

        # pygame.draw.lines(self.game.screen, (255, 255, 255), False, (start, end), width=self.gun_width)

    def assign_weapon(self, weapon: Weapon):
        """Assigning weapon to player"""
        self.weapon = weapon
