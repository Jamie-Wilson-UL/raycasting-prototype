import math
import pygame

class Player:
    def __init__(self, x, y, angle=0, eye_height=96, pitch=-64):
        # (x, y) is the player's position on the floor.
        self.x = x
        self.y = y
        self.angle = angle
        self.eye_height = eye_height      # Height of the eyes above the floor.
        self.pitch = pitch                # Vertical offset (negative raises the view).
        self.move_speed = 3.0             # Default movement speed
        self.rot_speed = 0.08            # Default rotation speed

    def update(self, keys):
        if keys[pygame.K_w]:
            self.x += self.move_speed * math.cos(self.angle)
            self.y += self.move_speed * math.sin(self.angle)
        if keys[pygame.K_s]:
            self.x -= self.move_speed * math.cos(self.angle)
            self.y -= self.move_speed * math.sin(self.angle)
        if keys[pygame.K_a]:
            self.x += self.move_speed * math.cos(self.angle - math.pi/2)
            self.y += self.move_speed * math.sin(self.angle - math.pi/2)
        if keys[pygame.K_d]:
            self.x += self.move_speed * math.cos(self.angle + math.pi/2)
            self.y += self.move_speed * math.sin(self.angle + math.pi/2)
