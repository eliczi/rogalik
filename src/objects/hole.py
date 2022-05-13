import pygame
from .object import Object


class Hole:
    name = 'next_level'
    def __init__(self, game, position, room):
        self.game = game
        self.room = room
        self.image = None
        self.image_picked = pygame.image.load('./assets/objects/passage/passage_picked.png').convert_alpha()
        self.images = []
        self.load_image()
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        self.animation_frame = 0
        self.animate = True
        self.for_sale = False
        self.counter = 0
        self.interaction = False

    def load_image(self):
        for i in range(5):
            image = pygame.image.load(f'./assets/objects/passage/passage{i}.png').convert_alpha()
            self.images.append(image)
        self.image = self.images[0]

    def update_animation_frame(self):
        self.animation_frame += 1.5 / 15  # random.randint(10, 20)/100
        if self.animation_frame > 4:
            self.animate = False
        self.image = self.images[int(self.animation_frame)]

    def interact(self):
        self.game.world_manager.load_new_level()
        self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/Explosion3.wav'))

    def detect_collision(self):
        if self.game.player.hitbox.colliderect(self.rect) and self.game.player.interaction:
            self.image = self.image_picked
            self.interaction = True
        else:
            self.image = self.images[4]
            self.interaction = False

    def update(self):
        if self.animate:
            self.update_animation_frame()

    def draw(self):
        surface = self.room.tile_map.map_surface
        surface.blit(self.image, (self.rect.x, self.rect.y))
