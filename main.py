import pygame
from grid import Grid

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
        
        self.validMoves = self.grid.findValidMoves(self.grid.gridLogic, self.currentPlayer)
        self.lastMove = None
        self.gameOver = True
        
        self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
        self.sScore, self.oScore = self.grid.calculateScore(self.grid.gridLogic)
        
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
                    self.grid.printBoard()
                
                # Place a token based on player input
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    x, y = (x - self.tokenSize[0]) // self.tokenSize[0], (y - self.tokenSize[1]) // self.tokenSize[1]
                    
                    if (y, x) not in self.validMoves:
                        self.stateText = ["INVALID MOVE"]
                    else:
                        self.grid.addToken(self.grid.gridLogic, self.currentPlayer, y, x) # Add the token to the grid logic
                        self.lastMove = (y, x) # Save the last move for drawing the red circle
                        swappableTiles = self.grid.findSwappableTiles(y, x, self.grid.gridLogic, self.currentPlayer) 
                        
                        # Flip all the tokens in the direction of the move
                        for tile in swappableTiles:
                            self.grid.addToken(self.grid.gridLogic, self.currentPlayer, tile[0], tile[1])
                            
                        self.sScore, self.oScore = self.grid.calculateScore(self.grid.gridLogic)
                        self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS # Switch player
                        self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
                        self.validMoves = self.grid.findValidMoves(self.grid.gridLogic, self.currentPlayer)
                        print(self.validMoves)
                        
                        # Handle Skips
                        if self.validMoves == []:
                            self.stateText = [f"NO VALID MOVE", "TURN SKIPPED"]
                            self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS
                            self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
                            self.validMoves = self.grid.findValidMoves(self.grid.gridLogic, self.currentPlayer)
                            
                            # Both players skipped
                            if self.validMoves == []:
                                self.stateText = ["BOTH SKIPPED", "GAME OVER"]       
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((255, 255, 255)) # RRGGBB Format
        self.grid.drawGrid(self.screen)
        self.grid.draw_sidebar(self.screen, self.sScore, self.oScore, self.stateText)
        pygame.display.update()

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()