import pygame
from grid import Grid, is_on_grid
from ai_player import ComputerPlayer

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
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self)
        self.computerPlayer = ComputerPlayer('O', 4, self.grid)

        self.running = True
        self.dt = 0

    def run(self):
        # Main game loop
        while self.running:
            self.input()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000.0

    def input(self):
        # Handle window close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # For debugging, print the board
                # if event.button == 3:
                    # self.grid.print_board()

                # Place a token based on player input
                if event.button == 1:
                    if self.grid.gameOver == 0:
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
                    else:
                        print("Game Over - Cannot make moves.")

    def update(self):
        if self.grid.currentPlayer == 'O' and not self.grid.animating_tokens and self.grid.gameOver == 0:
            bestMove = self.computerPlayer.get_best_move() # Switch to get_best_move_ab() for alpha-beta pruning
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
        pygame.display.update()

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()