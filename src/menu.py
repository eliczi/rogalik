import pygame

import utils


class Button:
    def __init__(self, menu, x, y, name):
        self.name = name
        self.menu = menu
        self.images = []
        self.load_images()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y)
        self.clicked = False

    def load_images(self):
        self.images.append(pygame.image.load(f'../assets/{self.name}1.png').convert_alpha())
        self.images.append(pygame.image.load(f'../assets/{self.name}2.png').convert_alpha())

    def detect_action(self, pos):
        action = False
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.menu.running = False
            action = True
            self.clicked = True
        return action

    def update(self):
        pos = pygame.mouse.get_pos()
        self.image = self.images[1] if self.rect.collidepoint(pos) else self.images[0]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.play_button = Button(self, 21 * 64 / 2, 6 * 64 / 2, 'play')
        self.exit_button = Button(self, 21 * 64 / 2, 5 * 64 / 2 + 240, 'exit')
        self.dupa = self.game.running

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            self.running = False
            self.game.running = False
        if pressed[pygame.K_1]:
            self.running = False

    def show(self):
        while self.running:
            self.game.screen.fill((0, 0, 0))
            self.game.background.update()
            self.game.background.draw(self.game.screen)
            self.input()
            self.play_button.update()
            self.exit_button.update()
            self.play_button.draw(self.game.screen)
            self.exit_button.draw(self.game.screen)
            self.play_button.detect_action(pygame.mouse.get_pos())

            self.game.display.blit(self.game.screen, (0, 0))
            pygame.display.flip()
