class Cell:
    def __init__(self,position):
        self.typ = None
        self.next_type = None
        self.position = position
        self.neighbors = None
    
class Warrior:
    def __init__(self,cell):
        self.cell = cell
        
    def move(self):
        go_down = float('inf')
        nextt = None
        for nei in self.cell.neighbors:
            if nei.position[1] < go_down and self.cell.position[0] == nei.position[0]:
                go_down = nei.position[1]
                nextt = nei
        if nextt != None:
            nextt.next_type = self.cell.typ
            self.cell.next_type = None
            self.cell = nextt