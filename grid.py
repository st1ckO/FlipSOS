import pygame
from sos_token import Token

# Utility functions
def load_image(path, size):
    img = pygame.image.load(path).convert_alpha() # To make png transparent
    img = pygame.transform.scale(img, size)
    return img

def extract_sprite(sheet, x, y, scaleSize, size):
    # Extract a sprite from a sprite sheet
    sprite = pygame.Surface((size[0], size[1])).convert_alpha() # size parameter is the size of each sprite in the sheet
    sprite.blit(sheet, (0, 0), (x * size[0], y * size[1], size[0], size[1])) 
    sprite = pygame.transform.scale(sprite, scaleSize)
    return sprite

def find_valid_directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
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

def is_on_grid(x, y, minX=0, minY=0, maxX=7, maxY=7):
    # Check if the coordinates are within the grid bounds
    return minX <= x <= maxX and minY <= y <= maxY

# Handles the grid design and logic       
class Grid:
    def __init__(self, rows, columns, tokenSize, gameClass): 
        self.gameClass = gameClass
        self.y = rows
        self.x = columns
        self.tokenSize = tokenSize
        self.resizedToken = (tokenSize[0] - 2, tokenSize[1] - 2)
        self.validTokenSize = (tokenSize[0] - 5, tokenSize[1] - 5)
        self.tokens = {}
        self.playerO = 'O'
        self.playerS = 'S'
        self.currentPlayer = 'S'
        
        self.sToken = load_image('assets/S.png', self.resizedToken)
        self.oToken = load_image('assets/O.png', self.resizedToken)
        self.validToken = load_image('assets/Valid_Moves.png', self.validTokenSize)
        self.sidebar = load_image('assets/Sidebar.png', (360, 720))
        self.scoreFont = pygame.font.Font('assets/arial.ttf', 50)
        self.stateFont = pygame.font.Font('assets/arial.ttf', 28)
        
        self.bgDict = self.load_background_images()
        self.bg = self.create_background()
        self.gridLogic = self.regen_grid(self.y, self.x)
        
        self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
        self.sScore, self.oScore = self.calculate_score(self.gridLogic)
        self.sPatternScore, self.oPatternScore = 0, 0
        self.validMoves = self.find_valid_moves(self.gridLogic, self.currentPlayer)
        self.lastMove = None
        self.pattern = []
        self.bothSkipped = False
        self.gameOver = 0 # 0 = Continue, 1 = S wins, 2 = O wins, 3 = Draw
        
    def load_background_images(self):
        # Load background images for the grid 
        # Extracts the images from the sprite sheet and scales them to the token size
        imageDict = {}
        xAlpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        spriteSheet = pygame.image.load('assets/Sprite Sheet.png').convert_alpha()
        spriteActualSize = (192, 192)
        
        for y in range(3):
            for x in range(7):
                imageDict[xAlpha[x] + str(y)] = extract_sprite(spriteSheet, x, y, self.tokenSize, spriteActualSize)
        
        return imageDict
    
    def create_background(self):
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
    
    def add_token(self, grid, player, y, x):
        # Adds a token to the grid and updates the grid logic
        tokenImage = self.oToken if player == 'O' else self.sToken
        self.tokens[(y, x)] = Token(player, y, x, self.tokenSize, tokenImage, self.gameClass)
        grid[y][x] = self.tokens[(y, x)].player
        
    def regen_grid(self, rows, columns):
        # Generates empty grid for game logic
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append('-')
            grid.append(line)
            
        # Add starting tokens
        self.add_token(grid, 'O', 3, 3)
        self.add_token(grid, 'S', 3, 4)
        self.add_token(grid, 'O', 4, 4)
        self.add_token(grid, 'S', 4, 3)

        return grid
    
    def draw_grid(self, displayWindow):
        displayWindow.blit(self.bg, (0, 0))
        
        for token in self.tokens.values():
            token.draw(displayWindow)

        for move in self.validMoves:
            displayWindow.blit(self.validToken, (move[1] * self.tokenSize[0] + self.tokenSize[0] + 2, move[0] * self.tokenSize[1] + self.tokenSize[1] + 2))
        
        # Draw red circle on last clicked cell
        if self.lastMove:
            y, x = self.lastMove
            centerX = x * self.tokenSize[0] + (self.tokenSize[0] * 3) // 2
            centerY = y * self.tokenSize[1] + (self.tokenSize[1] * 3) // 2
            pygame.draw.circle(displayWindow, (255, 0, 0), (centerX, centerY), 5)  
        
        # Draw a line on each pattern formed
        for pattern in self.pattern:
            # Convert grid coordinates to pixel coordinates (center of each tile)
            pixel_coords = [
                (px * self.tokenSize[0] + (self.tokenSize[0] * 3) // 2, py * self.tokenSize[1] + (self.tokenSize[1] * 3) // 2)
                for (py, px) in pattern
            ]
            
            # Ensure line is drawn from one end to the other
            pixel_coords.sort()
            
            # Draw line from first to last point in the pattern
            pygame.draw.line(displayWindow, (255, 0, 0), pixel_coords[0], pixel_coords[-1], 1)
            
    def draw_sidebar(self, displayWindow):
        displayWindow.blit(self.sidebar, (720, 0)) # Blit the sidebar to the right
        
        # Draw overlay text
        sScoreText = self.scoreFont.render(f"{self.sScore} + {self.sPatternScore}", True, (0, 0, 0))
        oScoreText = self.scoreFont.render(f"{self.oScore} + {self.oPatternScore}", True, (0, 0, 0))
        displayWindow.blit(sScoreText, (870, 379))
        displayWindow.blit(oScoreText, (870, 490))
        
        # Assuming stateText is a list of strings
        lineSurfaces = [self.stateFont.render(line, True, (0, 0, 0)) for line in self.stateText]

        # Background box properties
        boxX, boxY = 767, 582
        boxWidth, boxHeight = 267, 121

        # Calculate total height of all lines
        totalHeight = sum(surf.get_height() for surf in lineSurfaces)
        startY = boxY + (boxHeight - totalHeight) // 2

        # Draw each line centered within the box
        for surf in lineSurfaces:
            x = boxX + (boxWidth - surf.get_width()) // 2
            displayWindow.blit(surf, (x, startY))
            startY += surf.get_height()
    
    def print_board(self):
        # Prints the grid to the console for debugging
        print('Current Board:')
        for row in self.gridLogic:
            print(row)
            
    def find_clickable_cells(self, grid, player):
        # Clickable cells are those that are empty and have at least one opponent token adjacent to it
        clickableCells = []
        
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                # Skip occupied cells
                if grid[gridX][gridY] != '-':
                    continue
                
                validDirections = find_valid_directions(gridX, gridY) # Get all directions that are within the grid
                
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
    
    def find_swappable_tiles(self, x, y, grid, player):
        surroundingCells = find_valid_directions(x, y)
        
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
                    
        if len(swappableTiles) > 0:
            swappableTiles.append((x, y))
            
        return swappableTiles
                
    def find_valid_moves(self, grid, player):
        # Valid move is a cell that is empty and has at least one opponent token adjacent to it, and has at least one swappable tile in the direction of the move
        clickableCells = self.find_clickable_cells(grid, player)
        validMoves = []
        
        for cell in clickableCells:
            x, y = cell
            
            swappableTiles = self.find_swappable_tiles(x, y, grid, player)
            
            if len(swappableTiles) > 0:
                validMoves.append(cell)
                
        return validMoves
    
    def flip_tiles(self, x, y):
        # Flip all the tokens in the direction of the move
        swappableTiles = self.find_swappable_tiles(x, y, self.gridLogic, self.currentPlayer)
        
        for tile in swappableTiles:
            self.add_token(self.gridLogic, self.currentPlayer, tile[0], tile[1])
            
        self.update_score(swappableTiles)
    
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
            
        return sScore, oScore
    
    def update_score(self, swappableTiles):
        self.sScore, self.oScore = self.calculate_score(self.gridLogic)
        currentPattern = self.find_patterns(self.gridLogic, swappableTiles)
        self.pattern = currentPattern
        patternScore = len(currentPattern)
        print(currentPattern)
        
        if self.currentPlayer == 'S':
            self.sPatternScore += patternScore
        else:
            self.oPatternScore += patternScore
    
    def find_patterns(self, grid, swappableTiles):
        directions = [
            (0, 1),   # horizontal right
            (1, 0),   # vertical down
            (1, 1),   # diagonal down-right
            (1, -1),  # diagonal down-left
        ]
        patterns = []
        seenPatterns = set()
        
        for cx, cy in swappableTiles:
            for dx, dy in directions:
                # Check 3-cell patterns in each direction of the current cell
                for offset in [-2, -1, 0]:
                    coordinates = [
                        (cx + dx * offset, cy + dy * offset),
                        (cx + dx * (offset + 1), cy + dy * (offset + 1)),
                        (cx + dx * (offset + 2), cy + dy * (offset + 2))
                    ]
                    
                    # Validate bounds
                    if not all(is_on_grid(cdx, cdy) for cdx, cdy in coordinates):
                        continue
                    
                    # Get pattern string (SOS or OSO)
                    pattern = [grid[cdx][cdy] for cdx, cdy in coordinates]
                    if pattern == ['S', 'O', 'S'] or pattern == ['O', 'S', 'O']:
                        key = frozenset(coordinates)  # Used frozenset to avoid duplicates
                        if key not in seenPatterns:
                            seenPatterns.add(key)
                            patterns.append(coordinates)             
        
        return patterns  
    
    def switch_player(self):
        self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS
        self.validMoves = self.find_valid_moves(self.gridLogic, self.currentPlayer)
        
        # Handle Skips
        if self.validMoves == []:
            self.stateText = [f"NO VALID MOVE", "TURN SKIPPED"]
            self.currentPlayer = self.playerO if self.currentPlayer == self.playerS else self.playerS
            self.validMoves = self.find_valid_moves(self.gridLogic, self.currentPlayer)
            
            # Both players skipped
            if self.validMoves == []:
                self.stateText = ["BOTH SKIPPED", "GAME OVER"]    
                self.bothSkipped = True 
            else:
                self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
        else:
            self.stateText = [f"PLAYER {self.currentPlayer}", "TURN"]
        
    def check_game_over(self):
        if self.bothSkipped or self.sScore + self.oScore == self.x * self.y:
            self.gameOver = self.check_winner(self.sScore, self.sPatternScore, self.oScore, self.oPatternScore)
            self.display_game_over()

    def check_winner(self, sScore, sPatternScore, oScore, oPatternScore):
        if (sScore + sPatternScore) > (oScore + oPatternScore):
            return 1
        elif (oScore + oPatternScore) > (sScore + sPatternScore):       
            return 2
        elif (sScore + sPatternScore) == (oScore + oPatternScore):         
            return 3
    
    def display_game_over(self):
        if self.gameOver == 1:
            self.stateText = ["PLAYER S WINS", "GAME OVER"]
        elif self.gameOver == 2:
            self.stateText = ["PLAYER O WINS", "GAME OVER"]
        else:
            self.stateText = ["DRAW", "GAME OVER"]