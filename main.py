import pygame

# Utility Functions
def loadImage(path, size):
    img = pygame.image.load(path).convert_alpha() # To make png transparent
    img = pygame.transform.scale(img, size)
    return img

# Main Game Class
class FlipSOS:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('FlipSOS')
        
        self.rows = 8
        self.columns = 8
        self.grid = Grid(self.rows, self.columns, (48, 48), self)
        
        self.running = True
        
    def run(self):
        # Main game loop
        while self.running == True:
            self.input()
            self.update()
            self.draw()
            
    def input(self):
        # Handle window close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # For debugging, print the board
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.grid.printBoard()
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((0, 0, 0)) # RGB Format
        
        pygame.display.update()
        
class Grid:
    def __init__(self, rows, columns, tokenSize, gameClass): 
        self.gameClass = gameClass
        self.y = rows
        self.x = columns
        self.tokenSize = tokenSize
        self.sToken = loadImage('assets/S.png', tokenSize)
        self.oToken = loadImage('assets/O.png', tokenSize)
        
        self.gridLogic = self.regenGrid(self.y, self.x)
        
    def regenGrid(self, rows, columns):
        # Generates empty grid for game logic
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)

        return grid
    
    def printBoard(self):
        # Prints the grid to the console for debugging
        for row in self.gridLogic:
            print(row)

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()