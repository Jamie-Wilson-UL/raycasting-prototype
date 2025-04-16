import os
import math
import pygame
import numpy as np
import random
import threading
import time

from engine.player import Player
from engine.map import TILE_SIZE, GAME_MAP, MAP_WIDTH, MAP_HEIGHT
from engine.raycaster import cast_rays, NUM_RAYS, wall_distances
from engine.enemy import Enemy
from engine.gun import Gun
from engine.constants import WIDTH, HEIGHT

# Define asset paths
sky_path = os.path.join("assets", "images", "sky.png")
floor_path = os.path.join("assets", "images", "floor.png")
enemy_path = os.path.join("assets", "images", "enemy.png")
dan_path = os.path.join("assets", "images", "dan.png")
jarlath_path = os.path.join("assets", "images", "jarlath.png")
cat_path = os.path.join("assets", "images", "cat.png")
zombie_path = os.path.join("assets", "images", "zombie_punk.png")
gun_path = os.path.join("assets", "images", "gun.png")

FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Title Screen ---
def show_title_screen():
    # Load title background
    title_bg = pygame.image.load(os.path.join("assets", "images", "title_bg.png")).convert()
    title_bg = pygame.transform.scale(title_bg, (WIDTH, HEIGHT))
    
    # Create fonts
    title_font = pygame.font.Font(None, 74)
    subtitle_font = pygame.font.Font(None, 36)
    
    # Create text surfaces
    title_text = title_font.render("RAYCASTING PROTOTYPE", True, (255, 255, 255))
    start_text = subtitle_font.render("CLICK TO BEGIN YOUR JOURNEY", True, (255, 255, 255))
    loading_text = subtitle_font.render("Loading...", True, (150, 150, 150))
    
    # Position text
    title_rect = title_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
    start_rect = start_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
    loading_rect = loading_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 100))
    
    # Show mouse cursor on title screen
    pygame.mouse.set_visible(True)
    
    # Animation variables
    pulse_speed = 0.05
    pulse_min = 0.5
    pulse_max = 1.0
    pulse_value = pulse_min
    pulse_direction = 1
    
    # Start loading assets in the background
    loading_thread = threading.Thread(target=load_assets)
    loading_thread.start()
    load_start_time = pygame.time.get_ticks()
    
    waiting = True
    while waiting:
        # Update pulse animation
        pulse_value += pulse_speed * pulse_direction
        if pulse_value >= pulse_max:
            pulse_value = pulse_max
            pulse_direction = -1
        elif pulse_value <= pulse_min:
            pulse_value = pulse_min
            pulse_direction = 1
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    waiting = False
        
        # Draw background and text
        screen.blit(title_bg, (0, 0))
        screen.blit(title_text, title_rect)
        
        # Draw pulsing start text
        alpha = int(255 * pulse_value)
        start_text.set_alpha(alpha)
        screen.blit(start_text, start_rect)
        
        # Show loading text while assets are loading
        if not loading_thread.is_alive():
            loading_text.set_alpha(0)
        else:
            loading_alpha = int(255 * (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2)
            loading_text.set_alpha(loading_alpha)
            screen.blit(loading_text, loading_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Wait for loading thread to complete
    loading_thread.join()
    
    # Hide mouse cursor before starting game
    pygame.mouse.set_visible(False)
    return True

def load_assets():
    """Load all game assets in a separate thread"""
    global sky_texture, floor_texture, enemy_sheet, dan_sheet, jarlath_sheet, cat_sheet, zombie_sheet, dan_hit_sheet, gun_sheet
    global enemy_bg, dan_bg, jarlath_bg, cat_bg, zombie_bg
    
    start_time = time.time()
    
    # Load textures
    sky_texture = pygame.image.load(sky_path).convert()
    floor_texture = pygame.image.load(floor_path).convert()
    
    # Load sprite sheets
    enemy_sheet = pygame.image.load(enemy_path).convert_alpha()
    enemy_bg = enemy_sheet.get_at((0, 0))[:3]
    
    dan_sheet = pygame.image.load(dan_path).convert_alpha()
    dan_bg = dan_sheet.get_at((0, 0))[:3]
    
    jarlath_sheet = pygame.image.load(jarlath_path).convert_alpha()
    jarlath_bg = jarlath_sheet.get_at((0, 0))[:3]
    
    cat_sheet = pygame.image.load(cat_path).convert_alpha()
    cat_bg = cat_sheet.get_at((0, 0))[:3]
    
    zombie_sheet = pygame.image.load(zombie_path).convert_alpha()
    zombie_bg = zombie_sheet.get_at((0, 0))[:3]
    
    # Load hit sprite sheet
    dan_hit_sheet = pygame.image.load('assets/images/dan_hit.png').convert_alpha()
    
    # Load gun sprite sheet
    gun_sheet = pygame.image.load(gun_path).convert_alpha()
    
    end_time = time.time()

def show_level_objective():
    # Create fonts
    title_font = pygame.font.Font(None, 48)
    subtitle_font = pygame.font.Font(None, 36)
    
    # Create text surfaces
    level_text = title_font.render("LEVEL 1: CAR PARK", True, (255, 255, 255))
    objective_text = subtitle_font.render("Objective: Reach The Venue", True, (200, 200, 200))
    
    # Position text
    level_rect = level_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 30))
    objective_rect = objective_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 20))
    
    # Animation variables
    fade_speed = 0.5
    alpha = 255
    
    # Show level screen for longer
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 5000:  # Show for 5 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        
        # Draw background and text
        screen.fill((0, 0, 0))
        level_text.set_alpha(alpha)
        objective_text.set_alpha(alpha)
        screen.blit(level_text, level_rect)
        screen.blit(objective_text, objective_rect)
        pygame.display.flip()
        
        # Start fading after 3 seconds
        if pygame.time.get_ticks() - start_time > 3000:
            alpha -= fade_speed
        
        clock.tick(FPS)
    
    return True

