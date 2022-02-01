import pygame

import utils


class GameOver:
    def __init__(self, game):
        self.game = game
        self.text = 'GAME OVER'
        self.counter = 0
        self.image_size = (360, 360)
        self.image = pygame.transform.scale(pygame.image.load('../assets/game_over.png'), self.image_size)
        self.rect = self.image.get_rect()
        self.rect.center = (utils.world_size[0] / 2, utils.world_size[1] /2)
        self.position = [utils.world_size[0] / 2 - 180, - 800]
        self.hover_value = -5
        self.game_over = False

    @staticmethod
    def input():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    def update(self):
        if self.game.player.dead:
            self.input()
            self.counter += 1
            if self.position[1] <= self.rect.midtop[1]:
                self.position[1] += 15
            else:
                self.game_over = True
                self.hover()

    def draw(self):
        if self.game.player.dead:
            self.game.screen.blit(self.image, self.position)
            #pygame.draw.rect(self.game.screen, (255, 255, 255), self.rect, 1)

    def hover(self):
        if self.counter % 30 == 0:
            self.position[1] += self.hover_value
        if pygame.time.get_ticks() % 1000 < 500:
            self.hover_value = -5
        elif pygame.time.get_ticks() % 1000 > 500:
            self.hover_value = 5
