import time
import pyautogui
import keyboard
# Variables globales pour gérer l'état du mouvement
last_move_key_time = 0
current_key_down = None

# Ne plus initier de mouvement
def reset_movement_state():
    for key in current_key_down:
        pyautogui.keyUp(key)
    current_key_down = None


def move_towards_target(player_position, target_position, threshold=30):
    """
    Fait bouger le joueur vers la position cible selon la direction, en utilisant ZQSD.
    """
    global current_key_down, last_move_key_time

    if time.time() - last_move_key_time < 0.2:
        return

    cx, cy = player_position
    tx, ty = target_position

    dx = tx - cx
    dy = ty - cy
    dist = (dx**2 + dy**2)**0.5

     # Si proche de la cible, relâcher toutes les touches maintenues
    if dist < threshold:
        reset_movement_state()
        return

    # Déterminer quelles touches appuyer selon dx, dy
    keys_to_press = set()
    if abs(dx) > threshold: # Se déplacer horizontalement si écart significatif
        keys_to_press.add('d' if dx > 0 else 'q')
    if abs(dy) > threshold: # Se déplacer verticalement si écart significatif
        keys_to_press.add('s' if dy > 0 else 'z')

    if keys_to_press == current_key_down:
        return

    # Relâcher les touches non désirées
    if current_key_down is None:
        current_key_down = set()
    for key in current_key_down - keys_to_press:
        pyautogui.keyUp(key)

    # Appuyer les nouvelles touches
    for key in keys_to_press - current_key_down:
        pyautogui.keyDown(key)

    current_key_down = keys_to_press
    last_move_key_time = time.time()

# Option avec keyboard
def move_towards_target(target_position, threshold=30):
    global last_move_key_time, current_key_down

    if time.time() - last_move_key_time < 0.2:
        return

    cx, cy = player_position
    tx, ty = target_position

    dx = tx - cx
    dy = ty - cy
    dist = (dx**2 + dy**2)**0.5

    # Si proche de la cible, relâcher toutes les touches maintenues
    if dist < threshold:
        if current_key_down:
            for key in current_key_down:
                keyboard.release(key)
            current_key_down = set()
        return

    # Déterminer quelles touches appuyer selon dx, dy
    keys_to_press = set()
    if abs(dx) > threshold:  # Se déplacer horizontalement si écart significatif
        keys_to_press.add('d' if dx > 0 else 'q')
    if abs(dy) > threshold:  # Se déplacer verticalement si écart significatif
        keys_to_press.add('s' if dy > 0 else 'z')

    if keys_to_press == current_key_down:
        return  # Rien à changer

    # Relâcher les touches non désirées
    for key in current_key_down - keys_to_press:
        keyboard.release(key)

    # Appuyer les nouvelles touches
    for key in keys_to_press - current_key_down:
        keyboard.press(key)

    current_key_down = keys_to_press
    last_move_key_time = time.time()