# Show title screen and check if user wants to quit
if not show_title_screen():
    pygame.quit()
    exit()

# Show level objective
if not show_level_objective():
    pygame.quit()
    exit()

# --- Camera/Projection Settings ---
EYE_HEIGHT = 100      # Lowered to fix floor rendering
PLAYER_PITCH = -30    # Lowered to fix floor rendering
baseline = (HEIGHT // 2) - PLAYER_PITCH

FOV = math.pi / 3  # 60°

# --- Asset Loading ---
sky_texture = pygame.image.load(sky_path).convert()
floor_texture = pygame.image.load(floor_path).convert()

try:
    enemy_sheet = pygame.image.load(enemy_path).convert_alpha()
    enemy_bg = enemy_sheet.get_at((0, 0))[:3]
except Exception as e:
    enemy_sheet = None
    enemy_bg = None

try:
    dan_sheet = pygame.image.load(dan_path).convert_alpha()
    dan_bg = dan_sheet.get_at((0, 0))[:3]
except Exception as e:
    dan_sheet = None
    dan_bg = None

try:
    jarlath_sheet = pygame.image.load(jarlath_path).convert_alpha()
    jarlath_bg = jarlath_sheet.get_at((0, 0))[:3]
except Exception as e:
    jarlath_sheet = None
    jarlath_bg = None

try:
    cat_sheet = pygame.image.load(cat_path).convert_alpha()
    cat_bg = cat_sheet.get_at((0, 0))[:3]
except Exception as e:
    cat_sheet = None
    cat_bg = None

# Load hit sprite sheet
dan_hit_sheet = pygame.image.load('assets/images/dan_hit.png').convert_alpha()

# --- Floor Texture Setup ---
floor_tex_array = pygame.surfarray.array3d(floor_texture)
floor_tex_w = floor_texture.get_width()
floor_tex_h = floor_texture.get_height()

# Scale floor texture to match world units
floor_scale = TILE_SIZE / 64  # Assuming original texture is meant to cover 64 units
floor_tex_w = int(floor_tex_w * floor_scale)
floor_tex_h = int(floor_tex_h * floor_scale)
floor_tex_array = pygame.surfarray.array3d(pygame.transform.scale(floor_texture, (floor_tex_w, floor_tex_h)))

d_proj = (WIDTH / 2) / math.tan(FOV / 2)

# --- Create the Player and Gun ---
player = Player(TILE_SIZE * 1.5, TILE_SIZE * 1.5, angle=0, eye_height=EYE_HEIGHT, pitch=PLAYER_PITCH)
player.move_speed = 12.0  # Reduced from 15.0 to 12.0 (20% slower)
player.rot_speed = 0.3  # Reduced from 0.4 to 0.3 (25% slower)
gun = Gun(gun_path)

# --- Random Sprite Placement ---
def get_free_positions():
    free = []
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if GAME_MAP[row][col] == 0:
                free.append((col, row))
    return free

def tile_to_world(tile):
    col, row = tile
    return (col * TILE_SIZE + TILE_SIZE/2, row * TILE_SIZE + TILE_SIZE/2)

free_tiles = get_free_positions()
random.shuffle(free_tiles)
sprites = []
if len(free_tiles) >= 5:
    pos1 = tile_to_world(free_tiles[0])
    sprites.append(Enemy(
        x = pos1[0],
        y = pos1[1],
        sprite_sheet = jarlath_sheet,
        rows = 2,
        cols = 4,
        anim_speed = 150,
        world_height = TILE_SIZE * 0.95,  # Slightly shorter than walls
        remove_bg_color = jarlath_bg,
        foot_offset = 12  # Increased to remove more from bottom
    ))
    pos2 = tile_to_world(free_tiles[1])
    sprites.append(Enemy(
        x = pos2[0],
        y = pos2[1],
        sprite_sheet = dan_sheet,
        rows = 2,
        cols = 4,
        anim_speed = 150,
        world_height = TILE_SIZE * 0.87,  # Slightly shorter
        remove_bg_color = dan_bg,
        foot_offset = 10,  # Increased to remove more from bottom
        hit_sheet = dan_hit_sheet  # Add hit sheet for Dan
    ))
    pos3 = tile_to_world(free_tiles[2])
    sprites.append(Enemy(
        x = pos3[0],
        y = pos3[1],
        sprite_sheet = cat_sheet,
        rows = 2,
        cols = 4,
        anim_speed = 150,
        world_height = TILE_SIZE * 0.78,  # Slightly shorter
        remove_bg_color = cat_bg,
        foot_offset = 8  # Increased to remove more from bottom
    ))
    pos4 = tile_to_world(free_tiles[3])
    sprites.append(Enemy(
        x = pos4[0],
        y = pos4[1],
        sprite_sheet = enemy_sheet,
        rows = 1,
        cols = 7,
        anim_speed = 150,
        world_height = TILE_SIZE * 0.62,  # Even shorter
        remove_bg_color = enemy_bg,
        foot_offset = 10  # Increased further to remove more from bottom
    ))
    pos5 = tile_to_world(free_tiles[4])
    sprites.append(Enemy(
        x = pos5[0],
        y = pos5[1],
        sprite_sheet = zombie_sheet,
        rows = 4,
        cols = 4,
        anim_speed = 150,
        world_height = TILE_SIZE * 0.9,  # Adjust height as needed
        remove_bg_color = zombie_bg,
        foot_offset = 10  # Adjust offset as needed
    ))

# Create enemies with hit animations - positioned in front of player
enemies = [
    Enemy(3.5 * TILE_SIZE, 3.5 * TILE_SIZE, dan_sheet, 4, 4, 100, TILE_SIZE * 0.8, (0, 0, 0), 0, dan_hit_sheet),
    Enemy(3.5 * TILE_SIZE, 4.5 * TILE_SIZE, dan_sheet, 4, 4, 100, TILE_SIZE * 0.8, (0, 0, 0), 0, dan_hit_sheet),
    Enemy(4.5 * TILE_SIZE, 3.5 * TILE_SIZE, dan_sheet, 4, 4, 100, TILE_SIZE * 0.8, (0, 0, 0), 0, dan_hit_sheet),
    Enemy(4.5 * TILE_SIZE, 4.5 * TILE_SIZE, dan_sheet, 4, 4, 100, TILE_SIZE * 0.8, (0, 0, 0), 0, dan_hit_sheet)
]

# --- Mouse Setup ---
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if gun.shoot():
                # Check if we hit any enemies
                for i, enemy in enumerate(sprites):
                    # Calculate distance to enemy
                    dx = enemy.x - player.x
                    dy = enemy.y - player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    # Calculate angle to enemy relative to player's angle
                    angle = math.atan2(dy, dx)
                    angle_diff = angle - player.angle
                    
                    # Normalize angle difference to be between -pi and pi
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    while angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                    
                    # Handle the case where the player is facing south (around 180 degrees)
                    if player.angle > math.pi/2 and angle_diff < -math.pi/2:
                        angle_diff += 2 * math.pi
                    elif player.angle < -math.pi/2 and angle_diff > math.pi/2:
                        angle_diff -= 2 * math.pi
                    
                    # Check if enemy is in front of player and within range
                    if abs(angle_diff) < 0.5 and distance < 300.0:
                        enemy.hit()  # Trigger hit animation
            else:
                print("Gun shoot() returned False - shooting not triggered")

    keys = pygame.key.get_pressed()
    player.update(keys)
    dx, _ = pygame.mouse.get_rel()
    player.angle += dx * 0.002
    gun.update()  # Update gun cooldown

    # --- Draw Sky ---
    sky_scaled = pygame.transform.scale(sky_texture, (WIDTH, baseline))
    screen.blit(sky_scaled, (0, 0))

    # --- Floor Casting ---
    floor_area_height = HEIGHT - baseline
    # Reduce resolution for better performance
    floor_width = WIDTH // 2
    floor_height = floor_area_height // 2
    floor_array = np.zeros((floor_width, floor_height, 3), dtype=np.uint8)
    
    # Calculate ray directions for floor casting
    rayDirX0 = math.cos(player.angle - FOV/2)
    rayDirY0 = math.sin(player.angle - FOV/2)
    rayDirX1 = math.cos(player.angle + FOV/2)
    rayDirY1 = math.sin(player.angle + FOV/2)
    
    # Pre-calculate some values
    floor_scale = TILE_SIZE / 64  # Assuming original texture is meant to cover 64 units
    tex_w = floor_texture.get_width()
    tex_h = floor_texture.get_height()
    
    # Pre-calculate distances for each row
    y_values = np.arange(floor_height)
    distances = (player.eye_height * d_proj) / (y_values + 0.0001)
    
    # Pre-calculate floor steps
    floorStepX = (rayDirX1 - rayDirX0) / floor_width
    floorStepY = (rayDirY1 - rayDirY0) / floor_width
    
    # Vectorized floor casting
    for y in range(floor_height):
        distance = distances[y]
        
        # Calculate starting point for floor casting
        floorX = player.x + distance * rayDirX0
        floorY = player.y + distance * rayDirY0
        
        # Calculate all x positions at once
        x_positions = np.arange(floor_width)
        floorX_array = floorX + x_positions * distance * floorStepX
        floorY_array = floorY + x_positions * distance * floorStepY
        
        # Calculate texture coordinates
        texX = (floorX_array * floor_scale).astype(int) % tex_w
        texY = (floorY_array * floor_scale).astype(int) % tex_h
        
        # Sample floor texture using numpy indexing
        floor_array[:, y, :] = floor_tex_array[texX, texY]
    
    # Scale up the floor surface to full resolution
    floor_surface = pygame.transform.scale(pygame.surfarray.make_surface(floor_array), (WIDTH, floor_area_height))
    screen.blit(floor_surface, (0, baseline))

    # --- Draw Walls and Sprites ---
    # First, collect all sprites and their distances
    visible_sprites = []
    for spr in sprites:
        spr.update(player, speed=0)
        dx = spr.x - player.x
        dy = spr.y - player.y
        distance = math.sqrt(dx * dx + dy * dy)
        sprite_angle = math.atan2(dy, dx)
        angle_diff = sprite_angle - player.angle
        
        # Normalize angle difference
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        # Check if sprite is in view
        if abs(angle_diff) < FOV/2:
            # Calculate which ray would hit this sprite
            ray_index = int((angle_diff + FOV/2) / FOV * NUM_RAYS)
            ray_index = max(0, min(ray_index, NUM_RAYS - 1))
            
            # Only add sprite if it's closer than the wall at that ray
            if distance < wall_distances[ray_index]:
                visible_sprites.append((distance, spr))
    
    # Sort sprites by distance (furthest first)
    visible_sprites.sort(reverse=True)
    
    # Draw walls
    cast_rays(screen, player, (HEIGHT // 2) + player.pitch)
    
    # Draw sprites in order of distance
    for _, spr in visible_sprites:
        # Check if sprite is in view
        dx = spr.x - player.x
        dy = spr.y - player.y
        distance = math.sqrt(dx * dx + dy * dy)
        sprite_angle = math.atan2(dy, dx)
        angle_diff = (sprite_angle - player.angle) % (2 * math.pi)
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        
        # Calculate which ray would hit this sprite
        ray_index = int((angle_diff + FOV/2) / FOV * NUM_RAYS)
        ray_index = max(0, min(ray_index, NUM_RAYS - 1))
        
        # Only set visible if sprite is closer than the wall at that ray
        is_visible = (abs(angle_diff) < math.pi / 2 and 
                     distance < 300 and 
                     distance < wall_distances[ray_index])
        
        spr.set_visibility(is_visible)
        spr.draw(screen, player.x, player.y, player.angle, FOV, WIDTH, HEIGHT, baseline)

    # --- Draw Gun ---
    gun.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
