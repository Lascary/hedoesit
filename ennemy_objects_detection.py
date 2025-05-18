import cv2
import numpy as np

def detect_enemy_players_and_bullets(hsv):
    detections = []

    # === Définir les plages de couleurs ennemies ===
    color_ranges = [
        (np.array([94, 230, 202]), np.array([99, 255, 252])),  # Bleu
        (np.array([0, 150, 100]), np.array([10, 255, 255])),   # Rouge bas
        (np.array([170, 100, 100]), np.array([180, 255, 255])),# Rouge haut
        (np.array([134, 102, 222]), np.array([139, 152, 255])),# Violet
        (np.array([71, 230, 202]), np.array([76, 255, 252])),  # Vert
    ]

    # === Masques de couleur ===
    enemy_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in color_ranges:
        enemy_mask |= cv2.inRange(hsv, lower, upper)

    # === Masque gris (canon) ===
    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 20, 70])
    gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)

    contours, _ = cv2.findContours(enemy_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        x, y, radius = int(x), int(y), int(radius)

        if 3 < radius < 40:
            # Sécurise les bornes pour éviter erreurs d'index
            h, w = hsv.shape[:2]
            x1, x2 = max(0, x - 50), min(w, x + 50)
            y1, y2 = max(0, y - 50), min(h, y + 50)

            # Calcule la moyenne HSV dans la zone
            gray_zone = gray_mask[y1:y2, x1:x2]
            if gray_zone.size == 0:
                continue

            gray_ratio = np.mean(gray_zone > 0.1)# 0.1 = 10%
            padding = 3
            top_left = (x - radius - padding, y - radius - padding)
            bottom_right = (x + radius + padding, y + radius + padding)

            draw_list = [
                ("rect", top_left, bottom_right, (0, 0, 255) if gray_ratio > 0.1 else (0, 255, 0), 1),
                ("circle", (x, y), 40, (255, 0, 255), 1),  # Cercle debug rayon max
                ("rect", (x - 50, y - 50), (x + 50, y + 50), (0, 255, 255), 1),  # Zone gris
                ("text", (x - 20, y - radius - 10),
                 "player" if gray_ratio > 0.1 else "bullet",
                 cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                 (0, 0, 255) if gray_ratio > 0.1 else (0, 255, 0), 1),
                 ("text", (x - 20, y + radius + 15),
                f"{gray_ratio*100:.1f}%", cv2.FONT_HERSHEY_SIMPLEX,
                0.4, (255, 255, 255), 1)
            ]

            detections.append({
                "type": "ennemy_player" if gray_ratio > 0.1 else "ennemy_bullet",
                "position": (x, y),
                "draw": draw_list
            })

    return detections
