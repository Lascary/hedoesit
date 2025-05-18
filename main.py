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

# test thread:
import threading
from queue import Queue
from actions_decider import actions_decider

auto_fire_on = False
instruction_queue = Queue(maxsize=1) # maxsize=1 pour ne jamais accumuler de retard
lock = threading.Lock()

def actions_thread_loop():
    global auto_fire_on
    while True:
        try:
            # Attend qu'une nouvelle frame d'instructions soit disponible (max 0.1s)
            all_draw_instructions = instruction_queue.get(timeout=0.1)
            with lock:
                auto_fire_on = actions_decider(all_draw_instructions, auto_fire_on)
        except:
            continue  # Timeout ou vide, on passe à la suite

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
    fps_limit = 40
    frame_duration = 1 / fps_limit
    
    # Démarre le thread d'action
    threading.Thread(target=actions_thread_loop, daemon=True).start()
    
    while True:
        start_time = time.time()

        global auto_fire_on
        capture = game_screener()
        all_draw_instructions = capture_analysis(capture) # lance les reconnaissances d'image // fait dans display_renderer = frame_renderer
        frame = draw_shapes_on_frame(capture.copy(), all_draw_instructions)
        frame_display(frame) # affiche frame finale

        # Envoie les instructions au thread, sans bloquer
        if not instruction_queue.full():
            instruction_queue.put(all_draw_instructions)
        # pour THREAD : auto_fire_on = actions_decider(all_draw_instructions, auto_fire_on)
        
        elapsed = time.time() - start_time
        time_to_sleep = frame_duration - elapsed
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        if cv2.waitKey(1) & 0xFF == ord('k'):
            break
            
    cv2.destroyAllWindows()




if __name__ == "__main__":
    main()
