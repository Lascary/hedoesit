import mss
import numpy as np
import cv2
import pygetwindow as gw
import win32con
import win32gui
import time


# Outils
from screen_capture import screen_init, game_screener
from display_renderer import create_display, draw_shapes_on_frame, frame_display

# détection
from polygones_detection import passive_polygons_detector

# Actions
from actions_decider import actions_decider

# je capture = capture
# je reçois l'image  rendue = analyzed_frame

auto_fire_on = False  # variable globale, accessible dans farm()
# last_auto_fire = 0

def main():
    # screen_init() pas utile, j'ai démarqué un rectangle où screener dans screener()
    create_display()

    run()

def capture_analysis(capture):
    all_draw_instructions = []
    all_draw_instructions += passive_polygons_detector(capture)

    return all_draw_instructions

def run():
    
    while True:
        global auto_fire_on
        capture = game_screener()
        all_draw_instructions = capture_analysis(capture) # lance les reconnaissances d'image // fait dans display_renderer = frame_renderer
        frame = draw_shapes_on_frame(capture.copy(), all_draw_instructions)
        frame_display(frame) # affiche frame finale
        auto_fire_on = actions_decider(all_draw_instructions, auto_fire_on)
        


        if cv2.waitKey(1) & 0xFF == ord('k'):
            break
            
    cv2.destroyAllWindows()




if __name__ == "__main__":
    main()
