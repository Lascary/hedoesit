import cv2
import numpy as np

# === Paramètres ===
GRAY_THRESHOLD = 0.001 # 0.1 = 10% de gris minimum dans l'anneau pour détecter un joueur

    # === Définir les plages de couleurs ennemies ===
COLOR_RANGES = [
    (np.array([94, 230, 202]), np.array([99, 255, 252]), "blue"),
    # (np.array([0, 150, 100]), np.array([10, 255, 255]), "red"),
    (np.array([175, 160, 220]), np.array([179, 185, 255]), "red"),
    (np.array([134, 102, 222]), np.array([139, 152, 255]), "purple"),
    (np.array([71, 230, 202]), np.array([76, 255, 252]), "green"),
]

def create_color_masks(hsv):
    enemy_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    mask_color_map = {}
    for lower, upper, color in COLOR_RANGES:
        mask = cv2.inRange(hsv, lower, upper)
        enemy_mask |= mask
        mask_color_map[color] = mask_color_map.get(color, 0) + mask
    return enemy_mask, mask_color_map

    # === Masque gris (canon) ===
def detect_contours(hsv, enemy_mask):
    lower_gray = np.array([0, 0, 152])
    upper_gray = np.array([180, 20, 154])
    gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)

    # détection des formes colorées ennemies
    contours, _ = cv2.findContours(enemy_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours, gray_mask

def classify_candidates(hsv, contours, gray_mask, mask_color_map):
    candidates = []
    h, w = hsv.shape[:2]
    center = (w // 2, h // 2)

    # Pour chaque cercle parmi ces cercles
    for cnt in contours:
        
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        x, y, radius = int(x), int(y), int(radius)
        # si le cercle fait entre 3 et 40px de rayon
        if not 3 < radius < 40:
            continue

        # === Créer un masque circulaire en anneau ===
        mask_shape = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.circle(mask_shape, (x, y), radius + 6, 255, -1)
        cv2.circle(mask_shape, (x, y), radius + 2, 0, -1)

        # Intersection avec les zones grises: px =255 si gris, sinon px=0
        gray_in_ring = cv2.bitwise_and(gray_mask, mask_shape)
        # Calcul du ratio de gris dans l'anneau
        num_gray_pixels = cv2.countNonZero(gray_in_ring)
        num_ring_pixels = cv2.countNonZero(mask_shape)
        gray_ratio = num_gray_pixels / num_ring_pixels if num_ring_pixels > 0 else 0

        is_player = gray_ratio > GRAY_THRESHOLD
        color_detected = detect_color(mask_color_map, x, y)

        candidates.append({
            "raw_type": "player" if is_player else "bullet",
            "position": (x, y),
            "radius": radius,
            "gray_ratio": gray_ratio,
            "color": color_detected,
            "distance_to_center": np.hypot(x - center[0], y - center[1])
        })

    return candidates

def detect_color(mask_color_map, x, y):
    for color_name, color_mask in mask_color_map.items():
        if color_mask[y, x] > 0:
            return color_name
    return None

def annotate_detections(candidates, self_color, self_player):
    detections = []
    color_map = {
        "red": (0, 0, 255),
        "blue": (255, 0, 0),
        "green": (0, 255, 0),
        "purple": (255, 0, 255)
    }

    for c in candidates:
        x, y = c["position"]
        radius = c["radius"]
        gray_ratio = c["gray_ratio"]
        raw_type = c["raw_type"]
        color = c["color"]

        if c is self_player:
            label = "self"
        elif color == self_color:
            label = f"ally_{raw_type}"
        else:
            label = f"ennemy_{raw_type}"

        if c is self_player:
            rect_color = (255, 255, 0)  # Cyan fluo
        elif color == self_color:
            rect_color = (0, 255, 0)    # Vert fluo
        else:
            rect_color = (255, 0, 255)  # Rouge magenta fluo

        draw_list = [
            # ("circle", (x, y), radius + 2, (0, 255, 255), 1),
            # ("circle", (x, y), radius + 6, (0, 128, 255), 1),
            ("text", (x - 20, y - radius - 10), label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1),
            ("text", (x - 20, y + radius + 15), f"{gray_ratio*100:.2f}%", cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1),
            ("rect", (x - radius - 4, y - radius - 4), (x + radius + 4, y + radius + 4), rect_color, 1)
        ]

        detections.append({
            "type": label,
            "position": (x, y),
            "color": color,
            "draw": draw_list
        })

    return detections

def detect_players_bullets_and_self(hsv, known_self_color=None):
    # Création des masques couleur
    enemy_mask, mask_color_map = create_color_masks(hsv)

    # Détection des contours ennemis + masque gris
    contours, gray_mask = detect_contours(hsv, enemy_mask)

    # Classification des candidats (joueurs ou balles)
    candidates = classify_candidates(hsv, contours, gray_mask, mask_color_map)

    # Identification du joueur "self"
    if known_self_color is None:
        self_player = min(
            (c for c in candidates if c["raw_type"] == "player"),
            key=lambda c: c["distance_to_center"],
            default=None
        )
        self_color = self_player["color"] if self_player else None
    else:
        self_player = min(
            (c for c in candidates if c["raw_type"] == "player" and c["color"] == known_self_color),
            key=lambda c: c["distance_to_center"],
            default=None
        )
        self_color = known_self_color

    # Annotation des détections avec les infos nécessaires au dessin
    detections = annotate_detections(candidates, self_color, self_player)

    # On retourne *directement* la liste de détections (pour dessiner), et la couleur si besoin
    return detections, self_color


