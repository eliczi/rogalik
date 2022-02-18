import pygame
from .object import Object
import random
from particles import PowerUpAttackParticle, ShieldParticle


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
        self.shadow_position = [self.rect.midbottom[0] - 28, self.rect.midbottom[1]]
        self.shadow_value = 2
        self.counter = 0
        self.elevated = False
        self.hover_value = 5
        self.up = False
        self.shadow_width = self.hitbox.width
        self.particles = []

    def load_image(self):
        image = pygame.image.load(f'../assets/power_ups/{self.name}/{self.name}.png').convert_alpha()
        image = pygame.transform.scale(image, self.size)
        self.image = image

    def detect_collision(self):
        if self.game.player.rect.colliderect(self.rect):
            self.image = pygame.image.load(f'../assets/power_ups/{self.name}/{self.name}_picked.png').convert_alpha()
            self.interaction = True
        else:
            self.image = pygame.image.load(f'../assets/power_ups/{self.name}/{self.name}.png').convert_alpha()
            self.interaction = False
            self.show_name.reset_line_length()

    def interact(self):
        pass

    def update(self):
        self.hovering.hovering()
        self.show_price.update()
        self.update_hitbox()

    def draw(self):
        surface = self.room.tile_map.map_surface
        self.draw_shadow(surface)
        surface.blit(self.image, (self.rect.x, self.rect.y))
        self.beautify(surface)
        if self.interaction:
            self.show_name.draw(surface, self.rect)
        self.show_price.draw(surface)

    def draw_shadow(self, surface):
        color = (0, 0, 0, 120)
        shape_surf = pygame.Surface((50, 50), pygame.SRCALPHA).convert_alpha()
        if self.up:
            pygame.draw.ellipse(shape_surf, color, (1, 0, self.shadow_width / 2 - 2, 12))
        else:
            pygame.draw.ellipse(shape_surf, color, (0, 0, self.shadow_width / 2, 14))
        shape_surf = pygame.transform.scale(shape_surf, (100, 100))
        surface.blit(shape_surf, self.shadow_position)

    def beautify(self, surface):
        pass

    def pickup_effect(self):
        pass


class AttackPowerUp(PowerUp):
    name = 'attack'

    def __init__(self, game, room, position=None):
        super().__init__(game, room, self.name, position)

    def interact(self):
        self.game.player.strength *= 1.1
        self.room.objects.remove(self)

    def beautify(self, surface):
        if random.randint(1, 20) == 1:
            x = random.randint(self.rect.midtop[0] - 30, self.rect.midtop[0] + 30)
            y = random.randint(self.rect.midtop[1] - 30, self.rect.midtop[1] + 30)
            self.game.particle_manager.particle_list.append(PowerUpAttackParticle(self.game, x, y))

    def pickup_effect(self):
        pass


class ShieldPowerUp(PowerUp):
    name = 'armor'

    def __init__(self, game, room, position=None):
        super().__init__(game, room, self.name, position)
        self.value = 50

    def interact(self):
        self.game.player.shield += 1
        self.room.objects.remove(self)

    def beautify(self, surface):
        if random.randint(1, 10) == 1:
            x = random.randint(self.hitbox.midtop[0] - 10, self.rect.midtop[0] + 10)
            y = random.randint(self.hitbox.midtop[1] - 10, self.rect.midtop[1] + 10)
            self.game.particle_manager.particle_list.append(ShieldParticle(self.game, x, y))
