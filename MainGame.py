import pygame
from Cell import Cell
from Buttons import StartButton, ClearButton, ComboBox
from CONFIG import *

class MainGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIN_DIMS[0],WIN_DIMS[1]+MENU_SIZE))
        self.bgColor = (255,255,255)
        self.background_image = pygame.image.load("artistic_battlefield_map.png")
        self.quit_game = False
        
        self.board = [[Cell() for _ in range(WIN_DIMS[1]//CELL_SIZE)] for _ in range(WIN_DIMS[0]//CELL_SIZE)]
        
        self.start_button = StartButton(self,'Start', 10, 730, True)
        self.start_iteration = False
        self.clear_button = ClearButton(self,'Clear', 170, 730, True)
        self.combo_box = ComboBox(self,330,730,25,150,[0,1,2,3],0)
    
        self.dragging = False
    
    def play(self):
        while not self.quit_game:
            self.update()
            self.render()
            
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.dragging:
                        self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.handle_click(event.pos)

    def handle_click(self, position):
        if position[0]<WIN_DIMS[0] and position[1]<WIN_DIMS[1] and not self.combo_box.active:
            col = position[0]//CELL_SIZE
            row = position[1]//CELL_SIZE
            self.board[col][row].clicked = True
            
        if self.start_button.rect.collidepoint(position):
            if self.start_button.text == 'Start':
                self.start_iteration = True
            else:
                self.start_iteration = False
            self.start_button.get_clicked()
            
        if self.clear_button.rect.collidepoint(position):
            for row in self.board:
                for x in row:
                    x.clicked = False
        
        if self.combo_box.rect.collidepoint(position):
            self.combo_box.handle_event(position,True)
        else:
            self.combo_box.handle_event(position,False)
    
    
    def render(self):
        self.window.fill(self.bgColor)
        self.window.blit(self.background_image,(0,0))
        for i,row in enumerate(self.board):
            for j,col in enumerate(row):
                if col.clicked == True:
                    pygame.draw.rect(self.window,(255,0,0),(i*CELL_SIZE,j*CELL_SIZE,10,10))
        self.start_button.draw()
        self.clear_button.draw()
        self.combo_box.draw()
        pygame.display.update()
        

x = MainGame()