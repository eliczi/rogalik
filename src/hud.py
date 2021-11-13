import pygame
import utils


class Hud:
    position = (9 * 64, utils.world_size[1] - 1.5 * 64)

    def __init__(self, game):
        self.game = game
        self.hud_frame = pygame.image.load('../assets/hud_frame.png').convert_alpha()
        self.items_positions = [[580, self.position[1] + 4], [644 + 4, self.position[1] + 4], [708 + 8, self.position[1] + 4]]

    def draw_items(self):
        if self.game.player.items:
            for i, item in enumerate(self.game.player.items):
                position = self.items_positions[i]
                # position = (self.position[0] + 4, self.position[1] + 4)
                # pygame.draw.rect(self.game.screen, (255, 255, 255, 120), (*position, 64, 64))
                self.game.screen.blit(item.hud_image, position)

    def draw(self):
        self.draw_items()
        self.game.screen.blit(self.hud_frame, self.position)
