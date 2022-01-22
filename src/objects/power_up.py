import pygame
from .object import Object
import random


class PowerUp(Object):
    type = 'flask'
    size = (64, 64)

    def __init__(self, game, room):
        self.name = random.choice(['attack', 'armor'])
        self.position = [644, 400]
        Object.__init__(self, game, self.name, self.type, self.size, room, self.position)
        self.interaction = False
        self.shadow_position = [self.rect.bottomleft[0] - 4, self.rect.bottomleft[1] - 5]
        self.shadow_value = 1
        self.counter = 0

    def load_image(self):
        image = pygame.image.load(f'../assets/power_ups/{self.name}/{self.name}.png').convert_alpha()
        image = pygame.transform.scale(image, self.size)
        self.image = image

    def detect_collision(self):
        if self.game.player.hitbox.colliderect(self.rect):
            self.image = pygame.image.load(f'../assets/power_ups/{self.name}/{self.name}_picked.png').convert_alpha()
            self.interaction = True
        elif self.interaction:
            self.image = pygame.image.load(f'../assets/power_ups/{self.name}/{self.name}.png').convert_alpha()

    def interact(self):
        if self.name == 'attack':
            self.game.player.strength += 0.1
        elif self.name == 'armor':
            self.game.player.shield += 1
        elif self.name == 'hp':
            self.game.player.max_hp += 20
            self.game.player.hp += 20
        self.room.objects.remove(self)

    def update(self):
        self.update_hitbox()

    def draw(self):
        surface = self.room.tile_map.map_surface
        #self.draw_shadow(surface)
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def change_size(self):
        pass

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(shape_surf, color, (0, 0, 30, 14 + self.shadow_value))
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        position = [self.rect.bottomleft[0] - 4, self.rect.bottomleft[1] - 5]
        surface.blit(shape_surf, self.shadow_position)



    def pickup_effect(self):
        pass
