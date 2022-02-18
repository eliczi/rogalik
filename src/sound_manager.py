import pygame

import random


class SoundManager:
    def __init__(self, game):
        self.game = game
        self.coin_sound = []
        self.load_coin_sound()

    def load_coin_sound(self):
        self.coin_sound.append(pygame.mixer.Sound('../assets/coin/sound/Pickup Coin.wav'))
        self.coin_sound.append(pygame.mixer.Sound('../assets/coin/sound/Pickup Coin2.wav'))
        self.coin_sound.append(pygame.mixer.Sound('../assets/coin/sound/Pickup Coi3.wav'))

    def play_coin_sound(self):
        pygame.mixer.Sound.play(random.choice(self.coin_sound))
