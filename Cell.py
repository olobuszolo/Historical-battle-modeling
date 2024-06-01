from CONFIG import *
import math
import random

class Cell:
    def __init__(self, position):
        self.typ = None
        self.next_type = None
        self.position = position
        self.x = position[0]
        self.y = position[1]
        self.neighbors = []
        self.fight_neighbours = []
        self.blocked = False
        self.staticField = SFMAX
        self.n_targetted = 0
    
class Warrior:
    def __init__(self, cell, team):
        self.cell = cell
        self.team = team
        
    def move(self):
        go_down = float('-inf')
        nextt = None
        for nei in self.cell.neighbors:
            if nei.position[0] > go_down and self.cell.position[1] == nei.position[1] and nei.typ == None and not nei.blocked:
                go_down = nei.position[0]
                nextt = nei
        if nextt != None:
            nextt.blocked = True
            nextt.next_type = self
            self.cell.next_type = None
            self.cell = nextt
        else:
            self.cell.next_type = self.cell.typ
            self.cell.blocked = True

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
