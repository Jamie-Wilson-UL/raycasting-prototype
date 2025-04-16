import math
import pygame
import numpy as np
from engine.map import GAME_MAP, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT
from engine.constants import WIDTH, HEIGHT

wall_texture = None
texture_width = None
texture_height = None

FOV = math.pi / 3  # 60°
NUM_RAYS = 800
MAX_DEPTH = 20
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS
d_proj = (WIDTH / 2) / math.tan(FOV / 2)

# Store wall distances for sprite occlusion
wall_distances = np.zeros(NUM_RAYS)

def init_textures():
    global wall_texture, texture_width, texture_height
    if wall_texture is None:
        wall_texture = pygame.image.load("assets/images/wall.png").convert()
        texture_width = wall_texture.get_width()
        texture_height = wall_texture.get_height()

def cast_rays(screen, player, baseline):
    init_textures()
    start_angle = player.angle - FOV/2
    
    # Pre-calculate sin and cos for all rays
    ray_angles = np.arange(NUM_RAYS) * DELTA_ANGLE + start_angle
    sin_a = np.sin(ray_angles)
    cos_a = np.cos(ray_angles)
    
    for ray in range(NUM_RAYS):
        current_sin = sin_a[ray]
        current_cos = cos_a[ray]
        
        for depth in range(1, MAX_DEPTH * TILE_SIZE):
            target_x = player.x + depth * current_cos
            target_y = player.y + depth * current_sin
            map_x = int(target_x // TILE_SIZE)
            map_y = int(target_y // TILE_SIZE)
            
            if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                break
                
            if GAME_MAP[map_y][map_x]:
                depth_corrected = depth * math.cos(player.angle - ray_angles[ray])
                wall_distances[ray] = depth_corrected
                lineHeight = (TILE_SIZE / (depth_corrected + 0.0001)) * d_proj
                
                hit_offset = target_x % TILE_SIZE
                texture_x = int((hit_offset / TILE_SIZE) * texture_width)
                texture_x = min(texture_x, texture_width - 1)
                
                wall_slice = wall_texture.subsurface((texture_x, 0, 1, texture_height))
                wall_slice_scaled = pygame.transform.scale(wall_slice, (SCALE, int(lineHeight)))
                drawStart = int(baseline - (lineHeight/2))
                column_position = ray * SCALE
                screen.blit(wall_slice_scaled, (column_position, drawStart))
                break
