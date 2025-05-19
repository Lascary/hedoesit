from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
import math

keyboard = KeyboardController()
mouse = MouseController()

# État interne pour éviter de refaire les mêmes actions
state = {
    "active": False,
    "mouse_set": False
}

def simpler_farm(farm_targets, auto_fire_on):
    if farm_targets:
        # Active la marche avant si pas déjà fait
        if not state["active"]:
            keyboard.press('z')
            state["active"] = True

        # Active l'auto-fire si pas déjà activé
        if not auto_fire_on:
            keyboard.press('e')
            keyboard.release('e')
            auto_fire_on = True

        # Positionne la souris une fois à 45°
        if not state["mouse_set"]:
            angle_deg = 45
            distance = 100
            angle_rad = math.radians(angle_deg)
            dx = int(distance * math.cos(angle_rad))
            dy = int(-distance * math.sin(angle_rad))
            x, y = mouse.position
            mouse.position = (x + dx, y - dy)
            state["mouse_set"] = True

    else:
        # Si plus rien à farmer, on relâche les touches
        if state["active"]:
            keyboard.release('z')
            state["active"] = False
            state["mouse_set"] = False  # Repositionne la souris à la prochaine activation

    return auto_fire_on
