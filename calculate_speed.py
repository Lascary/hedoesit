import time
import math
import cv2
import numpy as np

class EntityTracker:
    def __init__(self):
        self.prev_entities = {}
        self.prev_frame = None
        self.last_update_time = None

    def update(self, detections, current_frame, current_time, dx_bg=0, dy_bg=0):
        if self.last_update_time is None:
            self.last_update_time = current_time
            self.prev_frame = current_frame
            self.prev_entities = {self._make_id(e): e for e in detections}
            return detections

        dt = current_time - self.last_update_time
        if dt == 0:
            return detections

        updated_entities = {}

        for entity in detections:
            eid = self._make_id(entity)
            x, y = entity["position"]

            best_match_id = None
            min_dist = float("inf")
            for prev_id, prev in self.prev_entities.items():
                if prev["type"] != entity["type"] or prev["color"] != entity["color"]:
                    continue
                px, py = prev["position"]
                dist = math.hypot(x - px - dx_bg, y - py - dy_bg)
                if dist < min_dist and dist < 50:
                    min_dist = dist
                    best_match_id = prev_id

            if best_match_id:
                px, py = self.prev_entities[best_match_id]["position"]
                vx = (x - px - dx_bg) / dt
                vy = (y - py - dy_bg) / dt
                speed = math.hypot(vx, vy)


                entity["speed_x"] = vx
                entity["speed_y"] = vy
                entity["speed"] = speed
    

                entity.setdefault("draw", []).append(
                    ("line", (int(px), int(py)), (int(x), int(y)), (0, 255, 255), 2)
                )
                label = f"{int(speed)} px/s"
                color = (0, 140, 255) if entity["type"].startswith("ennemy") else (0, 0, 255)
                entity["draw"].append(
                    ("text", (int(x + 5), int(y - 5)), label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                )

            updated_entities[eid] = entity

        self.prev_frame = current_frame
        self.prev_entities = updated_entities
        self.last_update_time = current_time

        return list(updated_entities.values())

    def _make_id(self, item):
        return f"{item['type']}_{item['color']}"




def calculate_things_speed(all_draw_instructions, entity_tracker, current_frame=None, current_time=None):
    """
    Met à jour all_draw_instructions en ajoutant les vitesses calculées des entités,
    en tenant compte de la vitesse du fond (background_speed).

    :param all_draw_instructions: liste de détections (dict)
    :param entity_tracker: 
    :param current_frame: image actuelle en BGR (optionnel, nécessaire pour tracker)
    :param current_time: timestamp actuel (optionnel, si None, prend time.time())
    :return: all_draw_instructions mise à jour avec "speed" pour ennemis, etc.
    """
    if current_time is None:
        current_time = time.time()

    # Extraire background_speed de all_draw_instructions
    background_speed = (0, 0)
    for item in all_draw_instructions:
        if item.get("type") == "background_speed":
            background_speed = (item.get("speed_dx", 0), item.get("speed_dy", 0))
            break

    dx_bg, dy_bg = background_speed

    # Filtrer uniquement tanks et bullets à tracker
    object_to_avoid = {"ennemy_bullet"}
    tank_to_fight = {"ennemy_player"}
    to_track = [item for item in all_draw_instructions if item.get("type") in object_to_avoid.union(tank_to_fight)]



    # Mettre à jour le tracking avec frame et temps actuels
    tracked_items = entity_tracker.update(to_track, current_frame, current_time, dx_bg, dy_bg)

    # Remplacer les entités d'origine par celles enrichies
    for i, item in enumerate(all_draw_instructions):
        if item.get("type") in object_to_avoid.union(tank_to_fight):
            # Trouver l'entité trackée correspondante (par id)
            eid = entity_tracker._make_id(item)
            for tracked_item in tracked_items:
                if entity_tracker._make_id(tracked_item) == eid:
                    all_draw_instructions[i] = tracked_item
                    break

    return all_draw_instructions


# Fonction estimate_background_speed améliorée (retourne dx, dy pour être plus précis)




import cv2
import numpy as np
import math

def estimate_background_speed(prev_hsv, curr_hsv):
    if prev_hsv is None or curr_hsv is None:
        return [{
            "type": "background_speed",
            "speed": 0,
            "speed_dx": 0,
            "speed_dy": 0,
            "draw": []
        }]

    lower_gray = np.array([0, 0, 193])
    upper_gray = np.array([0, 0, 203])

    prev_mask = cv2.inRange(prev_hsv, lower_gray, upper_gray)
    curr_mask = cv2.inRange(curr_hsv, lower_gray, upper_gray)

    # Utilise les canaux HSV filtrés comme des images 1 canal (améliore matchTemplate)
    h, w = prev_mask.shape
    win_size = 200
    margin = 50
    cx, cy = w // 2, h // 2

    x0 = cx - win_size // 2
    y0 = cy - win_size // 2

    x1 = max(0, x0 - margin)
    y1 = max(0, y0 - margin)
    x2 = min(w, x0 + win_size + margin)
    y2 = min(h, y0 + win_size + margin)

    template = prev_mask[y0:y0+win_size, x0:x0+win_size]
    search_area = curr_mask[y1:y2, x1:x2]

    if search_area.shape[0] < win_size or search_area.shape[1] < win_size:
        return [{
            "type": "background_speed",
            "speed": 0,
            "speed_dx": 0,
            "speed_dy": 0,
            "draw": []
        }]

    result = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)

    dx = max_loc[0] - (x0 - x1)
    dy = max_loc[1] - (y0 - y1)
    speed = math.hypot(dx, dy)

    draw = [
        ("rectangle", (x0, y0, x0 + win_size, y0 + win_size), (0, 255, 0), 1),
        ("rectangle", (x1, y1, x2, y2), (0, 255, 255), 1),
        ("line", (cx, cy), (cx + dx, cy + dy), (255, 0, 0), 2),
        ("text", (cx + dx + 5, cy + dy + 5), f"BG speed: {speed:.2f} px", cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    ]

    return [{
        "type": "background_speed",
        "speed": speed,
        "speed_dx": dx,
        "speed_dy": dy,
        "draw": draw
    }]



