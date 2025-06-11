import pygame

class Button:
    def __init__(self, x, y, width, height, text, main_color, hover_color, text_color, font_name='assets/game_font.ttf', font_size=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.main_color = main_color
        self.hover_color = hover_color
        self.current_color = main_color
        self.is_hovered = False

        try:
            self.font = pygame.font.Font(font_name, font_size)
        except FileNotFoundError:
            print(f"Warning: Font '{font_name}' not found. Falling back to default font.")
            self.font = pygame.font.Font(None, font_size)

        self.text_surf = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        # For smooth hover animation
        self.color_transition_speed = 10

    def draw(self, surface):
        # Smooth color transition on hover
        target_color = self.hover_color if self.is_hovered else self.main_color
        self.current_color = self._interpolate_color(self.current_color, target_color, self.color_transition_speed)

        # Draw shadow
        shadow_offset = 4
        shadow_color = (0, 0, 0, 50)
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, shadow_color, shadow_surface.get_rect(), border_radius=12)
        surface.blit(shadow_surface, (self.rect.x + shadow_offset, self.rect.y + shadow_offset))

        # Draw button
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=12)

        # Render and center text
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        surface.blit(self.text_surf, self.text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def _interpolate_color(self, current, target, speed):
        return tuple(int(c + (t - c) / speed) for c, t in zip(current, target))
