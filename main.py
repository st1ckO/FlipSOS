import pygame
from grid import Grid, is_on_grid
from ai_player import ComputerPlayer
from button import Button

# TODO:
# Add play again button (after game over)
# Fix state text (timer (like show "invalid move" for only 2secs), etc.)
# Add delay between skipping turns (AI and player)
# Hide valid moves when it's AI's turn or make the opacity of the valid moves less visible (DONE - Hid AI valid moves)
# UI improvements (font style and size, colors, etc.)
# LOW PRIO: token selection (S or O), AI difficulty, sounds, etc.

# Handles the Main game loop and grid logic
class FlipSOS:
    def __init__(self):
        pygame.init()
        self.resolution = (1080, 720)
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('FlipSOS')
        self.clock = pygame.time.Clock()

        self.rows = 8
        self.columns = 8
        self.tokenSize = (72, 72)
        self.computerToken = 'O'
        self.playerToken = 'S'
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self.playerToken, self)
        self.computerPlayer = ComputerPlayer(self.computerToken, 4, self.grid)

        # Play Again button
        button_width, button_height = 250, 60
        button_x = (self.resolution[0] - button_width) // 2
        button_y = self.resolution[1] // 2 + 50
        self.play_again_button = Button(
            button_x, button_y, button_width, button_height,
            "PLAY AGAIN", (100, 230, 100), (150, 255, 150), (0, 0, 0), 36
        )

        # Game over overlay
        self.overlay = pygame.Surface(self.resolution, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Game over font
        self.game_over_font = pygame.font.Font('assets/arial.ttf', 48)
        self.winner_font = pygame.font.Font('assets/arial.ttf', 36)

        self.running = True
        self.dt = 0

    def reset_game(self):
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self)
        self.computerPlayer = ComputerPlayer(self.computerToken, 4, self.grid)

    def draw_game_over(self):
        # Draw semi-transparent overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.game_over_font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(self.resolution[0]//2, self.resolution[1]//2 - 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw winner text
        if self.grid.gameOver == 1:
            winner_text = "PLAYER S WINS!"
        elif self.grid.gameOver == 2:
            winner_text = "PLAYER O WINS!"
        else:
            winner_text = "IT'S A DRAW!"
            
        winner_surf = self.winner_font.render(winner_text, True, (255, 255, 255))
        winner_rect = winner_surf.get_rect(center=(self.resolution[0]//2, self.resolution[1]//2 - 20))
        self.screen.blit(winner_surf, winner_rect)
        
        # Draw the play again button
        self.play_again_button.draw(self.screen)

    def run(self):
        while self.running:
            self.input()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000.0

    def input(self):
        mouse_pos = pygame.mouse.get_pos()
        self.play_again_button.check_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.grid.gameOver > 0:
                    if self.play_again_button.is_clicked(mouse_pos, event):
                        self.reset_game()
                        continue
                
                if event.button == 1 and self.grid.gameOver == 0:
                    x_pixel, y_pixel = pygame.mouse.get_pos()
                    grid_col = (x_pixel - self.tokenSize[0]) // self.tokenSize[0]
                    grid_row = (y_pixel - self.tokenSize[1]) // self.tokenSize[1]

                    clicked_coord = (grid_row, grid_col)

                    if not is_on_grid(grid_row, grid_col):
                        print("Clicked outside grid")
                        continue

                    if clicked_coord not in self.grid.validMoves:
                        self.grid.stateText = ["INVALID MOVE"]
                    else:
                        self.grid.lastMove = clicked_coord 
                        self.grid.flip_tiles(grid_row, grid_col)
                        self.grid.switch_player() 
                        self.grid.check_game_over() 

    def update(self):
        if self.grid.gameOver == 0 and self.grid.currentPlayer == self.computerToken and not self.grid.animating_tokens:
            bestMove = self.computerPlayer.get_best_move()
            if bestMove:
                self.grid.lastMove = bestMove 
                self.grid.flip_tiles(bestMove[0], bestMove[1])
                self.grid.switch_player()
                self.grid.check_game_over()
            else:
                print("BUG: No valid moves for AI player.")

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.grid.draw_grid(self.screen)
        self.grid.draw_sidebar(self.screen)
        self.grid.update_animations(self.dt)
        
        # Draw game over screen if game is over
        if self.grid.gameOver > 0:
            self.draw_game_over()
            
        pygame.display.update()

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()