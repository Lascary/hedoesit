import cv2
import numpy as np

def detect_enemy_players_and_bullets(hsv):
    detections = []

    # === Définir les 3 plages de couleurs ennemies ===
    color_ranges = [
        (np.array([94, 230, 202]), np.array([99, 255, 252])), # Bleu
        (np.array([0, 150, 100]), np.array([10, 255, 255])),    # Rouge (partie basse)
        (np.array([170, 100, 100]), np.array([180, 255, 255])), # Rouge (partie haute)
        (np.array([134, 102, 222]), np.array([139, 152, 255])), # Violet
        (np.array([71, 230, 202]), np.array([76, 255, 252])), # Vert
    ]

    # === Combiner les masques couleurs ennemies ===
    enemy_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in color_ranges:
        enemy_mask |= cv2.inRange(hsv, lower, upper)

    # === Détection du gris (canon) ===
    lower_gray = np.array([0, 0, 128])
    upper_gray = np.array([180, 38, 179])
    gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)

    # Trouver les contours des ennemis (colorés)
    contours, _ = cv2.findContours(enemy_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    # Pour chaque contour :
    # Obtenir la position de l'objet coloré,
    # Vérifier s’il y a du gris autour (rayon court, genre 20px) = un canon, donc un joueur
    # calcule le plus petit cercle possible qui entoure complètement le contour cnt.
    for cnt in contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        x, y, radius = int(x), int(y), int(radius)

        # On ignore les objets trop petits (radius ≤ 3) → probablement du bruit.
        # On ignore les objets trop gros (radius ≥ 30) → probablement pas des balles/joueurs ennemis.
        if 3 < radius < 40: # tu peux ajuster
            # zone carrée 100×100 px autour du centre de l'objet.
            gray_zone = gray_mask[y - 50:y + 50, x - 50:x + 50]
            if gray_zone.size == 0:
                continue

            gray_ratio = np.mean(gray_zone > 0)

            # augmenter artificiellement la taille du carré imprimé
            padding = 3
            top_left = (x - radius - padding, y - radius - padding)
            bottom_right = (x + radius + padding, y + radius + padding)

            if gray_ratio > 0.1:
                # Joueur ennemi → carré rouge
                detections.append({
                    "type": "ennemy_player",
                    "position": (x, y),
                    "draw": [("rect", top_left, bottom_right, (0, 0, 255), 1)]
                })
            else:
                # Balle ennemie → carré vert
                detections.append({
                    "type": "ennemy_bullet",
                    "position": (x, y),
                    "draw": [("rect", top_left, bottom_right, (0, 255, 0), 1)]
                })

    return detections
