import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font('assets/arial.ttf', font_size)
        self.is_hovered = False
        self.shadow_offset = 3
        self.click_offset = 2
        
    def draw(self, surface):
        # Draw shadow
        shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset)
        pygame.draw.rect(surface, (50, 50, 50, 150), shadow_rect, border_radius=10)
        
        # Draw button
        color = self.hover_color if self.is_hovered else self.color
        pos = self.rect.topleft
        if self.is_hovered and pygame.mouse.get_pressed()[0]:
            pos = (pos[0] + self.click_offset, pos[1] + self.click_offset)
        
        button_rect = pygame.Rect(pos, self.rect.size)
        pygame.draw.rect(surface, color, button_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), button_rect, 2, border_radius=10)  # Border
        
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False
