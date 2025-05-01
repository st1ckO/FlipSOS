import pygame
from grid import Grid

# TODO:
# HIGH PRIO: AI player logic (Fixed-Depth Heuristic Search)
# Fix state text (sequence, timer, etc.)
# Fix game over logic (stop updating state text, add play again button, etc.)
# Clean up code (add comments, remove complicated methods in infinite loops if possible, arrange methods logically, etc.)
# LOW PRIO: token selection (S or O), AI difficulty, animations, sounds, etc.

# Handles the Main game loop and grid logic
class FlipSOS:
    def __init__(self):
        pygame.init()
        self.resolution = (1080, 720)
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('FlipSOS')
        
        self.rows = 8
        self.columns = 8
        self.tokenSize = (72, 72)
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self)
        
        self.running = True
        
    def run(self):
        # Main game loop
        while self.running:
            self.input()
            self.update()
            self.draw()
            
    def input(self):
        # Handle window close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # For debugging, print the board
                if event.button == 3:
                    self.grid.print_board()
                
                # Place a token based on player input
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    x, y = (x - self.tokenSize[0]) // self.tokenSize[0], (y - self.tokenSize[1]) // self.tokenSize[1]
                    
                    if (y, x) not in self.grid.validMoves:
                        self.grid.stateText = ["INVALID MOVE"]
                    else:
                        self.grid.lastMove = (y, x) # Save the last move for drawing the red circle
                        self.grid.flip_tiles(y, x) 
                        self.grid.switch_player()
                        self.grid.check_game_over()
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((255, 255, 255)) # RRGGBB Format
        self.grid.draw_grid(self.screen)
        self.grid.draw_sidebar(self.screen)
        pygame.display.update()

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()