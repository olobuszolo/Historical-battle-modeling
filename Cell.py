from CONFIG import *
import random

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
    
    def get_damage(self):
        self.health -= random_int(1, MAX_DAMAGE_WARIOR)

        
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
        opp[fight_with_oppenent].typ.get_damage()



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


def random_int(mini, maxi):
    return random.randint(mini, maxi)