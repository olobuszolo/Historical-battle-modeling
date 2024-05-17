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
    def __init__(self, game, x, y, options, selected_index=0):
        self.game = game
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont('Arial',18)
        self.rect = pygame.rect.Rect((self.x, self.y), (150, 25))
        self.options = options
        self.selected_index = selected_index
        self.active = False
        
    def draw(self):
        pygame.draw.rect(self.game.window, 'gray', self.rect, 0 , 5)
        pygame.draw.rect(self.game.window, 'black', self.rect, 2 , 5)

        selected_text = self.font.render(str(self.options[self.selected_index]), True, 'black')
        self.game.window.blit(selected_text, (self.rect.x + 5, self.rect.y + 5))

        if self.active:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y - (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(self.game.window, 'gray', option_rect, 0 , 5)
                pygame.draw.rect(self.game.window, 'black', option_rect, 2 , 5)
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
                
class Slider:
    def __init__(self,game, x, y, w, h, min_val=0, max_val=100):
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = (min_val + max_val) // 2
        self.dragging = False

    def draw(self):
        pygame.draw.rect(self.game.window, 'gray', self.rect, 0 , 5)
        pygame.draw.rect(self.game.window, 'black', self.rect, 2 , 5)
        handle_pos = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.w
        handle_rect = pygame.Rect(handle_pos - 5, self.rect.y, 10, self.rect.h)
        pygame.draw.rect(self.game.window, (0, 0, 0), handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                relative_x = mouse_x - self.rect.x
                relative_x = max(0, min(relative_x, self.rect.w))
                self.value = self.min_val + (relative_x / self.rect.w) * (self.max_val - self.min_val)

    def get_value(self):
        return int(self.value)

    def set_value(self, value):
        if self.min_val <= value <= self.max_val:
            self.value = value
        else:
            raise ValueError(f"Value out of range ({self.min_val}-{self.max_val})")
