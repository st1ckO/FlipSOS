from grid import *
from copy import deepcopy

# Utility Functions
def apply_move(x, y, grid, player):
    newGrid = deepcopy(grid)
    newGrid[x][y] = player
    
    return newGrid, find_swappable_tiles(x, y, grid, player)

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
    
    # TODO: Revise the reward depending on the values returned by the heuristic function
    if playerScore > opponentScore:
        return 50000
    elif playerScore < opponentScore:
        return -50000
    else:
        return 0
    
class ComputerPlayer:
    def __init__(self, player, maxDepth):
        self.player = player
        self.opponent = 'S' if player == 'O' else 'O'
        self.maxDepth = maxDepth
        
    def get_best_move(self, grid, sExistingScore, oExistingScore):
        bestScore = float('-inf')
        bestMove = None
        validMoves = find_valid_moves(grid, self.player)
        
        if not validMoves:
            return None
        
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.player)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sScore, oScore = 0, 0
            
            if self.player == 'O':
                oScore += patternScore
            else:
                sScore += patternScore
            
            score = self.min_score(newGrid, 1, sScore, oScore, sExistingScore, oExistingScore)
            if score > bestScore:
                bestScore = score
                bestMove = move
        
        print(f"Best Move: {bestMove}, Score: {bestScore}")
        return bestMove
    
    def min_score(self, grid, depth, sSCore, oScore, sExistingScore, oExistingScore):
        if is_terminal(grid):
            return get_reward(grid, self.player, sSCore + sExistingScore, oScore + oExistingScore)
        
        if depth >= self.maxDepth:
            return self.heuristic_evaluation(grid, self.opponent, sSCore, oScore)
        
        validMoves = find_valid_moves(grid, self.opponent)
        
        if not validMoves: # Opponent's turn is skipped
            if not find_valid_moves(grid, self.player): # Both turns are skipped, game over
                print("min_score - both turns skipped")
                return get_reward(grid, self.opponent, sSCore + sExistingScore, oScore + oExistingScore)
            else: 
                print("min_score - opponent turn skipped")
                return self.max_score(grid, depth + 1, sSCore, oScore, sExistingScore, oExistingScore)
            
        minScore = float('inf')
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.opponent)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sNewScore, oNewScore = sSCore, oScore
            
            if self.opponent == 'S':
                sNewScore += patternScore
            else:
                oNewScore += patternScore
            
            score = self.max_score(newGrid, depth + 1, sNewScore, oNewScore, sExistingScore, oExistingScore)
            minScore = min(minScore, score)
            
        return minScore
            
    def max_score(self, grid, depth, sScore, oScore, sExistingScore, oExistingScore):
        if is_terminal(grid):
            return get_reward(grid, self.player, sScore + sExistingScore, oScore + oExistingScore)
        
        if depth >= self.maxDepth:
            return self.heuristic_evaluation(grid, self.player, sScore, oScore)
        
        validMoves = find_valid_moves(grid, self.player)
        
        if not validMoves: # AI's turn is skipped
            if not find_valid_moves(grid, self.opponent): # Both turns are skipped, game over
                print("max_score - both turns skipped")
                return get_reward(grid, self.player, sScore + sExistingScore, oScore + oExistingScore)
            else: 
                print("max_score - AI turn skipped")
                return self.min_score(grid, depth + 1, sScore, oScore, sExistingScore, oExistingScore)
            
        maxScore = float('-inf')
        for move in validMoves:
            newGrid, flippedTokens = apply_move(move[0], move[1], grid, self.player)
            patternScore = len(find_patterns(newGrid, flippedTokens))
            sNewScore, oNewScore = sScore, oScore
            
            if self.player == 'O':
                oNewScore += patternScore
            else:
                sNewScore += patternScore
            
            score = self.min_score(newGrid, depth + 1, sNewScore, oNewScore, sExistingScore, oExistingScore)
            maxScore = max(maxScore, score)
            
        return maxScore
            
    def heuristic_evaluation(self, grid, player, sScore, oScore):
        value_table = [
            [100, -10, 11, 6, 6, 11, -10, 100],
            [-10, -20, 1, 2, 2, 1, -20, -10],
            [10, 1, 5, 4, 4, 5, 1, 10],
            [6, 2, 4, 2, 2, 4, 2, 6],
            [6, 2, 4, 2, 2, 4, 2, 6],
            [10, 1, 5, 4, 4, 5, 1, 10],
            [-10, -20, 1, 2, 2, 1, -20, -10],
            [100, -10, 11, 6, 6, 11, -10, 100],
        ]
        
        opponent = 'S' if player == 'O' else 'O'
        rx = [-1, -1, 0, 1, 1, 1, 0, -1]
        ry = [0, 1, 1, 1, 0, -1, -1, -1]

        value = own_stones = opp_stones = 0
        own_front = opp_front = own_free_front = opp_free_front = 0

        for i in range(8):
            for j in range(8):
                cell = grid[i][j]
                if cell == player:
                    value += value_table[i][j]
                    own_stones += 1
                elif cell == opponent:
                    value -= value_table[i][j]
                    opp_stones += 1

                if cell != '.':
                    own_flag = opp_flag = True
                    for k in range(8):
                        x, y = i + rx[k], j + ry[k]
                        if 0 <= x < 8 and 0 <= y < 8 and grid[x][y] == '.':
                            if own_flag and cell == player:
                                own_front += 1
                                own_flag = False
                            if opp_flag and cell == opponent:
                                opp_front += 1
                                opp_flag = False
                            if cell == player:
                                own_free_front += 1
                            elif cell == opponent:
                                opp_free_front += 1

        piece_diff = 0 if own_stones + opp_stones == 0 else 100 * (own_stones - opp_stones) / (own_stones + opp_stones)
        own_moves = len(find_valid_moves(grid, player))
        opp_moves = len(find_valid_moves(grid, opponent))
        mobility = 0 if own_moves + opp_moves == 0 else 100 * (own_moves - opp_moves) / (own_moves + opp_moves)
        frontier = 0 if own_front + opp_front == 0 else 100 * (opp_front - own_front) / (own_front + opp_front)

        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        own_corner = opp_corner = 0
        for i, j in corners:
            if grid[i][j] == player:
                own_corner += 1
            elif grid[i][j] == opponent:
                opp_corner += 1
        corner_score = 25 * (own_corner - opp_corner)

        own_adj = opp_adj = 0
        for idx, (i, j) in enumerate(corners):
            if grid[i][j] == '.':
                for dx in range(2):
                    for dy in range(2):
                        x, y = i + dx, j + dy if idx in [0, 1] else i - dx, j - dy
                        if 0 <= x < 8 and 0 <= y < 8:
                            if grid[x][y] == player:
                                own_adj += 1
                            elif grid[x][y] == opponent:
                                opp_adj += 1
        corner_adj = 12.5 * (own_adj - opp_adj)

        score = 15 * piece_diff + 60 * mobility + 30 * frontier + 40 * corner_score + 30 * corner_adj + 50 * value
        return score