import pygame
import copy

class FlipSOS:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('FlipSOS')
        
        self.run = True
        
    def run(self):
        # Main game loop
        while self.run == True:
            self.input()
            self.update()
            self.draw()
            
    def input(self):
        # Handle window close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((255, 255, 255)) # White mona
        