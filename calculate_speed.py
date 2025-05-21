import time
import math
import cv2
import numpy as np
from copy import deepcopy

class EntityTracker:
    def __init__(self, max_match_dist=150):
        self.prev_entities = []
        self.prev_frame = None
        self.last_update_time = None
        self.max_match_dist = max_match_dist

    def update(self, detections, current_frame, current_time, dx_bg=0, dy_bg=0):
        # Deepcopy pour éviter effet de bord sur input
        detections = deepcopy(detections)

        if self.last_update_time is None:
            self.last_update_time = current_time
            self.prev_frame = current_frame
            self.prev_entities = detections
            # Initialisation vitesses à 0
            for ent in detections:
                ent["speed_x"] = 0.0
                ent["speed_y"] = 0.0
                ent["speed"] = 0.0
            return detections

        dt = current_time - self.last_update_time
        if dt <= 0:
            # Temps non valide ou identique => pas de mise à jour de vitesse
            return detections

        updated_entities = []
        used_prev = set()

        for entity in detections:
            x, y = entity["position"]
            best_match = None
            min_dist = float("inf")
            best_index = -1

            for i, prev in enumerate(self.prev_entities):
                if i in used_prev:
                    continue
                if prev["type"] != entity["type"] or prev["color"] != entity["color"]:
                    continue

                px, py = prev["position"]
                # Distance compensée du déplacement du fond
                dist = math.hypot((x - px) - dx_bg, (y - py) - dy_bg)
                if dist < min_dist and dist < self.max_match_dist:
                    min_dist = dist
                    best_match = prev
                    best_index = i

            if best_match:
                used_prev.add(best_index)
                px, py = best_match["position"]
                vx = ((x - px) - dx_bg) / dt
                vy = ((y - py) - dy_bg) / dt
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
            else:
                # Nouvelle entité : vitesse nulle par défaut
                entity["speed_x"] = 0.0
                entity["speed_y"] = 0.0
                entity["speed"] = 0.0
                entity["new"] = True

            updated_entities.append(entity)

        # Mise à jour des états
        self.prev_frame = current_frame
        self.prev_entities = updated_entities
        self.last_update_time = current_time

        return updated_entities


