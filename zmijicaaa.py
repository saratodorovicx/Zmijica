import math
import random
import pygame

stranica = 500
kolone = 17
red = 15 

screen = pygame.display.set_mode((stranica, stranica))
pygame.display.set_caption("Zmijica")

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    pygame.display.update()
    clock.tick(60)

class Kvadrat():
    

 Zmija():
    telo = []
    
