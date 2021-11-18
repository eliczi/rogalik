import pygame
import utils


class Hud:
    position = (21/2 * 64, utils.world_size[1] - 1.5 * 64)

    def __init__(self, game):
        self.game = game
        self.hud_frame = pygame.image.load('../assets/hud_frame.png').convert_alpha()
        self.items_positions = [[580, self.position[1] + 4], [644 + 4, self.position[1] + 4],
                                [708 + 8, self.position[1] + 4]]

    def draw_items(self):
        #works for 3 items
        if self.game.player.items:
            for i, item in enumerate(self.game.player.items):
                if self.game.player.weapon == item:
                    position = self.items_positions[1]
                else:
                    position = self.items_positions[(i//2) * -1]
                self.game.screen.blit(item.hud_image, position)
                # 0 -> 1
                # 1 -> 0
                # 2 > 2 or -1

        text = f'Gold: {str(self.game.player.gold)}'
        text_surface = pygame.font.Font(utils.font, 15).render(text, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (700, 10))
        text2 = f'FPS: {str(int(self.game.clock.get_fps()))}'
        text_surface = pygame.font.Font(utils.font, 15).render(text2, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (700, 30))

    def update(self):
        if self.game.player.items:
            pass

    def draw(self):
        self.draw_items()
        self.game.screen.blit(self.hud_frame, self.position)
