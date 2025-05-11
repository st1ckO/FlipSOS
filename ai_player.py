from grid import *
from copy import deepcopy

# Utility Functions
def copy_grid(grid):
    return [row[:] for row in grid]

def apply_move(x, y, grid, player):
    newGrid = copy_grid(grid)
    swappableTiles = find_swappable_tiles(x, y, newGrid, player)
    
    # Apply the move to the grid and flip the swappable tiles
    for tile in swappableTiles:
        newGrid[tile[0]][tile[1]] = player
    
    return newGrid, swappableTiles

def is_terminal(grid):
    sSCore, oScore = calculate_score(grid)
    return sSCore + oScore == 64
    
def get_reward(grid, player, sPatternScore, oPatternScore):
    sScore, oScore = calculate_score(grid)
    
    if player == 'O':
        playerScore = oPatternScore + oScore
        opponentScore = sPatternScore + sScore
    else:
        playerScore = sPatternScore + sScore
        opponentScore = oPatternScore + oScore
    
    if playerScore > opponentScore:
        return 100000
    elif playerScore < opponentScore:
        return -100000
    else:
        return 0

# For debugging purposes, print the grid in a readable format
def print_grid(grid):
    for row in grid:
        print(' '.join(row))
    print()
    
class ComputerPlayer:
    def __init__(self, player, maxDepth, gridClass):
        self.player = player
        self.opponent = 'S' if player == 'O' else 'O'
        self.maxDepth = maxDepth
        self.gridClass = gridClass
        
    def get_best_move(self):
        bestScore = float('-inf')
        bestMove = None
        validMoves = find_valid_moves(self.gridClass.gridLogic, self.player)
        testGrid = copy_grid(self.gridClass.gridLogic)
        
        if not validMoves:
            return None
        
        # Iterate through all valid moves of the AI and evaluate them
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], testGrid, self.player)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sScore, oScore = 0, 0
            
            if self.player == 'O':
                oScore += patternScore
            else:
                sScore += patternScore
            
            score = self.min_score(newGrid, 1, sScore, oScore) # Check the minimum score of the AI given the opponent's best move
            
            # Update the best score and move if the current score is better
            if score > bestScore:
                bestScore = score
                bestMove = move
        
        print(f"Best Move: {bestMove}, Score: {bestScore}") # For debugging
        return bestMove
    
    def min_score(self, grid, depth, sScore, oScore):
        # Check if the game is over or if the maximum depth has been reached
        if is_terminal(grid):
            return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore)
        
        if depth >= self.maxDepth:
            return self.heuristic_evaluation(grid, self.player, sScore, oScore)
        
        validMoves = find_valid_moves(grid, self.opponent)
        
        if not validMoves: # Opponent's turn is skipped
            if not find_valid_moves(grid, self.player): # Both turns are skipped, game over
                return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore) # Identify the winner
            else: 
                return self.max_score(grid, depth + 1, sScore, oScore) # AI's turn
            
        minScore = float('inf')
        
        # Iterate through all valid moves of the opponent and evaluate them
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.opponent)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sNewScore, oNewScore = sScore, oScore
            
            if self.opponent == 'S':
                sNewScore += patternScore
            else:
                oNewScore += patternScore
            
            score = self.max_score(newGrid, depth + 1, sNewScore, oNewScore) # Check the maximum score of the AI given the opponent's best move
            minScore = min(minScore, score) # Update the minimum score if the current score is lower
            
        return minScore
            
    def max_score(self, grid, depth, sScore, oScore):
        # Check if the game is over or if the maximum depth has been reached
        if is_terminal(grid):
            return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore)
        
        if depth >= self.maxDepth:
            return self.heuristic_evaluation(grid, self.player, sScore, oScore)
        
        validMoves = find_valid_moves(grid, self.player)
        
        if not validMoves: # AI's turn is skipped
            if not find_valid_moves(grid, self.opponent): # Both turns are skipped, game over
                return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore) # Identify the winner
            else: 
                return self.min_score(grid, depth + 1, sScore, oScore)
            
        maxScore = float('-inf')
        
        # Iterate through all valid moves of the AI and evaluate them
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.player)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sNewScore, oNewScore = sScore, oScore
            
            if self.player == 'O':
                oNewScore += patternScore
            else:
                sNewScore += patternScore
            
            score = self.min_score(newGrid, depth + 1, sNewScore, oNewScore) # Check the minimum score of the AI given the opponent's best move
            maxScore = max(maxScore, score) # Update the maximum score if the current score is higher
            
        return maxScore
            
    def heuristic_evaluation(self, grid, player, sScore, oScore):
        opponent = 'S' if player == 'O' else 'O'
        
        # Static Positional Weights
        valueTable = [
            [100, -10,  11,   6,   6,  11, -10, 100],
            [-10, -20,   1,   2,   2,   1, -20, -10],
            [ 10,   1,   5,   4,   4,   5,   1,  10],
            [  6,   2,   4,   2,   2,   4,   2,   6],
            [  6,   2,   4,   2,   2,   4,   2,   6],
            [ 10,   1,   5,   4,   4,   5,   1,  10],
            [-10, -20,   1,   2,   2,   1, -20, -10],
            [100, -10,  11,   6,   6,  11, -10, 100],
        ]
        
        # Directions (W, NW, N, NE, E, SE, S, SW)
        rx = [-1, -1,  0,  1,  1,  1,  0, -1]
        ry = [ 0,  1,  1,  1,  0, -1, -1, -1]

        staticValue = 0 
        ownTokens = oppTokens = 0 # Number of tokens on the board
        ownFront = oppFront = 0 # Frontier Tokens (tokens adjacent to empty spaces). They are vulnerable to being flipped.
        
        # Static Board Evaluation (-456 to +456)
        for row in range(8):
            for col in range(8):
                cell = grid[row][col]
                
                if cell == player:
                    staticValue += valueTable[row][col]
                    ownTokens += 1
                elif cell == opponent:
                    staticValue -= valueTable[row][col]
                    oppTokens += 1

        # Calculate the number of frontier tokens for stability evaluation
                # If cell is not empty, check the adjacent cells
                if cell != '-': 
                    ownFlag = oppFlag = True # Flags to ensure we only count a token once as a frontier token
                    
                    # Loop through all 8 directions
                    for k in range(8):
                        x, y = row + rx[k], col + ry[k]
                        if 0 <= x < 8 and 0 <= y < 8 and grid[x][y] == '-':
                            if ownFlag and cell == player:
                                ownFront += 1
                                ownFlag = False
                            if oppFlag and cell == opponent:
                                oppFront += 1
                                oppFlag = False

        # Token Difference Evaluation (-100 to +100)
        tokenDiff = 0 if ownTokens + oppTokens == 0 else 100 * (ownTokens - oppTokens) / (ownTokens + oppTokens)
        
        # Frontier Tokens Evaluation (-100 to +100)
        frontier = 0 if ownFront + oppFront == 0 else 100 * (oppFront - ownFront) / (ownFront + oppFront)
        
        # Mobility Evaluation (-100 to +100)
        ownValidMoves = len(find_valid_moves(grid, player))
        oppValidMoves = len(find_valid_moves(grid, opponent))
        mobility = 0 if ownValidMoves + oppValidMoves == 0 else 100 * (ownValidMoves - oppValidMoves) / (ownValidMoves + oppValidMoves)

        # Corners Captured Evaluation (-100 to +100)
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        ownCorner = oppCorner = 0
        for x, y in corners:
            if grid[x][y] == player:
                ownCorner += 1
            elif grid[x][y] == opponent:
                oppCorner += 1
        cornerScore = 25 * (ownCorner - oppCorner)
        
        # Corner Closeness Evaluation (-150 to +150): The squares adjacent to the empty corner squares are rated negatively.
        adjacentCorners = [
            [(0, 1), (1, 0), (1, 1)], # Adjacent to top-left corner
            [(0, 6), (1, 6), (1, 7)], # Adjacent to top-right corner
            [(6, 0), (6, 1), (7, 1)], # Adjacent to bottom-left corner
            [(6, 6), (6, 7), (7, 6)], # Adjacent to bottom-right corner
        ]
        ownAdj = oppAdj = 0
        
        # Check each adjacent square for each corner
        for cornerNum, (i, j) in enumerate(corners):
            if grid[i][j] == '-':  # If the corner is empty
                for x, y in adjacentCorners[cornerNum]:
                    if 0 <= x < 8 and 0 <= y < 8:
                        if grid[x][y] == player:
                            ownAdj += 1
                        elif grid[x][y] == opponent:
                            oppAdj += 1
                            
        cornerAdj = 12.5 * (oppAdj - ownAdj) 
        
        # Pattern Evaluation (-100 to +100)
        ownPatternScore = oScore if player == 'O' else sScore
        oppPatternScore = sScore if player == 'O' else oScore
        patternScoreDiff = 0 if ownPatternScore + oppPatternScore == 0 else 100 * (ownPatternScore - oppPatternScore) / (ownPatternScore + oppPatternScore)
        
        # Score Range: -52300 to +52300
        # staticValue: -456 to +456 => -22800 to +22800
        # tokenDiff: -100 to +100 => -1500 to +1500
        # frontier: -100 to +100 => -3000 to +3000
        # mobility: -100 to +100 => -6000 to +6000
        # cornerScore: -100 to +100 => -4000 to +4000
        # cornerAdj: -150 to +150 => -4500 to +4500
        # patternScoreDiff: -100 to +100 => -6000 to +6000
        score = (50 * staticValue) + (15 * tokenDiff) + (30 * frontier) + (60 * mobility) + (40 * cornerScore) + (30 * cornerAdj) + (60 * patternScoreDiff)
        
        return score
    





