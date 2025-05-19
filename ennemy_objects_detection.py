import cv2
import numpy as np

def detect_enemy_players_and_bullets(hsv):
    detections = []

    # === Paramètres ===
    GRAY_THRESHOLD = 0.00001  # 0.1 = 10% de gris minimum dans l'anneau pour détecter un joueur


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
    lower_gray = np.array([0, 0, 152])
    upper_gray = np.array([180, 20, 154])
    gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)

    # détection des formes colorées ennemies
    contours, _ = cv2.findContours(enemy_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # cv2.imshow("Gray Mask", gray_mask)
    # Pour chaque cercle dans ces cercles
    for cnt in contours:
        # Circonscription de l'objet de couleur ennemie dans un cercle (centre: x,y; rayon: radius)
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        x, y, radius = int(x), int(y), int(radius)


        # si le cercle fait entre 3 et 40px de rayon
        if 3 < radius < 40:
            # === Créer un masque circulaire en anneau ===
            mask_shape = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.circle(mask_shape, (x, y), radius + 6, 255, -1)  # r + 10 = Grand cercle 
            cv2.circle(mask_shape, (x, y), radius + 2, 0, -1)         # Retire intérieur


            # Intersection avec les zones grises: px =255 si gris, sinon px=0
            gray_in_ring = cv2.bitwise_and(gray_mask, gray_mask, mask=mask_shape)

            # Calcul du ratio de gris dans l'anneau
            gray_ratio = np.mean(gray_in_ring > 0)

            # === Dessins ===
            padding = 2 # côté carré plus grand de 3px
            top_left = (x - radius - padding, y - radius - padding)
            bottom_right = (x + radius + padding, y + radius + padding)

            is_player = gray_ratio > GRAY_THRESHOLD

            draw_list = [
                # rectangle P=ROUGE/ B=VERT autour de l'ennemi
                ("rect", top_left, bottom_right, (0, 0, 255) if is_player else (0, 255, 0), 1),
                
                # debug Cercle VIOLET rayon max
                ("circle", (x, y), 40, (255, 0, 255), 1),

                 # debug Anneau de détection du gris
                ("circle", (x, y), radius + 2, (0, 255, 255), 1), # Cercle JAUNE intérieur (limite forme)
                ("circle", (x, y), radius + 6, (0, 128, 255), 1), # Cercle ORANGE extérieur (limite gris)

                # Texte pour le type
                ("text", (x - 20, y - radius - 10),
                 "player" if is_player else "bullet",
                 cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                 (0, 0, 255) if is_player else (0, 255, 0), 1),
                
                # debug Texte pour le ratio
                ("text", (x - 20, y + radius + 15),
                f"{gray_ratio*100:.3f}%", cv2.FONT_HERSHEY_SIMPLEX,
                0.4, (255, 255, 255), 1)
            ]

            detections.append({
                "type": "ennemy_player" if is_player else "ennemy_bullet",
                "position": (x, y),
                "draw": draw_list
            })

    return detections
