import pygame

# Utility Functions
def loadImage(path, size):
    img = pygame.image.load(path).convert_alpha() # To make png transparent
    img = pygame.transform.scale(img, size)
    return img

def extractSprite(sheet, x, y, scaleSize, size):
    # Extract a sprite from a sprite sheet
    sprite = pygame.Surface((size[0], size[1])).convert_alpha() # size parameter is the size of each sprite in the sheet
    sprite.blit(sheet, (0, 0), (x * size[0], y * size[1], size[0], size[1])) 
    sprite = pygame.transform.scale(sprite, scaleSize)
    return sprite

# Handles the Main game loop and grid logic
class FlipSOS:
    def __init__(self):
        pygame.init()
        self.resolution = (1080, 720)
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('FlipSOS')
        
        self.playerO = 'O'
        self.playerS= 'S'
        self.currentPlayer = 'S'
        
        self.rows = 8
        self.columns = 8
        self.tokenSize = (72, 72)
        self.grid = Grid(self.rows, self.columns, self.tokenSize, self)
        
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
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # For debugging, print the board
                if event.button == 3:
                    self.grid.printBoard()
                
                # Place a token based on player input
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    x, y = (x - self.tokenSize[0]) // self.tokenSize[0], (y - self.tokenSize[1]) // self.tokenSize[1]
                    self.grid.addToken(self.grid.gridLogic, self.currentPlayer, y, x)
                    self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((173, 216, 230)) # RRGGBB Format
        self.grid.drawGrid(self.screen)
        pygame.display.update()

# Handles the grid design and logic       
class Grid:
    def __init__(self, rows, columns, tokenSize, gameClass): 
        self.gameClass = gameClass
        self.y = rows
        self.x = columns
        self.tokenSize = tokenSize
        self.resizedToken = (tokenSize[0] - 2, tokenSize[1] - 2)
        self.sToken = loadImage('assets/S.png', self.resizedToken)
        self.oToken = loadImage('assets/O.png', self.resizedToken)
        self.tokens = {}
        self.bgDict = self.loadBackgroundImages()
        self.bg = self.createBackground()
        self.gridLogic = self.regenGrid(self.y, self.x)
        
    def loadBackgroundImages(self):
        # Load background images for the grid 
        # Extracts the images from the sprite sheet and scales them to the token size
        imageDict = {}
        xAlpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        spriteSheet = pygame.image.load('assets/Sprite Sheet.png').convert_alpha()
        spriteActualSize = (192, 192)
        
        for y in range(3):
            for x in range(7):
                imageDict[xAlpha[x] + str(y)] = extractSprite(spriteSheet, x, y, self.tokenSize, spriteActualSize)
        
        return imageDict
    
    def createBackground(self):
        # Create the background for the grid using the loaded images (specific for 8x8 grid)
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],
            ['C1', 'A0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'G0', 'E1'],
            ['C1', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'E1'],
            ['C1', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'E1'],
            ['C1', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'E1'],
            ['C1', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'E1'],
            ['C1', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'E1'],
            ['C1', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'E1'],
            ['C1', 'A2', 'F0', 'B0', 'F0', 'B0', 'F0', 'B0', 'G2', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],
        ]
        background = pygame.Surface(((self.x + 2) * self.tokenSize[0], (self.y + 2) * self.tokenSize[1])).convert_alpha()
        background.set_colorkey('Black')
        
        for y, row in enumerate(gridBg):
            for x, sprite in enumerate(row):
                background.blit(self.bgDict[sprite], (x * self.tokenSize[0], y * self.tokenSize[1]))
        
        return background
                
        
    def regenGrid(self, rows, columns):
        # Generates empty grid for game logic
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append('-')
            grid.append(line)
            
        # Add starting tokens
        self.addToken(grid, 'O', 3, 3)
        self.addToken(grid, 'S', 3, 4)
        self.addToken(grid, 'O', 4, 4)
        self.addToken(grid, 'S', 4, 3)

        return grid
    
    def drawGrid(self, displayWindow):
        displayWindow.blit(self.bg, (0, 0))
        
        for token in self.tokens.values():
            token.draw(displayWindow)
    
    def printBoard(self):
        # Prints the grid to the console for debugging
        print('Current Board:')
        for row in self.gridLogic:
            print(row)
            
    def addToken(self, grid, player, y, x):
        tokenImage = self.oToken if player == 'O' else self.sToken
        self.tokens[(y, x)] = Token(player, y, x, self.tokenSize, tokenImage, self.gameClass)
        grid[y][x] = self.tokens[(y, x)].player
            
class Token:
    def __init__(self, player, gridX, gridY, tokenSize, image, gameClass):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = tokenSize[0] + (gridY * tokenSize[0])
        self.posY = tokenSize[1] + (gridX * tokenSize[1] + 4)
        self.gameClass = gameClass
        self.image = image
        
    def transition(self):
        pass
    
    def draw(self, displayWindow):
        displayWindow.blit(self.image, (self.posX, self.posY))

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()