import pygame

class Token:
    def __init__(self, player, gridX, gridY, tokenSize, image, s_image, o_image):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.original_width = tokenSize[0] - 2 
        self.token_height = tokenSize[1] - 2
        self.posX = tokenSize[0] + (gridY * tokenSize[0]) + 1 
        self.posY = tokenSize[1] + (gridX * tokenSize[1]) + 1 
        self.image = image
        self.s_image = s_image 
        self.o_image = o_image 

        # Animation attributes
        self.is_animating = False
        self.animation_progress = 0.0 
        self.animation_duration = 0.5 
        self.target_player = None
        self.target_image = None
        self.scale_x = 1.0
        self.max_animation_dt = 1 / 30

    def start_flip_animation(self, target_player):
        if self.player == target_player: 
             return
        self.is_animating = True
        self.animation_progress = 0.0
        self.target_player = target_player
        self.target_image = self.s_image if target_player == 'S' else self.o_image

    def update(self, dt):
        if not self.is_animating:
            return

        # --- Use clamped dt for animation progress ---
        effective_dt = min(dt, self.max_animation_dt)
        self.animation_progress += effective_dt / self.animation_duration
        # ------------------------------------------

        half_progress = 0.5

        if self.animation_progress >= 1.0:
            # Animation finished
            self.is_animating = False
            self.animation_progress = 1.0
            self.player = self.target_player 
            self.image = self.target_image   
            self.scale_x = 1.0
        elif self.animation_progress >= half_progress:

            if self.image != self.target_image:
                 self.image = self.target_image 
            self.scale_x = (self.animation_progress - half_progress) / half_progress
        else:
            self.scale_x = 1.0 - (self.animation_progress / half_progress)

        self.scale_x = max(0.0, min(1.0, self.scale_x))


    def draw(self, displayWindow):
        if self.is_animating:
            scaled_width = int(self.original_width * self.scale_x)
            scaled_height = self.token_height 

            if scaled_width <= 0: 
                return 

            current_image_being_drawn = self.target_image if self.animation_progress >= 0.5 else self.image
            if self.animation_progress >= 0.5 and self.image != self.target_image:
                 current_image_being_drawn = self.target_image

            try:
                scaled_surface = pygame.transform.scale(current_image_being_drawn, (scaled_width, scaled_height))
            except ValueError:
                return # Skip drawing if scale failed

            offset_x = (self.original_width - scaled_width) // 2
            draw_pos_x = self.posX + offset_x

            displayWindow.blit(scaled_surface, (draw_pos_x, self.posY))
        else:
            displayWindow.blit(self.image, (self.posX, self.posY))