import pygame
import src.utils as utils
from math import ceil


class HealthBar:
    def __init__(self, player, game):
        self.game = game
        self.block = None
        self.end = None
        self.start = None
        self.path = f'./assets/misc/health_bar'
        self.load_images()
        self.starting_position = (0, 0)
        self.player = player
        self.max_hp_color = (98, 35, 47)
        self.hp_color = (217, 78, 56)

    def load_images(self):
        self.block = pygame.image.load(f'{self.path}/block.png').convert_alpha()
        self.end = pygame.image.load(f'{self.path}/end.png').convert_alpha()
        self.start = pygame.image.load(f'{self.path}/start.png').convert_alpha()

    def draw_health_rectangle(self):
        current_hp = self.player.hp
        max_hp = self.player.max_hp
        pygame.draw.rect(self.game.screen, self.max_hp_color, (25, 10, max_hp + max_hp / 2, 20))
        num_of_blocks = int(current_hp // 10)
        end_position = None
        for i in range(num_of_blocks):
            pygame.draw.rect(self.game.screen, self.hp_color, (25 + i * 15, 15, 10, 15))
            end_position = (25 + i * 15 + 15)
        if end_position:
            pygame.draw.rect(self.game.screen, self.hp_color, (end_position, 15, current_hp % 10, 15))
        self.draw()

    def draw(self):
        end_position = None
        self.game.screen.blit(self.start, (0, 0))
        for i in range(self.player.max_hp // 10):
            self.game.screen.blit(self.block, (i * 15 + 40, 0))
            end_position = (i * 15 + 40, 0)
        self.game.screen.blit(self.end, end_position)


class PlayerGold:
    def __init__(self, player):
        self.image_size = (24, 24)
        self.image = None
        self.load_image()
        self.starting_position = (0, 0)
        self.player = player
        self.text = None
        self.image_position = (0, 50)
        self.text_position = (25, 55)

    def load_image(self):
        self.image = pygame.transform.scale(pygame.image.load('./assets/objects/coin/coin/coin0.png').convert_alpha(),
                                            self.image_size)

    def update(self):
        self.text = f'{self.player.gold}'

    def draw(self, surface):
        self.update()
        surface.blit(self.image, (0, 50))
        text_surface = pygame.font.Font(utils.font, 24).render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, (25, 55))


class PlayerShield:
    name = 'armor'

    def __init__(self, player):
        self.image_size = (24, 24)
        self.image = None
        self.load_image()
        self.starting_position = (0, 0)
        self.player = player
        self.text = None
        self.image_position = (0, 80)
        self.text_position = (25, 85)

    def load_image(self):
        self.image = pygame.transform.scale(
            pygame.image.load(f'./assets/objects/power_ups/{self.name}/{self.name}_hud.png').convert_alpha(),
            self.image_size)

    def update(self):
        self.text = f'x{self.player.shield}'

    def draw(self, surface):
        self.update()
        surface.blit(self.image, self.image_position)
        text_surface = pygame.font.Font(utils.font, 24).render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, self.text_position)


class PlayerAttack(PlayerShield):
    name = 'attack'

    def __init__(self, player):
        super().__init__(player)
        self.image_position = (0, 110)
        self.text_position = (25, 110)

    def update(self):
        self.text = f'x{round(self.player.strength,2)}'


class Hud:
    position = (17.8 / 2 * 64, utils.world_size[1] - 1.5 * 64)

    def __init__(self, game):
        self.game = game
        self.hud_frame = pygame.image.load('./assets/misc/hud_frame.png').convert_alpha()
        self.rect = self.hud_frame.get_rect()
        self.rect.midtop = (21 / 2 * 64, utils.world_size[1] - 1.4 * 64)
        self.items_positions = [[580, self.position[1] + 4], [644 + 4, self.position[1] + 4],
                                [708 + 8, self.position[1] + 4]]
        self.player = self.game.player
        self.gold = PlayerGold(self.game.player)
        self.shield = PlayerShield(self.game.player)
        self.attack = PlayerAttack(self.game.player)
        self.health_bar = HealthBar(self.game.player, self.game)

    def draw_items(self):
        # works for 3 items
        if self.player.items:
            for i, item in enumerate(self.player.items):
                if self.player.weapon == item:
                    position = self.items_positions[1]
                else:
                    position = self.items_positions[(i // 2) * -1]
                self.game.screen.blit(item.hud_image, position)

    def draw_info(self):
        text2 = f'FPS: {int(self.game.clock.get_fps())}'
        text_surface = pygame.font.Font(utils.font, 15).render(text2, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (0, 150))
        text2 = f'LEVEL: {int(self.game.world_manager.level)}'
        text_surface = pygame.font.Font(utils.font, 15).render(text2, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (600, 0))
        # text3 = f'C1111pa: {str(int(self.player.rect.x)), str(int(self.game.player.rect.midbottom[1]))}'
        # text_surface = pygame.font.Font(utils.font, 15).render(text3, True, (255, 255, 255))
        # self.game.screen.blit(text_surface, (0, 140))
        # text4 = f'HP: {self.player.hp}/{self.player.max_hp}'
        # text_surface = pygame.font.Font(utils.font, 15).render(text4, True, (255, 255, 255))
        # self.game.screen.blit(text_surface, (0, 200))
        # # self.hp.draw(self.game.screen)
        self.health_bar.draw_health_rectangle()
        self.gold.draw(self.game.screen)
        self.shield.draw(self.game.screen)
        self.attack.draw(self.game.screen)

    def draw(self):
        # self.game.screen.blit(self.hud_frame, self.rect)
        self.draw_info()
        # self.draw_items()
