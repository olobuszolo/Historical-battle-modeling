from CONFIG import *
import random
import math


class Cell:
    def __init__(self, position):
        self.typ = None
        self.next_type = None
        self.position = position
        self.x = position[0]
        self.y = position[1]
        self.n_targetted = 0
        self.neighbors = None
        self.fight_neighbors = []
        self.blocked = False
        self.staticField = SFMAX

    def calc_static_field(self):
        min_static_field = SFMAX
        if self.neighbors:
            min_static_field = min(neighbor.staticField for neighbor in self.neighbors)
        
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
            for neighbor in self.cell.neighbors:
                if neighbor.staticField < min_field and not neighbor.blocked and neighbor.typ == None :
                    min_field = neighbor.staticField
                    target_cell = neighbor

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
        if not self.cell.fight_neighbors:
            return
        
        if self.team == TEAM_A:
            for nei in self.cell.fight_neighbors:
                if nei.typ is not None and nei.typ.team == TEAM_B:
                    current_opponents.append(nei)
        else:
            for nei in self.cell.fight_neighbors:
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


    def count_team_neighbors(self, target_cell):
        team_neighbors = 0
        for neighbor in target_cell.neighbors:
            if neighbor.typ is not None and neighbor.typ.team == self.team:
                team_neighbors += 1
        return team_neighbors

    def find_target(self):
        min_field = float('inf')
        target_cell = None
        cx, cy = self.cell.position
        for row in self.board:
            for cell in row:
                x, y = cell.position
                curr_teammates = self.count_team_neighbors(cell)
                distance = math.sqrt((cx - x)**2 + (cy - y)**2)
                if distance <= self.engagement_range and cell.staticField  + 2*curr_teammates< min_field:
                    min_field = cell.staticField
                    target_cell = cell

        for nei in target_cell.fight_neighbors:
            if nei.typ is not None and nei.typ.team is not self.team:
                return target_cell
                
        return None


    def full_damage_process(self, target):
        if target and target.typ:
            target.typ.health -= random.randint(1, MAX_ARTILLERY_DAMAGE)
            self.last_shoot = self.game.iteration_num
        for nei in self.cell.fight_neighbors:
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
            for neighbor in self.cell.neighbors:
                if neighbor.staticField < min_field and not neighbor.blocked and neighbor.typ == None :
                    min_field = neighbor.staticField
                    target_cell = neighbor

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

class Hussar:
    def __init__(self, cell, team, teams):
        self.cell = cell
        self.team = team
        self.enemy_team = TEAM_B if team == TEAM_A else TEAM_A
        self.teams = teams
        self.health = HUSSAR_HEALTH
        self.fight = False

    def find_target(self):
        closest_target = None
        closest_distance = float('inf')

        for enemy in self.teams[self.enemy_team]:
            distance = get_distance(self.cell.x, self.cell.y, enemy.cell.x, enemy.cell.y)
            if distance < closest_distance:
                closest_distance = distance
                closest_target = enemy

        if closest_target is not None:
            closest_target.cell.n_targetted += 1

        return closest_target

    def move(self):
        self.cell.blocked = True

        if self.fight:
            return
        
        closest_target = self.find_target()

        if closest_target is None:
            self.cell.next_type = self
            return

        for _ in range(HUSSAR_SPEED):
            new_cell = get_move_cell(self.cell, closest_target.cell)

            new_cell.blocked = True
            new_cell.next_type = self

            self.cell.next_type = None
            self.cell.blocked = False
            self.cell = new_cell

            # slow down (random)
            if random.randint(1, 10) <= HUSSAR_SLOW_DOWN_CHANCE:
                break 
    def update(self):
        self.move()

        

def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def get_move_cell(cell1, cell2):
    closest_distance = float('inf')
    closest_nei = cell1

    for nei in cell1.neighbors:
        distance = get_distance(nei.x, nei.y, cell2.x, cell2.y)
        if distance < closest_distance and not nei.blocked:
            closest_distance = distance
            closest_nei = nei
    
    return closest_nei

def random_int(mini, maxi):
    return random.randint(mini, maxi)