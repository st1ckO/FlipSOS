import pygame
from grid import Grid, is_on_grid
from ai_player import ComputerPlayer
from button import Button

# TODO:
# Add play again button (after game over) (Done)
# Fix state text (timer (like show "invalid move" for only 2secs), etc.)
# Add delay between skipping turns (AI and player)
# Hide valid moves when it's AI's turn or make the opacity of the valid moves less visible (DONE - Hid AI valid moves) (Done)
# UI improvements (font style and size, colors, etc.)
# LOW PRIO: token selection (S or O), AI difficulty, sounds, etc.

# Handles the Main game loop and grid logic
class FlipSOS:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.resolution = (1080, 720)
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('FlipSOS')
        self.clock = pygame.time.Clock()

        # --- Sound State & Control ---
        self.is_music_on = True
        try:
            pygame.mixer.music.load('assets/background_music.mp3')
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(loops=-1)
            
            icon_size = (48, 48)
            self.sound_on_icon = pygame.image.load('assets/volume-up.png').convert_alpha()
            self.sound_on_icon = pygame.transform.scale(self.sound_on_icon, icon_size)
            self.sound_off_icon = pygame.image.load('assets/volume-mute.png').convert_alpha()
            self.sound_off_icon = pygame.transform.scale(self.sound_off_icon, icon_size)
            
            padding = 15
            self.sound_icon_rect = self.sound_on_icon.get_rect(topleft=(padding, padding))

        except pygame.error as e:
            print(f"Warning: Could not load assets. Error: {e}")
            self.sound_on_icon = None
            self.sound_off_icon = None

        # --- Game State & Timers ---
        self.game_state = "HOME"
        self.skip_turn_timer = 0.0
        self.skip_turn_duration = 1.5
        self.is_handling_skip = False

        # --- Game Constants ---
        self.rows = 8
        self.columns = 8
        self.tokenSize = (72, 72)
        self.computerToken = 'O'
        self.playerToken = 'S'

        self.grid = None
        self.computerPlayer = None

        # --- Fonts & UI ---
        font_path = 'assets/Play-Bold.ttf'
        try:
            self.title_font = pygame.font.Font(font_path, 96)
            self.description_font = pygame.font.Font(font_path, 28)
            self.game_over_font = pygame.font.Font(font_path, 48)
            self.winner_font = pygame.font.Font(font_path, 36)
        except FileNotFoundError:
            print(f"Warning: Font '{font_path}' not found. Falling back to default font.")
            font_path = None
            self.title_font = pygame.font.Font(font_path, 96)
            self.description_font = pygame.font.Font(font_path, 28)
            self.game_over_font = pygame.font.Font(font_path, 48)
            self.winner_font = pygame.font.Font(font_path, 36)
            
        self.home_bg = self.create_home_background()
        
        # --- Button Instantiation ---
        button_width, button_height = 280, 70
        button_x = (self.resolution[0] - button_width) // 2
        
        # Position buttons lower for the new layout
        start_button_y = self.resolution[1] // 2 + 50
        
        BLUE = (30, 144, 255)
        LIGHT_BLUE = (100, 181, 246)
        RED = (220, 50, 50)
        LIGHT_RED = (239, 83, 80)
        GREEN = (67, 160, 71)
        LIGHT_GREEN = (129, 199, 132)
        WHITE_TEXT = (240, 240, 240)

        self.start_button = Button(button_x, start_button_y, button_width, button_height, "START", BLUE, LIGHT_BLUE, WHITE_TEXT, font_size=40)
        quit_button_y = start_button_y + button_height + 30
        self.quit_button = Button(button_x, quit_button_y, button_width, button_height, "QUIT", RED, LIGHT_RED, WHITE_TEXT, font_size=40)
        self.play_again_button = Button(button_x, self.resolution[1] // 2 + 60, button_width, button_height, "RETRY", GREEN, LIGHT_GREEN, WHITE_TEXT, font_size=40)
        
        self.overlay = pygame.Surface(self.resolution, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))

        self.running = True
        self.dt = 0

    def toggle_music(self):
        self.is_music_on = not self.is_music_on
        if self.is_music_on: pygame.mixer.music.unpause()
        else: pygame.mixer.music.pause()

    def create_home_background(self):
        bg_surface = pygame.Surface(self.resolution)
        bg_surface.fill((20, 20, 30))
        try:
            tile_img = pygame.image.load('assets/Sprite Sheet.png').convert_alpha()
            tile = pygame.transform.scale(tile_img.subsurface((192,0,192,192)), (96, 96))
            tile.set_alpha(30)
            for y in range(0, self.resolution[1], tile.get_height()):
                for x in range(0, self.resolution[0], tile.get_width()):
                    bg_surface.blit(tile, (x, y))
        except pygame.error:
            print("Warning: Could not load assets for home screen background.")
        return bg_surface

    def reset_game(self):
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self.playerToken, self)
        self.computerPlayer = ComputerPlayer(self.computerToken, 4, self.grid)
        self.game_state = "IN_GAME"
        self.is_handling_skip = False
        self.skip_turn_timer = 0.0

    def handle_skip(self):
        self.is_handling_skip = True
        self.skip_turn_timer = self.skip_turn_duration

    def run(self):
        while self.running:
            self.input()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000.0

    def input(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.game_state == "HOME":
            self.start_button.check_hover(mouse_pos)
            self.quit_button.check_hover(mouse_pos)
        elif self.game_state == "GAME_OVER":
            self.play_again_button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.sound_on_icon and self.sound_icon_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.toggle_music()
                    continue

            if self.game_state == "HOME":
                if self.start_button.check_click(event): self.reset_game()
                if self.quit_button.check_click(event): self.running = False

            elif self.game_state == "GAME_OVER":
                if self.play_again_button.check_click(event): self.reset_game()

            if self.game_state == "IN_GAME" and not self.is_handling_skip:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.grid.currentPlayer == self.playerToken and not self.grid.animating_tokens:
                        x_pixel, y_pixel = mouse_pos
                        grid_col = (x_pixel - self.tokenSize[0]) // self.tokenSize[0]
                        grid_row = (y_pixel - self.tokenSize[1]) // self.tokenSize[1]
                        clicked_coord = (grid_row, grid_col)

                        if is_on_grid(grid_row, grid_col) and clicked_coord in self.grid.validMoves:
                            self.grid.lastMove = clicked_coord
                            self.grid.flip_tiles(grid_row, grid_col)
                            if self.grid.switch_player(): self.handle_skip()
                            self.grid.check_game_over()
                            if self.grid.gameOver > 0: self.game_state = "GAME_OVER"
                        elif is_on_grid(grid_row, grid_col):
                            self.grid.stateText = ["INVALID MOVE"]

    def update(self):
        if self.game_state == "IN_GAME": self.grid.update_animations(self.dt)

        if self.is_handling_skip:
            self.skip_turn_timer -= self.dt
            if self.skip_turn_timer <= 0:
                self.is_handling_skip = False
                if self.grid.switch_player():
                    self.grid.bothSkipped = True
                    self.grid.check_game_over()
                    if self.grid.gameOver > 0: self.game_state = "GAME_OVER"
            return

        if self.game_state == "IN_GAME":
            if self.grid.currentPlayer == self.computerToken and not self.grid.animating_tokens:
                bestMove = self.computerPlayer.get_best_move_ab()
                if bestMove:
                    self.grid.lastMove = bestMove
                    self.grid.flip_tiles(bestMove[0], bestMove[1])
                if self.grid.switch_player(): self.handle_skip()
                self.grid.check_game_over()
                if self.grid.gameOver > 0: self.game_state = "GAME_OVER"

    def draw(self):
        if self.game_state == "HOME": self.draw_home_screen()
        elif self.game_state == "IN_GAME": self.draw_game_screen()
        elif self.game_state == "GAME_OVER":
            self.draw_game_screen()
            self.draw_game_over_overlay()
        
        if self.sound_on_icon:
            if self.is_music_on: self.screen.blit(self.sound_on_icon, self.sound_icon_rect)
            else: self.screen.blit(self.sound_off_icon, self.sound_icon_rect)
        pygame.display.update()

    # --- THIS METHOD WAS MISSING ---
    def draw_home_screen(self):
        self.screen.blit(self.home_bg, (0, 0))

        # --- Draw Title ---
        title_text = self.title_font.render("FlipSOS", True, (230, 230, 240))
        title_rect = title_text.get_rect(center=(self.resolution[0] // 2, self.resolution[1] // 2 - 180))
        shadow_text = self.title_font.render("FlipSOS", True, (20, 20, 20))
        self.screen.blit(shadow_text, title_rect.move(4, 4))
        self.screen.blit(title_text, title_rect)

        # --- Draw Game Description ---
        description_string = "Flip tiles, form SOS patterns, and beat your opponent!"
        desc_text_surf = self.description_font.render(description_string, True, (200, 200, 220))
        desc_shadow_surf = self.description_font.render(description_string, True, (20, 20, 20))
        
        desc_rect = desc_text_surf.get_rect(center=(self.resolution[0] // 2, title_rect.bottom + 80))

        self.screen.blit(desc_shadow_surf, desc_rect.move(2, 2))
        self.screen.blit(desc_text_surf, desc_rect)

        # --- Draw Buttons ---
        self.start_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def draw_game_screen(self):
        self.screen.fill((255, 255, 255))
        if self.grid:
            self.grid.draw_grid(self.screen)
            self.grid.draw_sidebar(self.screen)

    def draw_game_over_overlay(self):
        self.screen.blit(self.overlay, (0, 0))
        game_over_text = self.game_over_font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(self.resolution[0]//2, self.resolution[1]//2 - 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        if self.grid.gameOver == 1: winner_text = "PLAYER S WINS!"
        elif self.grid.gameOver == 2: winner_text = "PLAYER O WINS!"
        else: winner_text = "IT'S A DRAW!"
            
        winner_surf = self.winner_font.render(winner_text, True, (255, 255, 255))
        winner_rect = winner_surf.get_rect(center=(self.resolution[0]//2, self.resolution[1]//2 - 20))
        self.screen.blit(winner_surf, winner_rect)
        self.play_again_button.draw(self.screen)

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()