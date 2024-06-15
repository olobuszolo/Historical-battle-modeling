import pygame
from CONFIG import *
from pathlib import PurePath


class Stats:
    def __init__(self,game):
        self.game = game
        self.max_healthA = 0
        self.max_healthB = 0
        
        self.healthA_stop = 0
        self.healthB_stop = 0
        
        self.agent = None
        self.agent_image = None
        
        self.stats_image = pygame.transform.scale(pygame.image.load(PurePath("./resources/steel.jpg")), (STATS_SIZE, WIN_DIMS[1]))

        
    def draw(self):

        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 30)
        # rect = pygame.Rect(WIN_DIMS[0], BARS_SIZE, STATS_SIZE, WIN_DIMS[1])
        self.game.window.blit(self.stats_image, (WIN_DIMS[0], BARS_SIZE))
        # pygame.draw.rect(self.game.window, 'white', rect)
        
        y_offset = BARS_SIZE + 10
        text = title_font.render("Teams statistics:", True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 60, y_offset))
        y_offset += 30
        text = title_font.render(TEAM_A, True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = title_font.render(TEAM_B, True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 20
        
        teamA_units = self.game.get_unit_stats(TEAM_A)
        teamB_units = self.game.get_unit_stats(TEAM_B)
        
        text = font.render("Kills: " + str(self.game.num_of_B-len(self.game.teams[TEAM_B])), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = font.render("Kills: " + str(self.game.num_of_A-len(self.game.teams[TEAM_A])), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 20
        text = font.render("Warriors: " + str(teamA_units[0]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = font.render("Warriors: " + str(teamB_units[0]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 20
        text = font.render("Archers: " + str(teamA_units[1]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = font.render("Archers: " + str(teamB_units[1]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 20
        text = font.render("Hussar: " + str(teamA_units[2]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = font.render("Hussar: " + str(teamB_units[2]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 20
        text = font.render("Artillery: " + str(teamA_units[3]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = font.render("Artillery: " + str(teamB_units[3]), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 20
        text = font.render("Sum: " + str(sum(teamA_units)), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
        text = font.render("Sum: " + str(sum(teamB_units)), True, (0,0,0))
        self.game.window.blit(text, (WIN_DIMS[0] + 150, y_offset))
        y_offset += 50
        if self.agent!=None:
            stats = self.agent.get_stats().split('\n')
            text = title_font.render("Tracked unit:", True, (0,0,0))
            self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
            y_offset += 30
            for stat in stats:
                text = font.render(stat, True, (0,0,0))
                self.game.window.blit(text, (WIN_DIMS[0] + 50, y_offset))
                y_offset+=20
                
            self.game.window.blit(self.agent_image, (WIN_DIMS[0] + 5, y_offset))
        
        for team_name, team in self.game.teams.items():
            sum_health = 0
            for agent in team:
                sum_health += agent.health
            if self.game.start_iteration:
                self.draw_health_bar(sum_health,team_name, 0)
            else:
                self.draw_health_bar(sum_health,team_name, 1)
                
    def draw_health_bar(self,total_health, team_name, flag):
        font = pygame.font.Font(None, 36)
        
        health_text = font.render(TEAM_A + " HP", True, (0,0,0))
        self.game.window.blit(health_text, (10, 5))
        
        health_text = font.render(TEAM_B + " HP", True, (0,0,0))
        self.game.window.blit(health_text, (2*HEALTH_BAR_WIDTH,5))
        
        if team_name == TEAM_A:
            if self.max_healthA and not flag:
                max_health = self.max_healthA
                bar_width = int((total_health / max_health) * HEALTH_BAR_WIDTH)
                pygame.draw.rect(self.game.window, 'green', (15 + 70, BARS_SIZE//2, bar_width, HEALTH_BAR_HEIGHT), 0, 5)
                pygame.draw.rect(self.game.window, 'black', (15 + 70, BARS_SIZE//2, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 3, 5)
                health_text = font.render(str(total_health), True, (0,0,0))
                self.game.window.blit(health_text, (10, BARS_SIZE//2))
            if flag:
                if self.max_healthA > 0:
                    max_health = self.max_healthA
                    bar_width = int((total_health / max_health) * HEALTH_BAR_WIDTH)
                    pygame.draw.rect(self.game.window, 'green', (15 + 70, BARS_SIZE//2, bar_width, HEALTH_BAR_HEIGHT), 0, 5)
                    pygame.draw.rect(self.game.window, 'black', (15 + 70, BARS_SIZE//2, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 3, 5)
                health_text = font.render(str(self.healthA_stop), True, (0,0,0))
                self.game.window.blit(health_text, (10, BARS_SIZE//2))
        if team_name == TEAM_B:
            if self.max_healthB and not flag:
                max_health = self.max_healthB
                bar_width = int((total_health / max_health) * HEALTH_BAR_WIDTH)
                pygame.draw.rect(self.game.window, 'red', (HEALTH_BAR_WIDTH + 85, BARS_SIZE//2, bar_width, HEALTH_BAR_HEIGHT), 0, 5)
                pygame.draw.rect(self.game.window, 'black', (HEALTH_BAR_WIDTH + 85, BARS_SIZE//2, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 3, 5)
                health_text = font.render(str(total_health), True, (0,0,0))
                self.game.window.blit(health_text, (90 + 2*HEALTH_BAR_WIDTH, BARS_SIZE//2))
            if flag:
                if self.max_healthB > 0:
                    max_health = self.max_healthB
                    bar_width = int((total_health / max_health) * HEALTH_BAR_WIDTH)
                    pygame.draw.rect(self.game.window, 'red', (HEALTH_BAR_WIDTH + 85, BARS_SIZE//2, bar_width, HEALTH_BAR_HEIGHT), 0, 5)
                    pygame.draw.rect(self.game.window, 'black', (HEALTH_BAR_WIDTH + 85, BARS_SIZE//2, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 3, 5)
                health_text = font.render(str(self.healthB_stop), True, (0,0,0))
                self.game.window.blit(health_text, (90 + 2*HEALTH_BAR_WIDTH, BARS_SIZE//2))