import pygame

class Button:
    def __init__(self,game,text,x,y,enabled):
        self.game = game
        self.text = text
        self.x = x
        self.y = y
        self.enabled = enabled
        self.font = pygame.font.SysFont('Arial',18)
        self.rect = pygame.rect.Rect((self.x, self.y), (150, 25))
        
    def draw(self):
        button_text = self.font.render(self.text,True, 'black')
        pygame.draw.rect(self.game.window, 'gray', self.rect, 0 , 5)
        pygame.draw.rect(self.game.window, 'black', self.rect, 2 , 5)
        self.game.window.blit(button_text,(self.x+3,self.y+3))
    
    def get_clicked(self):
        pass
        
class StartButton(Button):
    def get_clicked(self):
        if self.text == 'Start':
            self.text = 'Stop'
        else:
            self.text = 'Start'

class ClearButton(Button):
    def get_clicked(self):
        return super().get_clicked()
    
class ComboBox():
    def __init__(self, game, x, y, w, h, options, selected_index=0):
        self.game = game
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont('Arial',18)
        self.rect = pygame.rect.Rect((self.x, self.y), (150, 25))
        self.options = options
        self.selected_index = selected_index
        self.active = False
        
    def draw(self):
        pygame.draw.rect(self.game.window, 'white', self.rect)
        pygame.draw.rect(self.game.window, 'black', self.rect, 2)

        selected_text = self.font.render(str(self.options[self.selected_index]), True, 'black')
        self.game.window.blit(selected_text, (self.rect.x + 5, self.rect.y + 5))

        if self.active:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y - (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(self.game.window, 'white', option_rect)
                pygame.draw.rect(self.game.window, 'black', option_rect, 2)
                option_text = self.font.render(str(option), True, 'black')
                self.game.window.blit(option_text, (option_rect.x + 5, option_rect.y + 5))
                
    def handle_event(self,position,pred):
        if pred:
                self.active = not self.active
        elif self.active:
            for i in range(len(self.options)):
                option_rect = pygame.Rect(self.rect.x, self.rect.y - (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                if option_rect.collidepoint(position):
                    self.selected_index = i
                    self.active = False
                    break
            else:
                self.active = False