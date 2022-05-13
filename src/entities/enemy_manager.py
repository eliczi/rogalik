import pygame
import random
from src.map.map_generator import Room
from src.map.map_generator import Room
from src.entities.enemy import Imp, Enemy, Demon
from src.entities.boss import Boss


class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.enemy_list = []
        self.damage_multiplier = 1
        self.health_multiplier = 1

    def draw_enemies(self, surface):
        for enemy in self.game.world_manager.current_room.enemy_list:
            enemy.draw()
        if self.game.world_manager.next_room:
            for enemy in self.game.world_manager.next_room.enemy_list:
                enemy.draw()

    def set_enemy_list(self):
        self.enemy_list.clear()  # unnecessary to clear and repopulate list every loop, but no better idea for now
        for enemy in self.game.world_manager.current_room.enemy_list:
            self.enemy_list.append(enemy)

    def update_enemies(self):
        self.set_enemy_list()
        for enemy in self.game.world_manager.current_room.enemy_list:
            enemy.update()
        self.debug()

    def add_enemies(self):
        for row in self.game.world_manager.world.world:
            for room in row:
                if isinstance(room, Room) and room.type == 'normal':
                    self.add_normal_enemies(room)
                if isinstance(room, Room) and room.type == 'boss':
                    room.enemy_list.append(Boss(self.game, room))
                    self.upgrade_enemy(room.enemy_list[-1])
                    room.enemy_list[-1].bullet_damage *= self.damage_multiplier

    def set_enemy_damage(self, enemy):
        enemy.damage *= self.damage_multiplier

    def set_enemy_health(self, enemy):
        enemy.max_hp *= self.health_multiplier
        enemy.hp *= self.health_multiplier

    def upgrade_enemy(self, enemy):
        self.set_enemy_health(enemy)
        self.set_enemy_damage(enemy)

    def add_normal_enemies(self, room):
        level = self.game.world_manager.level
        num_of_demons = random.randint(1 + level, 4 + level)
        num_of_imps = random.randint(0 + level, 4 + level)
        for _ in range(num_of_imps):
            room.enemy_list.append(Imp(self.game, random.randint(100, 150) / 10, 100, room))
            self.upgrade_enemy(room.enemy_list[-1])
            room.enemy_list[-1].spawn()
        for _ in range(num_of_demons):
            room.enemy_list.append(Demon(self.game, 100, room))
            self.upgrade_enemy(room.enemy_list[-1])
            room.enemy_list[-1].spawn()

    def debug(self):
        if pygame.mouse.get_pressed()[2]:
            mx, my = pygame.mouse.get_pos()
            mx -= 64  # because we are rendering player on map_surface
            my -= 32
            self.game.world_manager.current_room.enemy_list.append(
                Demon(self.game, 200, self.game.world_manager.current_room))
            # Imp(self.game, random.randint(100, 150) / 10, 100, self.game.world_manager.current_room, 'imp'))
            self.game.world_manager.current_room.enemy_list[-1].rect.topleft = (mx, my)
