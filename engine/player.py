# engine/player.py
import math
import pygame

class Player:
    def __init__(self, x, y, angle=0):
        self.x = x  # Player's x-coordinate (float)
        self.y = y  # Player's y-coordinate (float)
        self.angle = angle  # Player's viewing angle in radians

    def update(self, keys, move_speed=3, rot_speed=0.03):
        # Forward and backward movement:
        if keys[pygame.K_w]:
            self.x += move_speed * math.cos(self.angle)
            self.y += move_speed * math.sin(self.angle)
        if keys[pygame.K_s]:
            self.x -= move_speed * math.cos(self.angle)
            self.y -= move_speed * math.sin(self.angle)
        
        # Rotation: turning left and right.
        if keys[pygame.K_a]:
            self.angle -= rot_speed
        if keys[pygame.K_d]:
            self.angle += rot_speed
