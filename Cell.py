from CONFIG import *
import random
import math

class Cell:
    def __init__(self,position):
        self.typ = None
        self.next_type = None
        self.position = position
        self.neighbours = None
        self.fight_neighbours = []
        self.blocked = False
        self.staticField = SFMAX

    def calc_static_field(self):
        min_static_field = SFMAX
        if self.neighbours:
            min_static_field = min(neighbour.staticField for neighbour in self.neighbours)
        
        if self.staticField > min_static_field + 1:
            self.staticField = min_static_field + 1
            return True
        
        return False
    
class Warrior:
    def __init__(self,cell, team):
        self.cell = cell
        self.team = team 
        self.health = WARRIOR_HEALTH
        self.fight = False
    
    def calc_static_field(self):
        return self.cell.calc_static_field()
        
    def move(self):
        min_field = SFMAX
        target_cell = None
        
        if not self.fight:
            for neighbour in self.cell.neighbours:
                if neighbour.staticField < min_field and not neighbour.blocked and neighbour.typ == None :
                    min_field = neighbour.staticField
                    target_cell = neighbour

        if target_cell is not None:
            target_cell.blocked = True
            target_cell.next_type = self.cell.typ
            self.cell.next_type = None

            self.cell.typ = self.cell.next_type
            target_cell.typ = target_cell.next_type
            target_cell.next_type = None
            self.cell = target_cell
        else:
            self.cell.next_type = self.cell.typ
            self.cell.blocked = True

            self.cell.typ = self.cell.next_type
            self.cell.next_type = None            

    def fight_process(self, n, opp):
        fight_with_oppenent = random_int(0, n - 1)
        opp[fight_with_oppenent].typ.health -= random_int(1, MAX_DAMAGE_WARIOR)

    def fight_with(self):
        current_opponents = []
        if not self.cell.fight_neighbours:
            return
        
        if self.team == TEAM_A:
            for nei in self.cell.fight_neighbours:
                if nei.typ is not None and nei.typ.team == TEAM_B:
                    current_opponents.append(nei)
        else:
            for nei in self.cell.fight_neighbours:
                if nei.typ is not None and nei.typ.team == TEAM_A:
                    current_opponents.append(nei)

        num_of_opp = len(current_opponents)
        if num_of_opp > 0:
            self.fight = True
            self.fight_process(num_of_opp, current_opponents)

    def update(self):
        self.fight_with()
        if not self.fight:
            self.move()
        self.fight = False

class Artillery:
    def __init__(self, cell, team, board, game):
        self.cell = cell
        self.team = team 
        self.health = ARTILLERY_HEALTH
        self.fight = False
        self.engagement_range = ARTILLERY_RANGE
        self.game = game
        self.board = board
        self.last_move = -10
        self.last_shoot = -10


    def count_team_neighbours(self, target_cell):
        team_neighbours = 0
        for neighbour in target_cell.neighbours:
            if neighbour.typ is not None and neighbour.typ.team == self.team:
                team_neighbours += 1
        return team_neighbours

    def find_target(self):
        min_field = float('inf')
        target_cell = None
        cx, cy = self.cell.position
        for row in self.board:
            for cell in row:
                x, y = cell.position
                curr_teammates = self.count_team_neighbours(cell)
                distance = math.sqrt((cx - x)**2 + (cy - y)**2)
                if distance <= self.engagement_range and cell.staticField  + 2*curr_teammates< min_field:
                    min_field = cell.staticField
                    target_cell = cell

        for nei in target_cell.fight_neighbours:
            if nei.typ is not None and nei.typ.team is not self.team:
                return target_cell
                
        return None


    def full_damage_process(self, target):
        if target and target.typ:
            target.typ.health -= random.randint(1, MAX_ARTILLERY_DAMAGE)
            self.last_shoot = self.game.iteration_num
        for nei in self.cell.fight_neighbours:
            damage = random.randint(1, MAX_ARTILLERY_DAMAGE) * 0.5
            if nei.typ is not None:
                nei.typ.health -= damage
                self.last_shoot = self.game.iteration_num


    def fight_with(self):
        target = self.find_target()
        if target is not None:
            self.full_damage_process(target)

    def move(self):
        min_field = SFMAX
        target_cell = None
        
        if not self.fight:
            for neighbour in self.cell.neighbours:
                if neighbour.staticField < min_field and not neighbour.blocked and neighbour.typ == None :
                    min_field = neighbour.staticField
                    target_cell = neighbour

        if target_cell is not None:
            target_cell.blocked = True
            target_cell.next_type = self.cell.typ
            self.cell.next_type = None

            self.cell.typ = self.cell.next_type
            target_cell.typ = target_cell.next_type
            target_cell.next_type = None
            self.cell = target_cell
            self.last_move = self.game.iteration_num

        else:
            self.cell.next_type = self.cell.typ
            self.cell.blocked = True

            self.cell.typ = self.cell.next_type
            self.cell.next_type = None     

    def update(self):
        print(self.game.iteration_num)
        if self.last_shoot + 2 <= self.game.iteration_num:
            self.fight_with()
        if self.last_move + 4 <= self.game.iteration_num and self.game.iteration_num != self.last_shoot:
            self.move()




def random_int(mini, maxi):
    return random.randint(mini, maxi)