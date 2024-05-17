class Cell:
    def __init__(self,position):
        self.clicked = False
        self.next_state = False
        self.typ = None
        self.poistion = position
        self.neighbors = None
    
    #GAME_OF_LIVE 
    def live(self):
        result = 0
        for nei in self.neighbors:
            if nei.clicked:
                result+=1
        return result