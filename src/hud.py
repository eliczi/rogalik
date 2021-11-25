import pygame
import utils


class Hud:
    position = (17.8 / 2 * 64, utils.world_size[1] - 1.5 * 64)

    def __init__(self, game):
        self.game = game
        self.hud_frame = pygame.image.load('../assets/hud_frame.png').convert_alpha()
        self.rect = self.hud_frame.get_rect()
        self.rect.midtop = (21 / 2 * 64, utils.world_size[1] - 1.4 * 64)
        self.items_positions = [[580, self.position[1] + 4], [644 + 4, self.position[1] + 4],
                                [708 + 8, self.position[1] + 4]]
        print(utils.world_size[0] / 2 * 64)

    def draw_items(self):
        # works for 3 items
        if self.game.player.items:
            for i, item in enumerate(self.game.player.items):
                if self.game.player.weapon == item:
                    position = self.items_positions[1]
                else:
                    position = self.items_positions[(i // 2) * -1]
                self.game.screen.blit(item.hud_image, position)
                # 0 -> 1
                # 1 -> 0
                # 2 > 2 or -1

    def draw_info(self):
        # text = f'Gold: {str(self.game.player.gold)}'
        # text_surface = pygame.font.Font(utils.font, 15).render(text, True, (255, 255, 255))
        # self.game.screen.blit(text_surface, (700, 10))
        text2 = f'FPS: {str(int(self.game.clock.get_fps()))}'
        text_surface = pygame.font.Font(utils.font, 15).render(text2, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (700, 30))
        text3 = f'Position: {str(int(self.game.player.rect.x)), str(int(self.game.player.rect.y))}'
        text_surface = pygame.font.Font(utils.font, 15).render(text3, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (700, 50))

    def draw(self):
        #self.game.screen.blit(self.hud_frame, self.rect)
        self.draw_info()
        # self.draw_items()
