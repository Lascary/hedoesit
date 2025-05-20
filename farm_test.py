import time
import pyautogui


CAPTURE_TOP = 114
CAPTURE_LEFT = 685

# Pour éviter que la souris vise tjrs un objet différent
last_target_positions = []
last_move_mouse_time = 0

current_key_down = None
last_move_key_time = 0


def aim_at_target(target):
    global last_move_mouse_time
    now = time.time()
    if now - last_move_mouse_time > 0.1:  # 0.2 = limite les moves à 5 fois/seconde max
        if "position" in target:
            x, y = target["position"]
            screen_x = CAPTURE_LEFT + x
            screen_y = CAPTURE_TOP + y
            pyautogui.moveTo(screen_x, screen_y)
        last_move_mouse_time = now

# centre de la partie de l'écran capturée
center_x, center_y = 680 // 2, 610 // 2
# priorité des couleurs
color_priority = {"blue_pentagon": 0, "red_triangle": 1, "yellow_square": 2}

# Tri des shapes to farm par ordre de priorité
def sort_key(target):
    x, y = target["position"]
    dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
    priority = color_priority.get(target["type"], 99)
    return (dist, priority)

def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5


# déplacements
def move_towards_target(target_position, threshold=30):
    global last_move_key_time, current_key_down

    if time.time() - last_move_key_time < 0.2:
        return

    cx, cy = center_x, center_y
    tx, ty = target_position

    dx = tx - cx
    dy = ty - cy
    dist = (dx**2 + dy**2)**0.5

    # Si proche de la cible, relâcher toutes les touches maintenues
    if dist < threshold:
        if current_key_down:
            for key in current_key_down:
                pyautogui.keyUp(key)
            current_key_down = set()
        return

    # Déterminer quelles touches appuyer selon dx, dy
    keys_to_press = set()
    if abs(dx) > threshold:  # Se déplacer horizontalement si écart significatif
        keys_to_press.add('d' if dx > 0 else 'q')
    if abs(dy) > threshold:  # Se déplacer verticalement si écart significatif
        keys_to_press.add('s' if dy > 0 else 'z')

    if keys_to_press == current_key_down:
        return  # Rien à changer, ne fait rien

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


# Choisit la manière adaptée de farmer
# global farm si les shapes sont groupées et d'un côté
# sinon : one_by_one_farm
def farm(farm_targets, auto_fire_on):
    
    should_farm = bool(farm_targets)
    if should_farm:
        print("farm")
        if len(farm_targets) < 5:
            auto_fire_on = one_by_one_farm(farm_targets)
        else:
            global_farm(farm_targets)
    
        if not auto_fire_on:
            pyautogui.press('e')  # active le mode tir auto
            auto_fire_on = True
            
    elif not should_farm and auto_fire_on:
        pyautogui.press('e')  # désactive le mode tir auto
        auto_fire_on = False

        # Relâche la touche de déplacement si elle est maintenue
        if current_key_down is not None:
            for key in current_key_down:
                pyautogui.keyUp(key)
            current_key_down = None

    return auto_fire_on
        

# Traite tout un côté
def global_farm(farm_targets):
    print("global farm")
    global current_key_down, last_move_mouse_time

    if not farm_targets:
        return

    # Récupère les coordonnées des cibles
    targets_x_list = [target["position"][0] for target in farm_targets]
    targets_y_list = [target["position"][1] for target in farm_targets]

    # Calculer la médiane des positions
    median_x = sorted(targets_x_list)[len(targets_x_list)//2]
    median_y = sorted(targets_y_list)[len(targets_y_list)//2]

    dx = median_x - center_x
    dy = median_y - center_y

    # Vise à 45° dans la direction dominante
    angle_x = 100 if dx > 0 else -100
    angle_y = 100 if dy > 0 else -100
    pyautogui.moveTo(CAPTURE_LEFT + center_x + angle_x,
                     CAPTURE_TOP + center_y + angle_y)
    print("mouse move")
    last_move_mouse_time = time.time()

    # Détermine le déplacement selon la direction dominante
    abs_dx, abs_dy = abs(dx), abs(dy)
    move_keys = set()

    if abs_dx > abs_dy:
        print("move hori")
        move_keys.add('d' if dx > 0 else 'q')  # droite/gauche
    else:
        print("move vert")
        move_keys.add('s' if dy > 0 else 'z')  # bas/haut

    # Appliquer les touches
    if current_key_down != move_keys:
        if current_key_down:
            for key in current_key_down:
                pyautogui.keyUp(key)
        for key in move_keys:
            pyautogui.keyDown(key)
        current_key_down = move_keys



# Traite les shapes une par une
def one_by_one_farm(farm_targets, auto_fire_on):
    global last_target_positions, last_move_mouse_time, current_key_down

    # tri des cibles par priorité 
    farm_targets.sort(key=sort_key)
    top_targets = farm_targets[:5]
    positions = [item["position"] for item in top_targets]

    # Vérifie si les 5 cibles prioritaires ont peu bougé (≤10 pixels)
    positions_stable = (
        len(last_target_positions) == 10 and
        all(distance(p1, p2) <= 10 for p1, p2 in zip(positions, last_target_positions))
    )

    if not positions_stable:
        best_target = top_targets[0]
        aim_at_target(best_target)
        
        # Stopper le déplacement si des shapes sont proches (≤ 150 px)
        close_targets = [t for t in farm_targets if distance(t["position"], (center_x, center_y)) < 150]
        if close_targets:
            if current_key_down is not None:
                for key in current_key_down:
                    pyautogui.keyUp(key)
                current_key_down = None

        # Déplacement clavier seulement s'il n'y a aucune cible dans un rayon de 150 px du centre
        else:
            move_towards_target(best_target["position"])


        last_target_positions = positions


    return








