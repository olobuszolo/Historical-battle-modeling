import pygame
from Cell import *
from Buttons import *
from CONFIG import *
import time
from pathlib import PurePath
from Stats import Stats

class MainGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIN_DIMS[0]+STATS_SIZE,WIN_DIMS[1]+MENU_SIZE+BARS_SIZE))
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

        # sun/fog
        self.last_fog = 0
        self.last_sun = 0
        self.fog_work = False
        self.sun_work = False
        self.sun_team = None
        
        # teams
        self.teams = {
            TEAM_A: [],
            TEAM_B: []
        }
        self.num_of_A = 0
        self.num_of_B = 0
        
        self.start_button = StartButton(self,'Start', 10, WIN_DIMS[1] + BARS_SIZE + 15, True)
        self.start_iteration = False
        self.clear_button = ClearButton(self,'Clear', 170,  WIN_DIMS[1] + BARS_SIZE + 15, True)
        self.combo_box = ComboBox(self, 330,  WIN_DIMS[1] + BARS_SIZE + 15, [
            (0, "Warrior Team A"),
            (1, "Warrior Team B"),
            (2, "Hussar Team A"),
            (3, "Hussar Team B"),
            (4, "Artillery Team A"),
            (5, "Artillery Team B"),
            (6, "Archer Team A"),
            (7, "Archer Team B"),
        ], 0)

        self.slider = Slider(self,490, WIN_DIMS[1] + BARS_SIZE + 15,150,25,0,100)
        self.fog_button = FogButton(self, 'Fog ON', 650,  WIN_DIMS[1] + BARS_SIZE + 15, True)
        
        self.stats = Stats(self)
    
        self.dragging = False

        self.warrior_A_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_warrior.jpg")), (CELL_SIZE, CELL_SIZE))
        self.warrior_B_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/germa_warrior.png")), (CELL_SIZE, CELL_SIZE))
        self.artillery_A_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_artillery.png")), (CELL_SIZE, CELL_SIZE))
        self.artillery_B_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/german_artillery.png")), (CELL_SIZE, CELL_SIZE))
        self.archer_A_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_archer.jpg")), (CELL_SIZE, CELL_SIZE))
        self.archer_B_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/german_archer.jpg")), (CELL_SIZE, CELL_SIZE))
        self.explosion_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/explosion.png")), (CELL_SIZE, CELL_SIZE))
        self.arrow_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/arrow.jpg")), (CELL_SIZE-4, CELL_SIZE-4))


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
                    iteration_curr_speed += 0.5
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

    def clean_is_shooted(self):
        for row in self.board:
            for cell in row:
                cell.is_shooted = False
    
    # def fog(self):
    #     if random_int(1, 10) <= 3:
    #         self.fog_work = True
    #         self.last_fog = self.iteration_num

    def sun(self):
        if random_int(1, 10) <= 3:
            self.sun_work = True
            self.last_sun = self.iteration_num
            self.sun_team = random.choice([TEAM_A, TEAM_B])
            # print(self.sun_team)
    
    def iteration(self):
        self.clean_is_shooted()
        self.field_clean()

        if self.last_sun == self.iteration_num - 3 or self.fog_work:
            self.sun_work = False
            self.sun_team = None

        if self.last_sun + 13 <= self.iteration_num and not self.fog_work:
            self.sun()

        for i in self.board:
            for j in i:
                j.blocked = False

        self.iteration_A()
        self.field_clean()
        self.iteration_B()
        self.field_clean()

        self.teams[TEAM_A] = [warrior for warrior in self.teams[TEAM_A] if warrior.health > 0]
        self.teams[TEAM_B] = [warrior for warrior in self.teams[TEAM_B] if warrior.health > 0]
        
        for row in self.board:
            for cell in row:
                if cell.typ is not None and cell.typ.health <= 0:
                    cell.typ = None



        
    def iteration_A(self):
        self.calculate_field_warrior(self.teams[TEAM_B])
        for elems in self.teams[TEAM_A]:
            elems.update()

    def iteration_B(self):
        self.calculate_field_warrior(self.teams[TEAM_A])
        for elems in self.teams[TEAM_B]:
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
                    if self.dragging and event.pos[0]<WIN_DIMS[0] and event.pos[1]<WIN_DIMS[1]+BARS_SIZE:
                        self.handle_click(event.pos)
                    self.slider.handle_event(event)

    def handle_click(self, position):

        ### add agent ###

        if position[0]<WIN_DIMS[0] and BARS_SIZE<position[1]<WIN_DIMS[1]+BARS_SIZE and not self.combo_box.active:
            col = position[0]//CELL_SIZE
            row = (position[1]-BARS_SIZE)//CELL_SIZE

            if self.board[col][row].typ == None:
                if not self.start_iteration:
                    match self.combo_box.selected_index:

                        # warrior
                        case 0:
                            self.board[col][row].typ = Warrior(self.board[col][row], TEAM_A, self.num_of_A)
                            self.teams[TEAM_A].append(self.board[col][row].typ)
                            self.num_of_A+=1
                            self.stats.max_healthA += WARRIOR_HEALTH
                        case 1:
                            self.board[col][row].typ = Warrior(self.board[col][row], TEAM_B, self.num_of_B)
                            self.teams[TEAM_B].append(self.board[col][row].typ)
                            self.num_of_B+=1
                            self.stats.max_healthB += WARRIOR_HEALTH
                        # hussar
                        case 2:
                            self.board[col][row].typ = Hussar(self.board[col][row], TEAM_A, self.teams, self.num_of_A)
                            self.teams[TEAM_A].append(self.board[col][row].typ)
                            self.num_of_A+=1
                            self.stats.max_healthA += HUSSAR_HEALTH
                        case 3:
                            self.board[col][row].typ = Hussar(self.board[col][row], TEAM_B, self.teams, self.num_of_B)
                            self.teams[TEAM_B].append(self.board[col][row].typ)
                            self.num_of_B+=1
                            self.stats.max_healthB += HUSSAR_HEALTH

                        # artillery
                        case 4:
                            self.board[col][row].typ = Artillery(self.board[col][row], TEAM_A, self.board, self, self.num_of_A)
                            self.teams[TEAM_A].append(self.board[col][row].typ)
                            self.num_of_A+=1
                            self.stats.max_healthA += ARTILLERY_HEALTH
                        case 5:
                            self.board[col][row].typ = Artillery(self.board[col][row], TEAM_B, self.board, self, self.num_of_B)
                            self.teams[TEAM_B].append(self.board[col][row].typ)
                            self.num_of_B+=1
                            self.stats.max_healthB += ARTILLERY_HEALTH
                        
                        #archer
                        case 6:
                            self.board[col][row].typ = Archer(self.board[col][row], TEAM_A, self.board, self, self.num_of_A)
                            self.teams[TEAM_A].append(self.board[col][row].typ)
                            self.num_of_A+=1
                            self.stats.max_healthA += ARCHER_HEALTH
                        case 7:
                            self.board[col][row].typ = Archer(self.board[col][row], TEAM_B, self.board, self, self.num_of_B)
                            self.teams[TEAM_B].append(self.board[col][row].typ)
                            self.num_of_B+=1
                            self.stats.max_healthB += ARCHER_HEALTH
            else:
                self.stats.agent = self.board[col][row].typ
                if isinstance(self.stats.agent, Warrior):
                    if self.stats.agent.team == TEAM_A:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_warrior.jpg")),(290,250))
                    else:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/germa_warrior.png")),(290,250))
                if isinstance(self.stats.agent, Artillery):
                    if self.stats.agent.team == TEAM_A: 
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_artillery.png")),(290,250))
                    else:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/german_artillery.png")),(290,250))
                if isinstance(self.stats.agent, Hussar):
                    if self.stats.agent.team == TEAM_A:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_warrior.jpg")),(290,250))
                    else:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/germa_warrior.png")),(290,250))
                if isinstance(self.stats.agent, Archer):
                    if self.stats.agent.team == TEAM_A:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/polish_archer.jpg")),(290,250))
                    else:
                        self.stats.agent_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/german_archer.jpg")),(290,250))
                
        ### start ###

        if self.start_button.rect.collidepoint(position):
            if self.start_button.text == 'Start':
                self.start_iteration = True
                self.stats.max_healthA_stop = self.stats.max_healthA
                self.stats.max_healthB_stop = self.stats.max_healthB
            else:
                self.start_iteration = False
                self.stats.healthA_stop = sum(warrior.health for warrior in self.teams[TEAM_A])
                self.stats.healthB_stop = sum(warrior.health for warrior in self.teams[TEAM_B])
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
            self.num_of_B = 0
            self.num_of_A = 0
            self.stats.max_healthA = 0
            self.stats.max_healthB = 0
            self.stats.healthA_stop = 0
            self.stats.healthB_stop = 0
            self.stats.agent = None
            self.clean_is_shooted = False
            self.clean_is_shooted_by_archer = False
            
        if self.fog_button.rect.collidepoint(position):
            self.fog_button.get_clicked()
        
        if self.combo_box.rect.collidepoint(position):
            self.combo_box.handle_event(position,True)
        else:
            self.combo_box.handle_event(position,False)
    

    def render(self):
        self.window.fill(self.bgColor)
        self.window.blit(self.background_image, (0, BARS_SIZE))
        self.window.blit(self.bar_image, (0, WIN_DIMS[1]+BARS_SIZE))
        self.window.blit(pygame.transform.scale(self.bar_image,(WIN_DIMS[0]+STATS_SIZE,BARS_SIZE)), (0, 0))
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                rect_position = (i * CELL_SIZE, j * CELL_SIZE + BARS_SIZE, CELL_SIZE, CELL_SIZE)
                if cell.typ is not None:

                    if isinstance(cell.typ, Warrior):
                        if cell.typ.team == TEAM_A:
                            self.window.blit(self.warrior_A_image, rect_position)
                        else:
                            self.window.blit(self.warrior_B_image, rect_position)
                    if isinstance(cell.typ, Artillery):
                        if cell.typ.team == TEAM_A: 
                            self.window.blit(self.artillery_A_image, rect_position)
                        else:
                            self.window.blit(self.artillery_B_image, rect_position)
                    if isinstance(cell.typ, Hussar):
                        if cell.typ.team == TEAM_A:
                            pygame.draw.rect(self.window, HUSSAR_COLOR_A, rect_position)
                        else:
                            pygame.draw.rect(self.window, HUSSAR_COLOR_B, rect_position)
                    if isinstance(cell.typ, Archer):
                        if cell.typ.team == TEAM_A:
                            self.window.blit(self.archer_A_image, rect_position)
                        else:
                            self.window.blit(self.archer_B_image, rect_position)        
                    if self.stats.agent == cell.typ:
                        pygame.draw.rect(self.window, 'cyan', rect_position, 2)
                    
                if cell.is_shooted:
                    if not cell.is_shooted_by_archer:
                        self.window.blit(self.explosion_image, rect_position)
                    else:
                        self.window.blit(self.arrow_image, rect_position)
                            
                    
                    
        self.start_button.draw()
        self.clear_button.draw()
        self.combo_box.draw()
        self.slider.draw()
        self.fog_button.draw()
        self.stats.draw()
        pygame.display.set_caption(f"Historical battle modeling ({self.iteration_num} iterations)")
        pygame.display.update()
        
    def get_unit_stats(self,team):
        w = a = h = ar = 0
        for unit in self.teams[team]:
            if isinstance(unit, Warrior):
                w += 1
            if isinstance(unit, Hussar):
                h += 1
            if isinstance(unit, Artillery):
                ar += 1
        return w, a, h, ar
