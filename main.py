import cv2
import time

# Outils
from screen_capture import game_screener, screen_init
from display_renderer import create_display, draw_shapes_on_frame, frame_display, debug_display

# détection
from polygones_detection import passive_polygons_detector
from minimap_detection import minimap_detector
from tanks_and_bullets_detection import detect_players_bullets_and_self


# Actions
from actions_decider import actions_decider

# test thread:
import threading
from queue import Queue, Full


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


def capture_analysis(hsv, self_color):
    all_draw_instructions = []
    all_draw_instructions += passive_polygons_detector(hsv)
    all_draw_instructions += minimap_detector(hsv)

    # Nouvelle version : tuple (detections, self_color)
    detections, new_self_color = detect_players_bullets_and_self(hsv, known_self_color=self_color)
    all_draw_instructions += detections
    return all_draw_instructions, new_self_color


def run():
    fps_limit = 40
    frame_duration = 1 / fps_limit
    
    threading.Thread(target=actions_thread_loop, daemon=True).start()

    frame_count = 0
    prev_time = time.time()
    self_color = None
    module_timings = {}  # Dictionnaire pour stocker les temps

    while True:
        frame_count += 1
        start_time = time.time()

        capture_start = time.time()
        capture = game_screener()
        hsv = cv2.cvtColor(capture, cv2.COLOR_BGR2HSV)
        module_timings["Capture+HSV"] = time.time() - capture_start

        # Analyse de l'image
        analysis_start = time.time()
        all_draw_instructions = []
        
        t0 = time.time()
        all_draw_instructions += passive_polygons_detector(hsv)
        module_timings["Passive polygons"] = time.time() - t0

        t0 = time.time()
        all_draw_instructions += minimap_detector(hsv)
        module_timings["Minimap"] = time.time() - t0

        t0 = time.time()
        detections, new_self_color = detect_players_bullets_and_self(hsv, known_self_color=self_color)
        module_timings["Tanks+Bullets"] = time.time() - t0
        all_draw_instructions += detections
        self_color = new_self_color

        module_timings["Total analysis"] = time.time() - analysis_start

        # Affichage image
        t0 = time.time()
        frame = draw_shapes_on_frame(capture.copy(), all_draw_instructions)
        frame_display(frame)
        module_timings["Draw+Display"] = time.time() - t0

        try:
            instruction_queue.put_nowait(all_draw_instructions)
        except Full:
            pass
        
        elapsed = time.time() - start_time
        time_to_sleep = frame_duration - elapsed
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        # Calcul FPS réel
        if frame_count % 5 == 0:
            fps = int(1 / elapsed) if elapsed > 0 else 0
            debug_display(fps, module_timings)

        if cv2.waitKey(1) & 0xFF == ord('k'):
            break
            
    cv2.destroyAllWindows()



def main():
    screen_init() # pas utile, j'ai démarqué un rectangle où screener dans screener()
    create_display()

    run()


if __name__ == "__main__":
    main()
