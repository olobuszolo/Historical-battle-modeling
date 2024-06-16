import pygame
from MainGame import *

def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load("./resources/muzyka.mp3") 
    pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()
    pygame.mixer.quit()

if __name__ == "__main__":
    play_music()
    
    try:
        game = MainGame()
        game.play()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        stop_music()
