import cv2
import time

# Outils
from screen_capture import game_screener, screen_init
from display_renderer import create_display, draw_shapes_on_frame, frame_display, debug_display

# détection
from polygones_detection import passive_polygons_detector
from minimap_detection import minimap_detector
from tanks_and_bullets_detection import detect_players_bullets_and_self
from calculate_speed import estimate_background_speed

# Mesures
from calculate_speed import calculate_things_speed

# Actions
from actions_decider import actions_decider

# Istanciation
from calculate_speed import EntityTracker
entity_tracker = EntityTracker()


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


def detect_on_capture(prev_hsv,hsv, self_color, speed_history):
    all_draw_instructions = []

    # Nouvelle version : tuple (detections, self_color)
    detections, new_self_color = detect_players_bullets_and_self(hsv, known_self_color=self_color)
    all_draw_instructions += detections

    all_draw_instructions += passive_polygons_detector(hsv)
    all_draw_instructions += minimap_detector(hsv)

    new_draws, speed_history = estimate_background_speed(prev_hsv, hsv, speed_history=speed_history)
    all_draw_instructions += new_draws
    return all_draw_instructions, new_self_color, speed_history


def analyse_things_detected(all_draw_instructions, capture_time, current_frame):
    global entity_tracker
   
    all_draw_instructions += calculate_things_speed(all_draw_instructions, entity_tracker, current_frame, capture_time)
    return all_draw_instructions



def run():
    threading.Thread(target=actions_thread_loop, daemon=True).start()

    frame_count = 0
    prev_time = time.time()
    self_color = None
    prev_hsv = None
    speed_history = []
    module_timings = {}  # Dictionnaire pour stocker les temps

    while True:
        frame_count += 1
        start_time = time.time()

        capture_start = time.time()
        capture = game_screener()
        capture_time = time.time()
        hsv = cv2.cvtColor(capture, cv2.COLOR_BGR2HSV)
        module_timings["Capture+HSV"] = time.time() - capture_start

        # Détections sur l'image
        all_draw_instructions, new_self_color, speed_history = detect_on_capture(prev_hsv, hsv, self_color, speed_history)
        self_color = new_self_color
        # print (all_draw_instructions)
        # Analyse des détections
        all_draw_instructions = analyse_things_detected(all_draw_instructions, capture_time, capture)

        try:
            instruction_queue.put_nowait(all_draw_instructions)
        except Full:
            pass
        

        # Affichage image
        t0 = time.time()
        frame = draw_shapes_on_frame(capture.copy(), all_draw_instructions)
        frame_display(frame)
        module_timings["Draw+Display"] = time.time() - t0

        prev_hsv = hsv.copy()
        
        elapsed = time.time() - start_time
        # time_to_sleep = frame_duration - elapsed
        # if time_to_sleep > 0:
        #     time.sleep(time_to_sleep)

        # Calcul FPS réel
        if frame_count % 5 == 0:
            fps = int(1 / elapsed) if elapsed > 0 else 0
            debug_display(fps, module_timings)

        if cv2.waitKey(1) & 0xFF == ord('k'):
            break
            
    cv2.destroyAllWindows()



def main():
    screen_init()
    create_display()

    run()


if __name__ == "__main__":
    main()
