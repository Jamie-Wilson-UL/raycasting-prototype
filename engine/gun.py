import pygame
from engine.constants import WIDTH, HEIGHT

class Gun:
    def __init__(self, image_path):
        # Load the sprite sheet
        sprite_sheet = pygame.image.load(image_path).convert_alpha()
        
        # Get the background color from the top-left pixel
        bg_color = sprite_sheet.get_at((0, 0))[:3]
        
        # Calculate frame dimensions
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        frame_width = sheet_width // 2
        frame_height = sheet_height // 2
        
        # Extract and process all frames
        self.frames = []
        for row in range(2):
            for col in range(2):
                # Extract frame
                frame = sprite_sheet.subsurface(pygame.Rect(
                    col * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height
                )).copy()
                
                # Create new surface with alpha
                new_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                
                # Copy pixels, making background transparent
                for x in range(frame_width):
                    for y in range(frame_height):
                        pixel = frame.get_at((x, y))
                        if (abs(pixel[0] - bg_color[0]) > 30 or
                            abs(pixel[1] - bg_color[1]) > 30 or
                            abs(pixel[2] - bg_color[2]) > 30):
                            new_frame.set_at((x, y), pixel)
                
                # Scale down the frame
                scaled_width = int(frame_width * 0.8)  # 80% of original size
                scaled_height = int(frame_height * 0.8)
                new_frame = pygame.transform.scale(new_frame, (scaled_width, scaled_height))
                
                self.frames.append(new_frame)
        
        # Animation state
        self.current_frame = 0
        self.animation_speed = 2  # Frames per animation step
        self.animation_counter = 0
        self.is_shooting = False
        
        # Position the gun
        self.rect = self.frames[0].get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT + 15  # Move further below screen bottom
        
        # Shooting mechanics
        self.shoot_cooldown = 0
        self.max_cooldown = 15  # Reduced from 30 to 15 frames (0.25 seconds at 60 FPS)
        
    def update(self):
        # Update shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Update animation
        if self.is_shooting:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % 4
                if self.current_frame == 0:  # Animation complete
                    self.is_shooting = False
            
    def shoot(self):
        if self.shoot_cooldown == 0:  # Only check cooldown
            self.shoot_cooldown = self.max_cooldown
            self.is_shooting = True
            self.current_frame = 1  # Start animation from second frame
            return True
        return False
        
    def draw(self, screen):
        screen.blit(self.frames[self.current_frame], self.rect) 