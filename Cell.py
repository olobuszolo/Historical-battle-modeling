class Cell:
    def __init__(self,position):
        self.typ = None
        self.next_type = None
        self.position = position
        self.neighbors = None
        self.blocked = False
    
class Warrior:
    def __init__(self,cell):
        self.cell = cell
        
    def move(self):
        go_down = float('-inf')
        nextt = None
        for nei in self.cell.neighbors:
            if nei.position[0] > go_down and self.cell.position[1] == nei.position[1] and nei.typ == None and not nei.blocked:
                go_down = nei.position[0]
                nextt = nei
        if nextt != None:
            nextt.blocked = True
            nextt.next_type = self.cell.typ
            self.cell.next_type = None
            self.cell = nextt
        else:
            self.cell.next_type = self.cell.typ
            self.cell.blocked = True