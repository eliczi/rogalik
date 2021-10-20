import pygame
from weapon import Weapon


class Items_bar(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((200, 50))
        self.image.fill((255, 54, 12))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 530
        self.weapon = ''

    def add_weapon(self, weapon):
        pass

    def draw_weapons(self):
        """

        :return:
        :rtype:
        """
        sword_image = pygame.image.load("../assets/weapon/sword.png")
        sword_image = pygame.transform.scale(sword_image, (70, 70))
        self.game.screen.blit(sword_image, (90, 500))

        kij_image = pygame.image.load("../assets/weapon/kij.png")
        kij_image = pygame.transform.scale(kij_image, (70, 70))
        self.game.screen.blit(kij_image, (50, 500))

        katana_image = pygame.image.load("../assets/weapon/katana.png")
        katana_image = pygame.transform.scale(katana_image, (100, 100))
        self.game.screen.blit(katana_image, (-10, 500))

        if self.weapon == 'katana':
            katana_image = pygame.image.load("weapon/katana_picked.png")
            katana_image = pygame.transform.scale(katana_image, (100, 100))
            self.game.screen.blit(katana_image, (-10, 500))

    def draw(self):
        """

        :return:
        :rtype:
        """
        # s = pygame.Surface((200, 70))  # the size of your rect
        # s.set_alpha(128)  # alpha level
        # s.fill(self.game.BROWN)  # this fills the entire surface
        # self.game.screen.blit(s, ( self.rect.x,  self.rect.y))
        self.draw_weapons()
