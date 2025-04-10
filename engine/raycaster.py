# engine/raycaster.py
import math
import pygame
from engine.map import GAME_MAP, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

# Configuration for raycasting
FOV = math.pi / 3  # 60° field of view
NUM_RAYS = 800  # This might equal your window width (if each ray corresponds to one pixel)
MAX_DEPTH = 20  # Maximum number of tiles to search
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = 800 // NUM_RAYS  # Adjust depending on window dimensions

def cast_rays(screen, player):
    """
    Cast rays from the player's position and render vertical slices of wall.
    """
    start_angle = player.angle - FOV / 2

    for ray in range(NUM_RAYS):
        current_angle = start_angle + ray * DELTA_ANGLE
        sin_a = math.sin(current_angle)
        cos_a = math.cos(current_angle)
        
        for depth in range(1, MAX_DEPTH * TILE_SIZE):
            target_x = player.x + depth * cos_a
            target_y = player.y + depth * sin_a

            map_x = int(target_x // TILE_SIZE)
            map_y = int(target_y // TILE_SIZE)

            # Ensure within map boundaries
            if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                break

            # Check if wall is hit (assuming non-zero values in GAME_MAP are walls)
            if GAME_MAP[map_y][map_x]:
                # Correct fisheye effect:
                depth *= math.cos(player.angle - current_angle)
                # Calculate wall slice height (the constant factor is chosen by trial)
                wall_height = (TILE_SIZE * 277) / (depth + 0.0001)
                # Determine color intensity based on depth:
                color_intensity = max(0, 255 - int(depth * 0.5))
                color = (color_intensity, color_intensity, color_intensity)
                # Draw vertical slice:
                column_position = ray * SCALE
                pygame.draw.rect(screen, color, (column_position, (600 // 2) - wall_height // 2, SCALE, wall_height))
                break
