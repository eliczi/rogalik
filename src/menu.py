import pygame
import utils


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.surface = pygame.Surface(utils.world_size)
        self.surface.fill((0, 0, 0))
        self.running = True

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            self.running = False
        if pressed[pygame.K_1]:
            self.running = False

    def show(self, screen):
        while self.running:
            self.input()
            screen.blit(self.surface, (0, 0))
            pygame.display.update()


