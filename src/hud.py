import pygame
import utils
from math import ceil


class PlayerHP:
    def __init__(self, player):
        self.image_size = (32, 32)
        self.images = []
        self.load_images()
        self.starting_position = (0, 0)
        self.player = player
        self.num_of_hearts = 0
        self.full_heart = self.images[0]
        self.half_heart = self.images[1]
        self.empty_heart = self.images[2]
        self.num_full_hearts = 0
        self.num_half_hearts = 0
        self.num_empty_heart = 0

    def load_images(self):
        self.images.append(
            pygame.transform.scale(pygame.image.load('../assets/full_heart.png').convert_alpha(), self.image_size))
        self.images.append(
            pygame.transform.scale(pygame.image.load('../assets/half_heart.png').convert_alpha(), self.image_size))
        self.images.append(
            pygame.transform.scale(pygame.image.load('../assets/empty_heart.png').convert_alpha(), self.image_size))

    def calculate_hearts(self):  # how many hearth to display and what kind
        if self.player.hp >= 0:
            self.num_of_hearts = ceil(self.player.max_hp / 20)
            self.num_full_hearts = self.player.hp // 20
            self.num_half_hearts = 1 if not (self.player.hp / 20).is_integer() else 0
            self.num_empty_heart = self.num_of_hearts - self.num_half_hearts - self.num_full_hearts

    def update(self):
        self.calculate_hearts()

    def draw(self, surface):
        self.update()
        x, y = 0, 5
        for _ in range(self.num_full_hearts):
            surface.blit(self.full_heart, (x * 36, y))
            x += 1
        for _ in range(self.num_half_hearts):
            surface.blit(self.half_heart, (x * 36, y))
            x += 1
        for _ in range(self.num_empty_heart):
            surface.blit(self.empty_heart, (x * 36, y))
            x += 1


class PlayerGold:
    def __init__(self, player):
        self.image_size = (24, 24)
        self.image = None
        self.load_image()
        self.starting_position = (0, 0)
        self.player = player
        self.text = None

    def load_image(self):
        self.image = pygame.transform.scale(pygame.image.load('../assets/coin/coin/coin0.png').convert_alpha(),
                                            self.image_size)

    def update(self):
        self.text = f'{self.player.gold}'

    def draw(self, surface):
        self.update()
        surface.blit(self.image, (0, 40))
        text_surface = pygame.font.Font(utils.font, 24).render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, (25, 45))


class PlayerShield:
    def __init__(self, player):
        self.image_size = (24, 24)
        self.image = None
        self.load_image()
        self.starting_position = (0, 0)
        self.player = player
        self.text = None

    def load_image(self):
        self.image = pygame.transform.scale(pygame.image.load('../assets/power_ups/armor/armor.png').convert_alpha(),
                                            self.image_size)

    def update(self):
        self.text = f'x{self.player.shield}'

    def draw(self, surface):
        self.update()
        surface.blit(self.image, (0, 70))
        text_surface = pygame.font.Font(utils.font, 24).render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, (25, 75))


class Hud:
    position = (17.8 / 2 * 64, utils.world_size[1] - 1.5 * 64)

    def __init__(self, game):
        self.game = game
        self.hud_frame = pygame.image.load('../assets/hud_frame.png').convert_alpha()
        self.rect = self.hud_frame.get_rect()
        self.rect.midtop = (21 / 2 * 64, utils.world_size[1] - 1.4 * 64)
        self.items_positions = [[580, self.position[1] + 4], [644 + 4, self.position[1] + 4],
                                [708 + 8, self.position[1] + 4]]
        self.player = self.game.player
        self.hp = PlayerHP(self.game.player)
        self.gold = PlayerGold(self.game.player)
        self.shield = PlayerShield(self.game.player)

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
        text2 = f'D000pa: {int(self.game.clock.get_fps())}'
        text_surface = pygame.font.Font(utils.font, 15).render(text2, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (0, 120))
        text3 = f'C1111pa: {str(int(self.player.rect.x)), str(int(self.game.player.rect.midbottom[1]))}'
        text_surface = pygame.font.Font(utils.font, 15).render(text3, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (0, 140))
        # text4 = f'konie na godzine: {self.player.hp}'
        # text_surface = pygame.font.Font(utils.font, 15).render(text4, True, (255, 255, 255))
        #self.game.screen.blit(text_surface, (0, 160))
        self.hp.draw(self.game.screen)
        self.gold.draw(self.game.screen)
        self.shield.draw(self.game.screen)

    def draw(self):
        # self.game.screen.blit(self.hud_frame, self.rect)
        self.draw_info()
        # self.draw_items()
