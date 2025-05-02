from grid import find_valid_moves

# Utility Functions
def apply_move(grid, x, y, player):
    grid[x][y] = player
    
def get_reward(grid, player):
    pass
    
class ComputerPlayer:
    def __init__(self, player, grid, maxDepth):
        self.player = player
        self.maxDepth = maxDepth
        
    def get_best_move(self, grid):
        bestScore = float('-inf')
        bestMove = None
        validMoves = find_valid_moves(grid, self.player)
        
        if not validMoves:
            return None
        
        for move in validMoves:
            newGrid= apply_move(grid, move[0], move[1], self.player)
            score = self.min_score(newGrid, 1)
            if score > bestScore:
                bestScore = score
                bestMove = move
                
        return bestMove
    
    def max_score(self, grid, depth):
        pass
    
    def min_score(self, grid, depth):
        pass
        