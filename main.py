import pygame
import copy

class FlipSOS:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((645, 609))
        pygame.display.set_caption('FlipSOS')
        
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
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((255, 255, 255)) # White mona

if __name__ == '__main__':
    game = FlipSOS()
    game.run()
    pygame.quit()