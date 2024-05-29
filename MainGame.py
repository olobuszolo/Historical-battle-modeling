import pygame
from Cell import *
from Buttons import StartButton, ClearButton, ComboBox, Slider
from CONFIG import *
import time
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
        
        self.field = [[0 for _ in range(WIN_DIMS[1]//CELL_SIZE)] for _ in range(WIN_DIMS[0]//CELL_SIZE)]
        self.board = [[Cell((i,j)) for i in range(WIN_DIMS[1]//CELL_SIZE)] for j in range(WIN_DIMS[0]//CELL_SIZE)]
        self.add_neighbour()
        self.add_neighbour_fight()
        self.iteration_num = 0
        self.team_A = []
        self.team_B = []
        
        self.start_button = StartButton(self,'Start', 10, 735, True)
        self.start_iteration = False
        self.clear_button = ClearButton(self,'Clear', 170, 735, True)
        self.combo_box = ComboBox(self,330,735,[0,1,2,3],0)
        self.slider = Slider(self,490,735,150,25,0,100)
    
        self.dragging = False
    
    #MOORE
    def add_neighbour_fight(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                fight_neighbours = []
                for x in range(i-1,i+2):
                    for y in range(j-1,j+2):
                        if i==x and y == j: 
                            continue
                        if x>=0 and x<len(self.board) and y >=0 and y<len(self.board[x]):
                            fight_neighbours.append(self.board[x][y])
                self.board[i][j].fight_neighbours = fight_neighbours
                
    def add_neighbour(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                neighbour = []
                if i > 0:
                    neighbour.append(self.board[i - 1][j])  # North
                if i < len(self.board) - 1:
                    neighbour.append(self.board[i + 1][j])  # South
                if j > 0:
                    neighbour.append(self.board[i][j - 1])  # West
                if j < len(self.board[i]) - 1:
                    neighbour.append(self.board[i][j + 1])  # East
                self.board[i][j].neighbours = neighbour
    
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
            for neighbour in warrior.cell.neighbours:
                if neighbour not in toCheck:
                    toCheck.append(neighbour)
        
        while toCheck:
            currPoint = toCheck[0]
            if currPoint.calc_static_field():
                for neighbour in currPoint.neighbours:
                    if neighbour not in toCheck:
                        toCheck.append(neighbour)
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
        print(len(self.team_A))
        print(len(self.team_B))

        
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
        if position[0]<WIN_DIMS[0] and position[1]<WIN_DIMS[1] and not self.combo_box.active:
            col = position[0]//CELL_SIZE
            row = position[1]//CELL_SIZE
            if self.board[col][row].typ == None:
                match self.combo_box.selected_index:
                    case 0:
                        self.board[col][row].typ = Warrior(self.board[col][row], TEAM_A)
                        self.team_A.append(self.board[col][row].typ)
                    case 1:
                        self.board[col][row].typ = Warrior(self.board[col][row], TEAM_B)
                        self.team_B.append(self.board[col][row].typ)

                    case 2:
                        pass
                    case 3:
                        pass
            
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
                    x.typ = None
                    x.next_type = None
                    x.blocked = False
        
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
                    if isinstance(cell.typ, Warrior):
                        if cell.typ.team == TEAM_A:
                            pygame.draw.rect(self.window, (255, 255, 0), (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        else:
                            pygame.draw.rect(self.window, (255, 0, 0), (i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        self.start_button.draw()
        self.clear_button.draw()
        self.combo_box.draw()
        self.slider.draw()
        pygame.display.set_caption(f"Historical battle modeling ({self.iteration_num} iterations)")
        pygame.display.update()
