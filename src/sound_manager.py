import pygame
import random


class SoundManager:
    def __init__(self, game):
        self.game = game
        self.coin_sound = None
        self.load_coin_sound()
        self.walk_sound = None
        self.load_walk_sound()
        self.walk_sound_cooldown = 250
        self.drop_sound = pygame.mixer.Sound('./assets/sound/Click3.wav')
        self.drop_sound.set_volume(0.15)
        self.sword_slash = pygame.mixer.Sound('./assets/sound/sword.wav')
        self.sword_slash.set_volume(0.3)
        self.fire_slash = pygame.mixer.Sound('./assets/sound/Fire.wav')
        self.fire_slash.set_volume(0.3)
        self.sword_slash_cooldown = 0
        self.hit_sound = pygame.mixer.Sound('./assets/sound/Hit.wav')
        self.hit_sound.set_volume(0.6)
        self.hit_cd = 0
        self.get_item = pygame.mixer.Sound('./assets/sound/get_item.wav')
        self.drop_items = pygame.mixer.Sound('./assets/sound/Explosion2.wav')
        self.passage = pygame.mixer.Sound('./assets/sound/passage.wav')
        self.passage.set_volume(1)
        self.player_hurt = pygame.mixer.Sound('./assets/sound/Impact4.wav')
        self.boss_bullet = pygame.mixer.Sound('./assets/sound/Click6.wav')
        self.boss_bullet.set_volume(0.2)

    def load_coin_sound(self):
        self.coin_sound = pygame.mixer.Sound('./assets/objects/coin/sound/Pickup Coin.wav')
        self.coin_sound.set_volume(0.3)

    def play(self, sound):
        pygame.mixer.Sound.play(sound)

    def load_walk_sound(self):
        self.walk_sound = pygame.mixer.Sound('./assets/sound/walk.wav')
        self.walk_sound.set_volume(0.8)

    def play_coin_sound(self):
        pygame.mixer.Sound.play(self.coin_sound)

    def play_walk_sound(self):
        if pygame.time.get_ticks() - self.walk_sound_cooldown > 350:
            self.walk_sound_cooldown = pygame.time.get_ticks()
            pygame.mixer.Sound.play(self.walk_sound)

    def play_drop_sound(self):
        pygame.mixer.Sound.play(self.drop_sound)

    def play_sword_sound(self, type='sword'):
        if (
            type == 'fire'
            and pygame.time.get_ticks() - self.sword_slash_cooldown > 350
        ):
            self.sword_slash_cooldown = pygame.time.get_ticks()
            pygame.mixer.Sound.play(self.fire_slash)

        elif pygame.time.get_ticks() - self.sword_slash_cooldown > 350:
            self.sword_slash_cooldown = pygame.time.get_ticks()
            pygame.mixer.Sound.play(self.sword_slash)

    def play_hit_sound(self):
        if pygame.time.get_ticks() - self.hit_cd > 25:
            self.hit_cd = pygame.time.get_ticks()
            pygame.mixer.Sound.play(self.hit_sound)

    def play_get_item_sound(self):
        pygame.mixer.Sound.play(self.get_item)

    def play_drop_items_sound(self):
        pygame.mixer.Sound.play(self.drop_items)

    def play_passage(self):
        pygame.mixer.Sound.play(self.passage)
