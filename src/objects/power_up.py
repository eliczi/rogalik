import pygame
from .object import Object
import random
from src.particles import PowerUpAttackParticle, ShieldParticle


class PowerUp(Object):
    type = 'flask'
    size = (64, 64)

    def __init__(self, game, room, name, position=None):
        self.name = name
        self.position = [644, 400]
        if position is not None:
            self.position = position
        Object.__init__(self, game, self.name, self.type, self.size, room, self.position)
        self.interaction = False
        self.counter = 0
        self.elevated = False
        self.particles = []

    def load_image(self):
        image = pygame.image.load(f'./assets/objects/power_ups/{self.name}/{self.name}.png').convert_alpha()
        image = pygame.transform.scale(image, self.size)
        self.image = image

    def detect_collision(self):
        if self.game.player.rect.colliderect(self.rect):
            self.image = pygame.image.load(
                f'./assets/objects/power_ups/{self.name}/{self.name}_picked.png').convert_alpha()
            self.interaction = True
        else:
            self.image = pygame.image.load(f'./assets/objects/power_ups/{self.name}/{self.name}.png').convert_alpha()
            self.interaction = False
            self.show_name.reset_line_length()

    def interact(self):
        pass

    def update(self):
        self.hovering.hovering()
        self.show_price.update()
        self.update_hitbox()
        self.update_bounce()

    def draw(self):
        surface = self.room.tile_map.map_surface
        surface.blit(self.image, (self.rect.x, self.rect.y))
        self.beautify(surface)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
        self.show_price.draw(surface)
        self.draw_shadow(surface, -12)

    def beautify(self, surface):
        pass


class AttackPowerUp(PowerUp):
    name = 'attack'

    def __init__(self, game, room, position=None):
        super().__init__(game, room, self.name, position)
        self.value = 250

    def interact(self):
        self.game.player.strength *= 1.1
        self.room.objects.remove(self)
        self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/PowerUp.wav'))

    def beautify(self, surface):
        if random.randint(1, 20) == 1:
            x = random.randint(self.rect.midtop[0] - 30, self.rect.midtop[0] + 30)
            y = random.randint(self.rect.midtop[1] - 30, self.rect.midtop[1] + 30)
            self.game.particle_manager.particle_list.append(PowerUpAttackParticle(self.game, x, y))


class ShieldPowerUp(PowerUp):
    name = 'armor'

    def __init__(self, game, room, position=None):
        super().__init__(game, room, self.name, position)
        self.value = 150

    def interact(self):
        self.game.player.shield += 1
        self.room.objects.remove(self)
        self.game.sound_manager.play(pygame.mixer.Sound('./assets/sound/PowerUp.wav'))

    def beautify(self, surface):
        if random.randint(1, 10) == 1:
            x = random.randint(self.hitbox.midtop[0] - 10, self.rect.midtop[0] + 10)
            y = random.randint(self.hitbox.midtop[1] - 10, self.rect.midtop[1] + 10)
            self.game.particle_manager.particle_list.append(ShieldParticle(self.game, x, y))
