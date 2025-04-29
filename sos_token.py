import pygame

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