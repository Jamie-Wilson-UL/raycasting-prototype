import math
import pygame
from engine.raycaster import wall_distances, NUM_RAYS, SCALE, TILE_SIZE, d_proj
from engine.constants import WIDTH, HEIGHT

# Define a constant for field-of-view used in sprite projection.
FOV = math.pi / 3  # 60° field-of-view

class Enemy:
    def __init__(self, x, y, sprite_sheet, rows, cols, anim_speed,
                 world_height, remove_bg_color, foot_offset=0, hit_sheet=None):
        """
        x, y: World position of the enemy's anchor (typically its center).
        sprite_sheet: A surface containing the enemy's animation frames.
        rows, cols: Number of rows and columns in the sprite sheet.
        anim_speed: Time (in ms) between animation frame changes.
        world_height: The height (in world units) the enemy occupies.
        remove_bg_color: A color tuple (RGB) which will be set as transparent.
        foot_offset: Extra pixel offset to lower the visible sprite so that its feet align with the ground.
        hit_sheet: Optional sprite sheet for hit animation.
        """
        self.x = x
        self.y = y
        self.world_height = world_height
        self.foot_offset = foot_offset
        self.anim_speed = anim_speed
        self.frames = self.slice_sprite_sheet(sprite_sheet, rows, cols, remove_bg_color)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        
        # Hit animation state
        self.is_hit = False
        self.hit_frames = []
        if hit_sheet is not None:
            self.hit_frames = self.slice_sprite_sheet(hit_sheet, 2, 2, remove_bg_color)
        self.hit_frame = 0
        self.hit_animation_speed = 300
        self.hit_last_update = 0
        self.hit_complete = False
        self.alpha = 0
        self.fade_speed = 10
        self.is_visible = False

    def slice_sprite_sheet(self, sheet, rows, cols, remove_bg_color):
        """
        Slices a sprite sheet into a list of frame surfaces with proper alpha transparency.
        Also detects the bottom of the sprite to help with floor alignment.
        """
        frames = []
        # Convert to RGBA for proper alpha handling
        sheet = sheet.convert_alpha()
        sheet_rect = sheet.get_rect()
        frame_width = sheet_rect.width // cols
        frame_height = sheet_rect.height // rows
        
        # Store the lowest non-transparent pixel for each frame
        self.frame_bottoms = []
        
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
                frame = sheet.subsurface(rect).copy()
                
                if remove_bg_color is not None:
                    # Create a new surface with per-pixel alpha
                    new_frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    
                    # Define color tolerance for background removal
                    tolerance = 30  # Adjust this value if needed
                    
                    # Find the bottom of the sprite (first non-transparent pixel from bottom)
                    bottom_y = frame_height - 1
                    for y in range(frame_height - 1, -1, -1):
                        row_has_content = False
                        for x in range(frame_width):
                            pixel = frame.get_at((x, y))
                            # Check if pixel color is close to background color
                            if (abs(pixel[0] - remove_bg_color[0]) >= tolerance or
                                abs(pixel[1] - remove_bg_color[1]) >= tolerance or
                                abs(pixel[2] - remove_bg_color[2]) >= tolerance):
                                row_has_content = True
                                break
                        if row_has_content:
                            bottom_y = y
                            break
                    
                    # Copy pixels from original frame, setting alpha to 0 for background color
                    for x in range(frame_width):
                        for y in range(frame_height):
                            pixel = frame.get_at((x, y))
                            # Check if pixel color is close to background color
                            if (abs(pixel[0] - remove_bg_color[0]) < tolerance and
                                abs(pixel[1] - remove_bg_color[1]) < tolerance and
                                abs(pixel[2] - remove_bg_color[2]) < tolerance):
                                new_frame.set_at((x, y), (0, 0, 0, 0))  # Transparent
                            else:
                                new_frame.set_at((x, y), pixel)
                    
                    frame = new_frame
                    self.frame_bottoms.append(bottom_y)
                else:
                    # For sprites with alpha channel, find the bottom non-transparent pixel
                    bottom_y = frame_height - 1
                    for y in range(frame_height - 1, -1, -1):
                        row_has_content = False
                        for x in range(frame_width):
                            if frame.get_at((x, y))[3] > 0:  # Check alpha channel
                                row_has_content = True
                                break
                        if row_has_content:
                            bottom_y = y
                            break
                    self.frame_bottoms.append(bottom_y)
                
                frames.append(frame)
        return frames

    def hit(self):
        """Start the hit animation if we have hit frames."""
        if self.hit_frames and not self.hit_complete:
            self.is_hit = True
            self.hit_frame = 0
            self.hit_last_update = pygame.time.get_ticks()
            self.hit_complete = False

    def update(self, player, speed=0):
        """
        Updates the animation frame based on elapsed time.
        The speed parameter is unused (kept for compatibility).
        """
        now = pygame.time.get_ticks()
        
        # Update hit animation if active
        if self.is_hit:
            if now - self.hit_last_update > self.hit_animation_speed:
                self.hit_last_update = now
                self.hit_frame += 1
                if self.hit_frame >= len(self.hit_frames):
                    self.hit_frame = len(self.hit_frames) - 1
                    self.hit_complete = True
                    pygame.time.set_timer(pygame.USEREVENT, 500)
        # Update normal animation if not hit
        elif not self.hit_complete and now - self.last_update > self.anim_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Update fade-in effect
        if self.is_visible and self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
        elif not self.is_visible and self.alpha > 0:
            self.alpha = max(0, self.alpha - self.fade_speed)

    def draw(self, screen, player_x, player_y, player_angle, fov, screen_width, screen_height, baseline):
        # Calculate distance and angle to player
        dx = self.x - player_x
        dy = self.y - player_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle to sprite
        sprite_angle = math.atan2(dy, dx)
        angle_diff = (sprite_angle - player_angle) % (2 * math.pi)
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
            
        # Check if sprite is in view
        if abs(angle_diff) < fov/2:
            # Calculate screen position
            screen_x = (angle_diff + fov/2) * (screen_width / fov)
            
            # Calculate sprite size based on distance
            sprite_height = (TILE_SIZE * d_proj) / distance
            sprite_width = sprite_height * (self.frames[self.current_frame].get_width() / self.frames[self.current_frame].get_height())
            
            # Calculate sprite position
            sprite_y = baseline - sprite_height/2
            
            # Select frame based on hit state
            if self.is_hit and self.hit_frames:
                frame = self.hit_frames[self.hit_frame]
            else:
                frame = self.frames[self.current_frame]
                
            # Scale frame
            scaled_frame = pygame.transform.scale(frame, (int(sprite_width), int(sprite_height)))
            
            # Apply fade effect
            scaled_frame.set_alpha(self.alpha)
            
            # Draw sprite
            screen.blit(scaled_frame, (screen_x - sprite_width/2, sprite_y))

    def set_visibility(self, is_visible):
        self.is_visible = is_visible