######################################################_ALPHA-BETA PRUNING_#######################################################
    # Alpha-Beta Pruning Version (if allowed)
    def get_best_move_ab(self):
        bestScore = float('-inf')
        bestMove = None
        alpha = float('-inf')
        beta = float('inf')

        validMoves = find_valid_moves(self.gridClass.gridLogic, self.player)
        testGrid = copy_grid(self.gridClass.gridLogic)

        if not validMoves:
            return None

        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], testGrid, self.player)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sScore, oScore = 0, 0

            if self.player == 'O':
                oScore += patternScore
            else:
                sScore += patternScore

            score = self.min_score_ab(newGrid, 1, sScore, oScore, alpha, beta)
            if score > bestScore:
                bestScore = score
                bestMove = move

            alpha = max(alpha, bestScore)

        print(f"Best Move: {bestMove}, Score: {bestScore}")
        return bestMove


    def min_score_ab(self, grid, depth, sScore, oScore, alpha, beta):
        if is_terminal(grid):
            return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore)

        if depth >= self.maxDepth:
            return self.heuristic_evaluation(grid, self.player, sScore, oScore)

        validMoves = find_valid_moves(grid, self.opponent)

        if not validMoves:
            if not find_valid_moves(grid, self.player):
                return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore)
            else:
                return self.max_score_ab(grid, depth + 1, sScore, oScore, alpha, beta)

        minScore = float('inf')
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.opponent)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sNewScore, oNewScore = sScore, oScore

            if self.opponent == 'S':
                sNewScore += patternScore
            else:
                oNewScore += patternScore

            score = self.max_score_ab(newGrid, depth + 1, sNewScore, oNewScore, alpha, beta)
            minScore = min(minScore, score)

            if minScore <= alpha:
                break  # Max won't allow this move
            beta = min(beta, minScore)

        return minScore


    def max_score_ab(self, grid, depth, sScore, oScore, alpha, beta):
        if is_terminal(grid):
            return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore)

        if depth >= self.maxDepth:
            return self.heuristic_evaluation(grid, self.player, sScore, oScore)

        validMoves = find_valid_moves(grid, self.player)

        if not validMoves:
            if not find_valid_moves(grid, self.opponent):
                return get_reward(grid, self.player, sScore + self.gridClass.sPatternScore, oScore + self.gridClass.oPatternScore)
            else:
                return self.min_score_ab(grid, depth + 1, sScore, oScore, alpha, beta)

        maxScore = float('-inf')
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.player)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sNewScore, oNewScore = sScore, oScore

            if self.player == 'O':
                oNewScore += patternScore
            else:
                sNewScore += patternScore

            score = self.min_score_ab(newGrid, depth + 1, sNewScore, oNewScore, alpha, beta)
            maxScore = max(maxScore, score)

            if maxScore >= beta:
                break  # Min won't allow this move
            alpha = max(alpha, maxScore)

        return maxScore
