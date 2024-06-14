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
        self.is_shooted = False
        self.is_shooted_by_archer = False
        

    def calc_static_field(self):
        min_static_field = SFMAX
        if self.neighbors:
            min_static_field = min(neighbor.staticField for neighbor in self.neighbors)
        
        if self.staticField > min_static_field + 1:
            self.staticField = min_static_field + 1
            return True
        
        return False
    
class Warrior:
    def __init__(self, cell, team, iden):
        self.cell = cell
        self.team = team 
        self.health = WARRIOR_HEALTH
        self.fight = False
        self.iden = iden
    
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
    
    def get_stats(self):
        return f"Team: {self.team}\nType: {self.__class__.__name__}\nID: {self.iden}\nHP: {self.health if self.health >=0 else 0}\n"
        

class Artillery:
    def __init__(self, cell, team, board, game, iden):
        self.cell = cell
        self.team = team 
        self.health = ARTILLERY_HEALTH
        self.fight = False
        self.engagement_range = ARTILLERY_RANGE
        self.game = game
        self.board = board
        self.last_move = -10
        self.last_shoot = -10
        self.shooting_range = SHOOT_RANGE
        self.iden = iden


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
                if distance <= self.engagement_range and cell.staticField  + 2*curr_teammates <= min_field:
                    min_field = cell.staticField
                    target_cell = cell

        for nei in target_cell.fight_neighbors:
            if nei.typ is not None and nei.typ.team is not self.team:
                return target_cell
        if target_cell.typ is not None and target_cell.typ.team is not self.team:
            return target_cell
                
        return None


    def full_damage_process(self, target):
        target.is_shooted = True
        if target:
            if target and target.typ:
                target.typ.health -= random.randint(1, MAX_ARTILLERY_DAMAGE)
                self.last_shoot = self.game.iteration_num

        for nei in target.fight_neighbors:
            damage = random.randint(1, MAX_ARTILLERY_DAMAGE) * 0.5
            if nei.typ is not None:
                nei.typ.health -= damage
                self.last_shoot = self.game.iteration_num


    def fight_with(self):
        target = self.find_target()
        if target is not None:
            self.last_shoot = self.game.iteration_num
            probability = random_int(1, 10)
            if probability <= 1:
                self.full_damage_process(target)
            elif probability <= 9:
                new_x = target.position[0] + random_int(-self.shooting_range, self.shooting_range)
                new_y = target.position[1] + random_int(-self.shooting_range, self.shooting_range)
                if new_y >= WIN_DIMS[1] or new_y <= 0 or new_x >= WIN_DIMS[0] or new_x <= 0:
                    return
                new_target = self.game.board[new_y][new_x]
                self.full_damage_process(new_target)
            else:
                pass


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
        if self.game.fog_work:
            self.shooting_range = SHOOT_RANGE + 2
        if (not self.game.fog_work and self.shooting_range != SHOOT_RANGE) and (self.game.sun_team != self.team):
            self.shooting_range = SHOOT_RANGE
        if self.game.sun_work and self.game.sun_team == self.team:
            self.shooting_range = SHOOT_RANGE + 2


        if self.last_shoot + 2 <= self.game.iteration_num:
            self.fight_with()
        if self.last_move + 5 <= self.game.iteration_num:
            self.move()
        
        
    def get_stats(self):
        return f"Team: {self.team}\nType: {self.__class__.__name__}\nID: {self.iden}\nHP: {self.health if self.health >=0 else 0}\n"
        # if self.game.sun_work or self.game.fog_work:
        #     print(str(self.game.iteration_num) + str(self.game.sun_work) + str(self.team) + str(self.game.sun_team) + str(self.game.fog_work) + str(self.shooting_range))

class Hussar:
    def __init__(self, cell, team, teams, iden):
        self.cell = cell
        self.team = team
        self.enemy_team = TEAM_B if team == TEAM_A else TEAM_A
        self.teams = teams
        self.health = HUSSAR_HEALTH
        self.fight = False
        self.iden = iden

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
            new_cell.next_type = self.cell.typ

            self.cell.next_type = None

            self.cell.typ = self.cell.next_type
            new_cell.typ = new_cell.next_type
            new_cell.next_type = None
            self.cell = new_cell

            # slow down (random)
            if random.randint(1, 10) <= HUSSAR_SLOW_DOWN_CHANCE:
                break 

    def update(self):
        self.move()
        
    def get_stats(self):
        return f"Team: {self.team}\nType: {self.__class__.__name__}\nID: {self.iden}\nHP: {self.health if self.health >=0 else 0}\n"
        # return self.health

class Archer:
    def __init__(self, cell, team, board, game, iden):
        self.cell = cell
        self.team = team 
        self.health = ARCHER_HEALTH
        self.fight = False
        self.engagement_range = ARCHER_RANGE
        self.game = game
        self.board = board
        self.last_move = -5
        self.last_shoot = -3
        self.shooting_range = 1
        self.iden = iden


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
                if distance <= self.engagement_range and cell.staticField  + curr_teammates <= min_field:
                    min_field = cell.staticField
                    target_cell = cell

        for nei in target_cell.fight_neighbors:
            if nei.typ is not None and nei.typ.team is not self.team:
                return target_cell
        if target_cell.typ is not None and target_cell.typ.team is not self.team:
            return target_cell
                
        return None


    def full_damage_process(self, target, t):
        target.is_shooted = True
        target.is_shooted_by_archer = True
        if target:
            if target and target.typ:
                if t == 'a':
                    target.typ.health -= random.randint(1, MAX_ARCHER_SHOT_DAMAGE)
                    self.last_shoot = self.game.iteration_num
                else:
                    target.typ.health -= random.randint(1, MAX_ARCHER_DAMAGE)

    def fight_with(self):
        target = self.find_target()
        if target is not None:
            # self.last_shoot = self.game.iteration_num
            if target.position[0] in [self.cell.x-1,self.cell.x,self.cell.x+1] and target.position[1] in [self.cell.y-1,self.cell.y,self.cell.y+1]:
                self.full_damage_process(target,'s')
            elif self.last_shoot + 2 <= self.game.iteration_num:
                self.last_shoot = self.game.iteration_num
                probability = random_int(1, 10)
                if probability <= 1:
                    self.full_damage_process(target,'a')
                elif probability <= 9:
                    if random.random() < 5:
                        new_x = target.position[0] + random_int(-self.shooting_range, self.shooting_range)
                        new_y = target.position[1]
                    else:
                        new_x = target.position[0]
                        new_y = target.position[1] + random_int(-self.shooting_range, self.shooting_range)
                    if new_y >= WIN_DIMS[1] or new_y <= 0 or new_x >= WIN_DIMS[0] or new_x <= 0:
                        return
                    new_target = self.game.board[new_y][new_x]
                    self.full_damage_process(new_target,'a')
                else:
                    pass


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
        if self.game.fog_work:
            self.shooting_range = 3
        if (not self.game.fog_work and self.shooting_range != SHOOT_RANGE) and (self.game.sun_team != self.team):
            self.shooting_range = 1
        if self.game.sun_work and self.game.sun_team == self.team:
            self.shooting_range = 1 + 2


        # if self.last_shoot + 2 <= self.game.iteration_num:
        self.fight_with()
        if self.last_move + 5 <= self.game.iteration_num:
            self.move()
        
        
    def get_stats(self):
        return f"Team: {self.team}\nType: {self.__class__.__name__}\nID: {self.iden}\nHP: {self.health if self.health >=0 else 0}\n"

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