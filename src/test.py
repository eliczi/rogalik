import pygame

screen = pygame.display.set_mode((1000, 1000)).convert



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    pygame.display.update()