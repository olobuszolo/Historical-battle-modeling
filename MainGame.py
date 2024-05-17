import pygame
from Cell import Cell
from Buttons import StartButton, ClearButton, ComboBox, Slider
from CONFIG import *

class MainGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIN_DIMS[0],WIN_DIMS[1]+MENU_SIZE))
        self.bgColor = (255,255,255)
        self.background_image = pygame.image.load("resources\\artistic_battlefield_map.png")
        self.bar_image = pygame.image.load("resources\\bar.jpg")
        pygame_icon = pygame.image.load('resources\\icon.png')
        pygame.display.set_icon(pygame_icon)
        self.quit_game = False
        
        self.board = [[Cell() for _ in range(WIN_DIMS[1]//CELL_SIZE)] for _ in range(WIN_DIMS[0]//CELL_SIZE)]
        self.iteration_num = 0
        
        self.start_button = StartButton(self,'Start', 10, 735, True)
        self.start_iteration = False
        self.clear_button = ClearButton(self,'Clear', 170, 735, True)
        self.combo_box = ComboBox(self,330,735,[0,1,2,3],0)
        self.slider = Slider(self,490,735,150,25,0,100)
    
        self.dragging = False
    
    def play(self):
        iteration_curr_speed = 0
        while not self.quit_game:
            if self.start_iteration:
                iteration_speed = self.slider.get_value()
                if iteration_curr_speed < iteration_speed:
                    iteration_curr_speed += 1
                else:
                    iteration_curr_speed = 0
                    self.iteration()
                    self.iteration_num += 1
            self.update()
            self.render()
    
    def iteration(self):
        pass
            
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game = True
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if event.pos[0]<WIN_DIMS[0] and event.pos[1]<WIN_DIMS[1]:
                        self.dragging = True
                    self.handle_click(event.pos)
                    self.slider.handle_event(event)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.dragging:
                        self.dragging = False
                    self.slider.handle_event(event)
                        
            elif event.type == pygame.MOUSEMOTION:
                    if self.dragging and event.pos[0]<WIN_DIMS[0] and event.pos[1]<WIN_DIMS[1]:
                        self.handle_click(event.pos)
                    self.slider.handle_event(event)

    def handle_click(self, position):
        if position[0]<WIN_DIMS[0] and position[1]<WIN_DIMS[1] and not self.combo_box.active:
            col = position[0]//CELL_SIZE
            row = position[1]//CELL_SIZE
            self.board[col][row].clicked = True
            self.board[col][row].typ = self.combo_box.selected_index
            
        if self.start_button.rect.collidepoint(position):
            if self.start_button.text == 'Start':
                self.start_iteration = True
            else:
                self.start_iteration = False
            self.start_button.get_clicked()
            
        if self.clear_button.rect.collidepoint(position):
            self.iteration_num = 0
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
        self.window.blit(self.bar_image,(0,720))
        for i,row in enumerate(self.board):
            for j,col in enumerate(row):
                if col.clicked == True:
                    if self.board[i][j].typ == 0:
                        pygame.draw.rect(self.window,(255,255,0),(i*CELL_SIZE,j*CELL_SIZE,10,10))
                    elif self.board[i][j].typ == 1:
                        pygame.draw.rect(self.window,(255,0,0),(i*CELL_SIZE,j*CELL_SIZE,10,10))
                    elif self.board[i][j].typ == 2:
                        pygame.draw.rect(self.window,(0,0,255),(i*CELL_SIZE,j*CELL_SIZE,10,10))
                    elif self.board[i][j].typ == 3:
                        pygame.draw.rect(self.window,(0,0,0),(i*CELL_SIZE,j*CELL_SIZE,10,10))  
                    
        self.start_button.draw()
        self.clear_button.draw()
        self.combo_box.draw()
        self.slider.draw()
        pygame.display.set_caption(f"Historical battel modeling ({self.iteration_num} iterations)")
        pygame.display.update()
        

x = MainGame()