def calculate_things_speed(all_draw_instructions, entity_tracker, current_frame=None, current_time=None):
    """
    Met à jour all_draw_instructions en calculant les vitesses des entités en tenant compte de la vitesse du fond.
    """

    if current_time is None:
        current_time = time.time()

    # Récupération de la vitesse du fond
    background_speed = (0, 0)
    for item in all_draw_instructions:
        if "type"== "background_speed":
            background_speed = (item.get("speed_dx", 0), item.get("speed_dy", 0))
            break

    dx_bg, dy_bg = background_speed

    # Types à suivre
    object_to_avoid = {"ennemy_bullet"}
    tank_to_fight = {"ennemy_player"}
    types_to_track = object_to_avoid.union(tank_to_fight)

    # Extraction des entités à tracker
    tracked_input = [item for item in all_draw_instructions if "type" in types_to_track]

    # Mise à jour du tracker
    tracked_output = entity_tracker.update(tracked_input, current_frame, current_time, dx_bg, dy_bg)

    # Reconstruction de la liste avec mise à jour des entités suivies
    updated_draw = []
    for item in all_draw_instructions:
        if "type" in types_to_track:
            # Trouver correspondance la plus proche dans tracked_output
            best_match = None
            min_dist = float("inf")
            for tracked_item in tracked_output:
                if tracked_item.get("type") == item.get("type") and tracked_item.get("color") == item.get("color"):
                    x1, y1 = item.get("position", (None, None))
                    x2, y2 = tracked_item.get("position", (None, None))
                    if x1 is not None and x2 is not None:
                        dist = math.hypot(x2 - x1, y2 - y1)
                        if dist < 5 and dist < min_dist:
                            best_match = tracked_item
                            min_dist = dist
            updated_draw.append(best_match if best_match else item)
        else:
            updated_draw.append(item)

    # Mise à jour spécifique pour "self" (joueur)
    for idx, item in enumerate(updated_draw):
        if "type" == "self":
            x, y = item.get("position", (0, 0))
            prev_self = next((e for e in entity_tracker.prev_entities if e.get("type") == "self"), None)
            # Attention : ici dt = current_time - prev_last_update_time avant la mise à jour
            dt = current_time - (entity_tracker.last_update_time if entity_tracker.last_update_time else current_time)
            if prev_self and dt > 0:
                x_prev, y_prev = prev_self.get("position", (0, 0))
                vx = (x - x_prev - dx_bg) / dt
                vy = (y - y_prev - dy_bg) / dt
            else:
                vx, vy = dx_bg, dy_bg

            speed = math.hypot(vx, vy)
            item["speed_x"] = vx
            item["speed_y"] = vy
            item["speed"] = speed

            item.setdefault("draw", []).append(
                ("line", (int(x - vx), int(y - vy)), (int(x), int(y)), (255, 255, 0), 2)
            )
            item["draw"].append(
                ("text", (int(x + 5), int(y - 5)), f"{int(speed)} px/s", cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            )
            updated_draw[idx] = item
            break

    return updated_draw


def estimate_background_speed(all_draw_instructions, prev_hsv, curr_hsv, smoothing_window=5, speed_history=None):
    """
    Calcule la vitesse de déplacement du fond entre deux images HSV,
    retourne la vitesse en pixels par frame et ses composantes dx, dy.
    Applique un lissage si speed_history est fourni.
    """

    if prev_hsv is None or curr_hsv is None:
        return [{
            "type": "background_speed",
            "speed": 0,
            "speed_dx": 0,
            "speed_dy": 0,
            "draw": []
        }], speed_history

    lower_gray = np.array([0, 0, 193])
    upper_gray = np.array([180, 30, 203])  # élargir la plage HSV pour inclure plus de gris

    prev_mask = cv2.inRange(prev_hsv, lower_gray, upper_gray)
    curr_mask = cv2.inRange(curr_hsv, lower_gray, upper_gray)

    h, w = prev_mask.shape
    win_size = 300
    margin = 200
    cx, cy = w // 2, h // 2

    x0 = cx - win_size // 2
    y0 = cy - win_size // 2

    x1 = max(0, x0 - margin)
    y1 = max(0, y0 - margin)
    x2 = min(w, x0 + win_size + margin)
    y2 = min(h, y0 + win_size + margin)

    if (y0 + win_size > h) or (x0 + win_size > w) or (y1 > h) or (x1 > w):
        # Fenêtre hors limite : retour vitesse nulle
        return [{
            "type": "background_speed",
            "speed": 0,
            "speed_dx": 0,
            "speed_dy": 0,
            "draw": []
        }], speed_history

    template = prev_mask[y0:y0+win_size, x0:x0+win_size]
    search_area = curr_mask[y1:y2, x1:x2]

    if search_area.shape[0] < win_size or search_area.shape[1] < win_size:
        return [{
            "type": "background_speed",
            "speed": 0,
            "speed_dx": 0,
            "speed_dy": 0,
            "draw": []
        }], speed_history

    result = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < 0.8:
        speed = 0
        dx = 0
        dy = 0
    else:
        dx = (max_loc[0] - (x0 - x1))
        dy = (max_loc[1] - (y0 - y1))
        speed = math.hypot(dx, dy)

    # On inverse dx/dy car on cherche le mouvement du fond relatif à la caméra
    dx, dy = -dx, -dy

    # Lissage sur l'historique
    if speed_history is None:
        speed_history = []
    speed_history.append((dx, dy))
    if len(speed_history) > smoothing_window:
        speed_history.pop(0)

    avg_dx = sum([v[0] for v in speed_history]) / len(speed_history)
    avg_dy = sum([v[1] for v in speed_history]) / len(speed_history)
    avg_speed = math.hypot(avg_dx, avg_dy)

    return {
        "type": "background_speed",
        "speed": avg_speed,
        "speed_dx": avg_dx,
        "speed_dy": avg_dy,
        "draw": [
            ("rectangle", (x0, y0, x0 + win_size, y0 + win_size), (0, 255, 0), 1),
            ("rectangle", (x1, y1, x2, y2), (0, 255, 255), 1),
            ("line", (cx, cy), (cx - int(avg_dx), cy - int(avg_dy)), (255, 0, 0), 2),
            ("text", (cx + int(avg_dx) + 5, cy + int(avg_dy) + 5), f"BG speed: {avg_speed:.2f} px", cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        ]
    }
