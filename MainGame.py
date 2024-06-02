import pygame
from Cell import *
from Buttons import StartButton, ClearButton, ComboBox, Slider
from CONFIG import *
import time
from pathlib import PurePath

class MainGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIN_DIMS[0],WIN_DIMS[1]+MENU_SIZE))
        self.bgColor = (255,255,255)
        self.background_image = pygame.image.load(PurePath('./resources/artistic_battlefield_map.png'))
        self.bar_image = pygame.image.load(PurePath('./resources/bar.jpg'))
        pygame_icon = pygame.image.load(PurePath('./resources/icon.png'))
        pygame.display.set_icon(pygame_icon)
        self.quit_game = False
        
        self.field = [[0 for _ in range(WIN_DIMS[1]//CELL_SIZE)] for _ in range(WIN_DIMS[0]//CELL_SIZE)]
        self.board = [[Cell((i,j )) for i in range(WIN_DIMS[1]//CELL_SIZE)] for j in range(WIN_DIMS[0]//CELL_SIZE)]
        self.add_neighbor()
        self.add_neighbor_fight()
        self.iteration_num = 0

        # teams
        self.teams = {
            TEAM_A: [],
            TEAM_B: []
        }
        
        self.start_button = StartButton(self,'Start', 10, 735, True)
        self.start_iteration = False
        self.clear_button = ClearButton(self,'Clear', 170, 735, True)
        self.combo_box = ComboBox(self,330,735,[0,1,2,3],0)
        self.slider = Slider(self,490,735,150,25,0,100)
    
        self.dragging = False

        self.warior_A_image = pygame.transform.scale(pygame.image.load("resources\\polish_warior.jpg"), (CELL_SIZE, CELL_SIZE))
        self.warior_B_image = pygame.transform.scale(pygame.image.load("resources\\germa_warrior.png"), (CELL_SIZE, CELL_SIZE))
        self.artillery_A_image = pygame.transform.scale(pygame.image.load("resources\\polish_artillery.png"), (CELL_SIZE, CELL_SIZE))
        self.artillery_B_image = pygame.transform.scale(pygame.image.load("resources\\german_artillery.png"), (CELL_SIZE, CELL_SIZE))


    #MOORE
    def add_neighbor_fight(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                fight_neighbors = []
                for x in range(i-1,i+2):
                    for y in range(j-1,j+2):
                        if i==x and y == j: 
                            continue
                        if x>=0 and x<len(self.board) and y >=0 and y<len(self.board[x]):
                            fight_neighbors.append(self.board[x][y])
                self.board[i][j].fight_neighbors = fight_neighbors
                
    def add_neighbor(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                neighbor = []
                if i > 0:
                    neighbor.append(self.board[i - 1][j])  # North
                if i < len(self.board) - 1:
                    neighbor.append(self.board[i + 1][j])  # South
                if j > 0:
                    neighbor.append(self.board[i][j - 1])  # West
                if j < len(self.board[i]) - 1:
                    neighbor.append(self.board[i][j + 1])  # East
                self.board[i][j].neighbors = neighbor
    
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


    def calculate_field_warrior(self, team):
        toCheck = []
        for warrior in team:
            warrior.cell.staticField = 0
            for neighbor in warrior.cell.neighbors:
                if neighbor not in toCheck:
                    toCheck.append(neighbor)
        
        while toCheck:
            currPoint = toCheck[0]
            if currPoint.calc_static_field():
                for neighbor in currPoint.neighbors:
                    if neighbor not in toCheck:
                        toCheck.append(neighbor)
            toCheck.pop(0)
    
    def field_clean(self):
        for row in self.board:
            for cell in row:
                cell.staticField = SFMAX
    
    def iteration(self):
        self.field_clean()
        for i in self.board:
            for j in i:
                j.blocked = False

        self.iteration_A()
        self.field_clean()
        self.iteration_B()
        self.field_clean()

        self.team_A = [warrior for warrior in self.team_A if warrior.health > 0]
        self.team_B = [warrior for warrior in self.team_B if warrior.health > 0]
        
        for row in self.board:
            for cell in row:
                if cell.typ is not None and cell.typ.health <= 0:
                    cell.typ = None

        
    def iteration_A(self):
        self.calculate_field_warrior(self.team_B)
        for elems in self.team_A:
            elems.update()

    def iteration_B(self):
        self.calculate_field_warrior(self.team_A)
        for elems in self.team_B:
            elems.update()

            
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

        ### add agent ###

        if position[0]<WIN_DIMS[0] and position[1]<WIN_DIMS[1] and not self.combo_box.active:
            col = position[0]//CELL_SIZE
            row = position[1]//CELL_SIZE

            if self.board[col][row].typ == None:
                match self.combo_box.selected_index:

                    # warrior
                    case 0:
                        self.board[col][row].typ = Warrior(self.board[col][row], TEAM_A)
                        self.teams[TEAM_A].append(self.board[col][row].typ)
                    case 1:
                        self.board[col][row].typ = Warrior(self.board[col][row], TEAM_B)
                        self.teams[TEAM_B].append(self.board[col][row].typ)

                    # hussar
                    case 2:
                        self.board[col][row].typ = Hussar(self.board[col][row], TEAM_A, self.teams)
                        self.teams[TEAM_A].append(self.board[col][row].typ)
                    case 3:
                        self.board[col][row].typ = Hussar(self.board[col][row], TEAM_B, self.teams)
                        self.teams[TEAM_B].append(self.board[col][row].typ)
                    # artillery
                    case 4:
                        self.board[col][row].typ = Artillery(self.board[col][row], TEAM_A, self.board, self)
                        self.teams[TEAM_A].append(self.board[col][row].typ)
                    case 5:
                        self.board[col][row].typ = Artillery(self.board[col][row], TEAM_B, self.board, self)
                        self.teams[TEAM_B].append(self.board[col][row].typ)
                    
        
        ### start ###

        if self.start_button.rect.collidepoint(position):
            if self.start_button.text == 'Start':
                self.start_iteration = True
            else:
                self.start_iteration = False
            self.start_button.get_clicked()
        
        ### clear ###

        if self.clear_button.rect.collidepoint(position):
            self.iteration_num = 0
            for row in self.board:
                for x in row:
                    x.typ = None
                    x.next_type = None
                    x.blocked = False
            self.teams[TEAM_A] = []
            self.teams[TEAM_B] = []
        
        if self.combo_box.rect.collidepoint(position):
            self.combo_box.handle_event(position,True)
        else:
            self.combo_box.handle_event(position,False)
    

    def render(self):
        self.window.fill(self.bgColor)
        self.window.blit(self.background_image, (0, 0))
        self.window.blit(self.bar_image, (0, 720))

        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell.typ is not None:
                    rect_position = (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                    if isinstance(cell.typ, Warrior):
                        if cell.typ.team == TEAM_A:
                            self.window.blit(self.warior_A_image, (i * CELL_SIZE, j * CELL_SIZE))
                        else:
                            self.window.blit(self.warior_B_image, (i * CELL_SIZE, j * CELL_SIZE))
                    if isinstance(cell.typ, Artillery):
                        if cell.typ.team == TEAM_A: 
                            self.window.blit(self.artillery_A_image, (i * CELL_SIZE, j * CELL_SIZE))
                        else:
                            self.window.blit(self.artillery_B_image, (i * CELL_SIZE, j * CELL_SIZE))
                    elif isinstance(cell.typ, Hussar):
                        if cell.typ.team == TEAM_A:
                            pygame.draw.rect(self.window, HUSSAR_COLOR_A, rect_position)
                        else:
                            pygame.draw.rect(self.window, HUSSAR_COLOR_B, rect_position)        
                            
                    
                    
        self.start_button.draw()
        self.clear_button.draw()
        self.combo_box.draw()
        self.slider.draw()
        pygame.display.set_caption(f"Historical battle modeling ({self.iteration_num} iterations)")
        pygame.display.update()
