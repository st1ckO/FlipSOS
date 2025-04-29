import pygame
from sos_token import Token

# Utility functions
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

def findValidDirections(x, y, minX=0, minY=0, maxX=7, maxY=7):
    # Returns a list of valid directions to move in the grid (Basically, directions that doesn't get out of bounds)
    validDirections = []
    
    if y != minY: validDirections.append((x, y - 1)) # Up
    if x != maxX and y != minY: validDirections.append((x + 1, y - 1)) # Up-right
    if x != maxX: validDirections.append((x + 1, y)) # Right
    if x != maxX and y != maxY: validDirections.append((x + 1, y + 1)) # Down-right
    if y != maxY: validDirections.append((x, y + 1)) # Down
    if x != minX and y != maxY: validDirections.append((x - 1, y + 1)) # Down-left
    if x != minX: validDirections.append((x - 1, y)) # Left
    if x != minX and y != minY: validDirections.append((x - 1, y - 1)) # Up-left
                
    return validDirections

# Handles the grid design and logic       
class Grid:
    def __init__(self, rows, columns, tokenSize, gameClass): 
        self.gameClass = gameClass
        self.y = rows
        self.x = columns
        self.tokenSize = tokenSize
        self.resizedToken = (tokenSize[0] - 2, tokenSize[1] - 2)
        self.validTokenSize = (tokenSize[0] - 5, tokenSize[1] - 5)
        self.sToken = loadImage('assets/S.png', self.resizedToken)
        self.oToken = loadImage('assets/O.png', self.resizedToken)
        self.validToken = loadImage('assets/Valid_Moves.png', self.validTokenSize)
        self.tokens = {}
        self.bgDict = self.loadBackgroundImages()
        self.bg = self.createBackground()
        self.gridLogic = self.regenGrid(self.y, self.x)
        self.sidebar = loadImage('assets/Sidebar.png', (360, 720))
        self.scoreFont = pygame.font.Font('C:\Windows\Fonts\Arial.ttf', 60)
        self.stateFont = pygame.font.Font('C:\Windows\Fonts\Arial.ttf', 28)
        
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
    
    def addToken(self, grid, player, y, x):
        # Adds a token to the grid and updates the grid logic
        tokenImage = self.oToken if player == 'O' else self.sToken
        self.tokens[(y, x)] = Token(player, y, x, self.tokenSize, tokenImage, self.gameClass)
        grid[y][x] = self.tokens[(y, x)].player
        
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

        for move in self.gameClass.validMoves:
            displayWindow.blit(self.validToken, (move[1] * self.tokenSize[0] + self.tokenSize[0] + 2, move[0] * self.tokenSize[1] + self.tokenSize[1] + 2))
        
        # Draw red circle on last clicked cell
        if self.gameClass.lastMove:
            y, x = self.gameClass.lastMove
            centerX = x * self.tokenSize[0] + self.tokenSize[0] + self.tokenSize[0] // 2
            centerY = y * self.tokenSize[1] + self.tokenSize[1] + self.tokenSize[1] // 2
            pygame.draw.circle(displayWindow, (255, 0, 0), (centerX, centerY), 6)  
            
    def draw_sidebar(self, displayWindow, sScore, oScore, stateText):
        displayWindow.blit(self.sidebar, (720, 0)) # Blit the sidebar to the right
        
        # Draw overlay text
        sScoreText = self.scoreFont.render(f"{sScore}", True, (0, 0, 0))
        oScoreText = self.scoreFont.render(f"{oScore}", True, (0, 0, 0))
        displayWindow.blit(sScoreText, (900, 373))
        displayWindow.blit(oScoreText, (900, 484))
        
        # Assuming state_text is a list of strings
        line_surfaces = [self.stateFont.render(line, True, (0, 0, 0)) for line in stateText]

        # Background box properties
        box_x, box_y = 767, 582
        box_width, box_height = 267, 121

        # Calculate total height of all lines
        total_height = sum(surf.get_height() for surf in line_surfaces)
        start_y = box_y + (box_height - total_height) // 2

        # Draw each line centered within the box
        for surf in line_surfaces:
            x = box_x + (box_width - surf.get_width()) // 2
            displayWindow.blit(surf, (x, start_y))
            start_y += surf.get_height()
    
    def printBoard(self):
        # Prints the grid to the console for debugging
        print('Current Board:')
        for row in self.gridLogic:
            print(row)
            
    def findClickableCells(self, grid, player):
        # Clickable cells are those that are empty and have at least one opponent token adjacent to it
        clickableCells = []
        
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                # Skip occupied cells
                if grid[gridX][gridY] != '-':
                    continue
                
                validDirections = findValidDirections(gridX, gridY) # Get all directions that are within the grid
                
                for direction in validDirections:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]
                    
                    # Find an opponent token in the direction
                    if checkedCell == '-' or checkedCell == player:
                        continue
                    else:
                        clickableCells.append((gridX, gridY))
                        break
                    
        return clickableCells
    
    def findSwappableTiles(self, x, y, grid, player):
        surroundingCells = findValidDirections(x, y)
        
        if len(surroundingCells) == 0:
            return []
        
        swappableTiles = []
        opposingPlayer = 'S' if player == 'O' else 'O'
        
        for checkedCell in surroundingCells:
            cellX, cellY = checkedCell
            difX, difY = cellX - x, cellY - y
            currentLine = [] # List of all the swappable tiles if current cell is chosen as a move
            checkingLine = True
            
            while checkingLine:
                # If an opponent token is found, continue checking in the same direction until a player token is found or an empty cell is found
                if grid[cellX][cellY] == opposingPlayer:
                    currentLine.append((cellX, cellY))
                elif grid[cellX][cellY] == player:
                    checkingLine = False
                    break
                elif grid[cellX][cellY] == '-':
                    currentLine.clear()
                    checkingLine = False
                    break
                
                # Move to the next cell in the direction
                cellX += difX
                cellY += difY
                
                # Check if the cell is within bounds
                if cellX < 0 or cellX > 7 or cellY < 0 or cellY > 7:
                    currentLine.clear()
                    checkingLine = False
                    break
                
            if len(currentLine) > 0:
                    swappableTiles.extend(currentLine)
                    
        return swappableTiles
                
    def findValidMoves(self, grid, player):
        # Valid move is a cell that is empty and has at least one opponent token adjacent to it, and has at least one swappable tile in the direction of the move
        clickableCells = self.findClickableCells(grid, player)
        validMoves = []
        
        for cell in clickableCells:
            x, y = cell
            
            swappableTiles = self.findSwappableTiles(x, y, grid, player)
            
            if len(swappableTiles) > 0:
                validMoves.append(cell)
                
        return validMoves
    
    def calculateScore(self, grid):
        # Calculate the score of each player
        sScore = 0
        oScore = 0
        
        for row in grid:
            for cell in row:
                if cell == 'S':
                    sScore += 1
                elif cell == 'O':
                    oScore += 1
        
        return sScore, oScore