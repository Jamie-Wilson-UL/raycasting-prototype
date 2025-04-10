# main.py
import pygame
from engine.player import Player
from engine.raycaster import cast_rays

# Screen settings
WIDTH, HEIGHT = 800, 600  
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Initialize player (starting at position 1.5 tiles from the top-left corner)
from engine.map import TILE_SIZE
player = Player(TILE_SIZE * 1.5, TILE_SIZE * 1.5)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player movement based on pressed keys.
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Render the scene.
    screen.fill((0, 0, 0))  # Clear screen with black.
    cast_rays(screen, player)  # Render walls via raycasting.

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
