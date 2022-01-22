import pygame


class GameOver:
    def __init__(self, game):
        self.size = (10, 10)
        self.position = (100, 100)
        self.screen = pygame.Surface((250, 250)).convert_alpha()
        self.game_over = False
        self.game = game

    def draw(self):
        self.screen.fill((182, 131, 29))
        self.game.screen.blit(self.screen, self.position)

    def run(self):
        while self.game_over:
            self.draw()
