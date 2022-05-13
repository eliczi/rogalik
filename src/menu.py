import pygame


class Button:
    def __init__(self, menu, x, y, name):
        self.name = name
        self.menu = menu
        self.images = []
        self.path = './assets/misc/buttons'
        self.load_images()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y)
        self.clicked = False
        self.sound = pygame.mixer.Sound('./assets/sound/menu select.wav')
        self.played = False

    def load_images(self):

        self.images.append(pygame.image.load(f'{self.path}/{self.name}1.png').convert_alpha())
        self.images.append(pygame.image.load(f'{self.path}/{self.name}2.png').convert_alpha())

    def detect_action(self, pos):
        pass

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.image = self.images[1]
            self.play_sound()
        else:
            self.image = self.images[0]
            self.played = False
        self.detect_action(pos)

    def play_sound(self):
        if not self.played:
            pygame.mixer.Sound.play(self.sound)
            self.played = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class PlayButton(Button):
    def __init__(self, menu, x, y):
        super().__init__(menu, x, y, 'play')

    def detect_action(self, pos):
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.menu.running = False
            self.menu.game.running = True
            self.clicked = True


class ExitButton(Button):
    def __init__(self, menu, x, y):
        super().__init__(menu, x, y, 'exit')

    def detect_action(self, pos):
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.menu.game.running = False
            self.menu.running = False
            self.clicked = True


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.play_button = PlayButton(self, 21 * 64 / 2, 8 * 64 / 2)
        self.exit_button = ExitButton(self, 21 * 64 / 2, 7 * 64 / 2 + 240)
        self.rogalik = pygame.image.load('./assets/misc/rogalik.png').convert_alpha()
        self.rogalik = pygame.transform.scale(self.rogalik, (320, 240))
        # self.rogalik.set_colorkey((0, 0, 0, 0))
        self.rogalik_rect = self.rogalik.get_rect()
        self.rogalik_rect.midtop = (21 * 64 / 2, 50)

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            self.game.running = False

    def update(self):
        self.game.background.update()
        self.play_button.update()
        self.exit_button.update()

    def draw(self):
        self.game.screen.fill((0, 0, 0))
        self.game.background.draw(self.game.screen)
        self.play_button.draw(self.game.screen)
        self.exit_button.draw(self.game.screen)
        self.game.screen.blit(self.rogalik, self.rogalik_rect)

    def show(self):
        while self.running:
            self.input()
            self.update()
            self.draw()
            self.play_button.detect_action(pygame.mouse.get_pos())
            self.game.clock.tick(self.game.fps)
            self.game.display.blit(self.game.screen, (0, 0))
            pygame.display.flip()
