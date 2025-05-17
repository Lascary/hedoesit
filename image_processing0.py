import cv2
import numpy as np


def get_player_position_center(frame):
    height, width, _ = frame.shape
    center_x = width // 2
    center_y = height // 2
    player_position = (center_x, center_y)


    cv2.circle(frame, player_position, 5, (0, 255, 0), -1)
    cv2.putText(frame, "X", (player_position[0] + 10, player_position[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame, player_position



def detect_bullets(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=10,
                               param1=50, param2=20, minRadius=2, maxRadius=10)

    bullet_positions = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            bullet_positions.append((x, y))
            cv2.circle(frame, (x, y), r, (0, 0, 255), 2)
            cv2.putText(frame, "Bullet", (x + 5, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    return frame, bullet_positions



def detect_passive_shapes(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Couleurs en HSV (tu pourras affiner les plages si besoin)
    yellow_lower = np.array([20, 80, 150])
    yellow_upper = np.array([35, 255, 255])

    red_lower1 = np.array([0, 100, 100])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 100, 100])
    red_upper2 = np.array([179, 255, 255])

    blue_lower = np.array([100, 100, 100])
    blue_upper = np.array([130, 255, 255])

    # Masques
    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
    mask_red = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)
    mask_blue = cv2.inRange(hsv, blue_lower, blue_upper)

    result = {
        "yellow_squares": detect_centers(mask_yellow, frame, (0, 255, 255)),
        "red_triangles": detect_centers(mask_red, frame, (0, 0, 255)),
        "blue_pentagons": detect_centers(mask_blue, frame, (255, 0, 0)),
    }

    return frame, result


def detect_centers(mask, frame, color):
# cv2.findContours trouve les contours dans l’image binaire mask.

# cv2.RETR_EXTERNAL : récupère uniquement les contours les plus externes.

# cv2.CHAIN_APPROX_SIMPLE : simplifie les contours pour économiser de la mémoire.

# contours est une liste de contours (chaque contour est un tableau de points).
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []

    for cnt in contours:
        # Calcule les moments géométriques du contour, qui permettent d’en extraire le centre (ou "centre de masse").
        M = cv2.moments(cnt)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centers.append((cx, cy))
            # cv2.circle(frame, (cx, cy), 3, color, -1)
            # Dessiner un cercle bien visible (magenta)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 255), -1)
            # Optionnel : petit point noir au centre
            cv2.circle(frame, (cx, cy), 2, (0, 0, 0), -1)

    return centers







# def detect_player_circle(frame):
# # On convertit l’image (frame) de l’espace BGR (bleu, vert, rouge) à HSV (teinte, saturation, valeur).
# # Pourquoi ? → HSV est plus adapté pour filtrer des couleurs, car la teinte (H) est isolée.
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# # On définit une plage de bleu en HSV.
# # Puis on crée un masque : tous les pixels dans cette plage deviennent blancs (255), le reste noir (0).
#     lower_blue = np.array([90, 50, 50])
#     upper_blue = np.array([130, 255, 255])
#     mask = cv2.inRange(hsv, lower_blue, upper_blue)

# # On applique le masque à l’image : seuls les pixels bleus restent visibles.
# # Le reste devient noir → on garde juste les objets bleus (donc le joueur si c’est encore un cercle bleu).
#     masked = cv2.bitwise_and(frame, frame, mask=mask)


# # Conversion en niveaux de gris (plus facile pour détecter des formes).
# # Puis flou gaussien pour atténuer le bruit (petits pixels parasites) → ça améliore la détection de cercles.
#     gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (9, 9), 2)


# # Utilise l’algorithme de détection de cercles de Hough :
#     # dp=1.2 : résolution de l'accumulation (1.2 = légèrement plus petit que l'image originale)
#     # minDist=30 : distance minimale entre deux cercles détectés
#     # param1=50 : seuil du détecteur de bords Canny (interne à Hough)
#     # param2=30 : seuil de détection réel (plus bas = plus de faux positifs)
#     # minRadius et maxRadius : on cherche des cercles d'une certaine taille
#     circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
#                                param1=50, param2=30, minRadius=10, maxRadius=40)


# # Si au moins un cercle est détecté :

# #     On arrondit les coordonnées

# #     On dessine un cercle vert sur l’image à chaque position (x, y) avec rayon r

# #     Et on écrit le texte "Player" à côté du cercle
#     if circles is not None:
#         circles = np.uint16(np.around(circles))
#         for (x, y, r) in circles[0, :]:
#             cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
#             cv2.putText(frame, "Player", (x - 10, y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#     return frame
