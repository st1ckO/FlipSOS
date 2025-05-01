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
        
        self.playerO = 'O'
        self.playerS = 'S'
        self.currentPlayer = 'S'
        
        self.rows = 8
        self.columns = 8
        self.tokenSize = (72, 72)
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self)
        
        self.validMoves = self.grid.find_valid_moves(self.grid.gridLogic, self.currentPlayer)
        self.lastMove = None
        self.gameOver = False
        
        self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
        self.sScore, self.oScore = self.calculate_score(self.grid.gridLogic)
        
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
                    
                    if (y, x) not in self.validMoves:
                        self.stateText = ["INVALID MOVE"]
                    else:
                        self.lastMove = (y, x) # Save the last move for drawing the red circle
                        swappableTiles = self.grid.find_swappable_tiles(y, x, self.grid.gridLogic, self.currentPlayer) 
                        
                        # Flip all the tokens in the direction of the move
                        for tile in swappableTiles:
                            self.grid.add_token(self.grid.gridLogic, self.currentPlayer, tile[0], tile[1])
                            
                        self.sScore, self.oScore = self.calculate_score(self.grid.gridLogic)
                        
                        self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS # Switch player
                        self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
                        self.validMoves = self.grid.find_valid_moves(self.grid.gridLogic, self.currentPlayer)
                        
                        # Handle Skips
                        if self.validMoves == []:
                            self.stateText = [f"NO VALID MOVE", "TURN SKIPPED"]
                            self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS
                            self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
                            self.validMoves = self.grid.find_valid_moves(self.grid.gridLogic, self.currentPlayer)
                            
                            # Both players skipped
                            if self.validMoves == []:
                                self.stateText = ["BOTH SKIPPED", "GAME OVER"]    
                                self.gameOver = True   
                    
                        if self.gameOver:
                            if self.sScore > self.oScore:
                                self.stateText = ["PLAYER S WINS", "GAME OVER"]
                            elif self.oScore > self.sScore:
                                self.stateText = ["PLAYER O WINS", "GAME OVER"]
                            else:
                                self.stateText = ["DRAW", "GAME OVER"]
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((255, 255, 255)) # RRGGBB Format
        self.grid.draw_grid(self.screen)
        self.grid.draw_sidebar(self.screen, self.sScore, self.oScore, self.stateText)
        pygame.display.update()
        
    def calculate_score(self, grid):
        # Calculate the score of each player
        sScore = 0
        oScore = 0
        
        for row in grid:
            for cell in row:
                if cell == 'S':
                    sScore += 1
                elif cell == 'O':
                    oScore += 1
                    
        if sScore + oScore == self.rows * self.columns:
            self.gameOver = True
        
        return sScore, oScore
    
    def find_patterns():
        pass

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()