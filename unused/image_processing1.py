import cv2
import numpy as np

# pointe juste le centre del'écran.., mais suivante devrait faire plus.
# def get_player_position_center(frame):
#     height, width, _ = frame.shape
#     center_x = width // 2
#     center_y = height // 2
#     player_position = (center_x, center_y)


#     cv2.circle(frame, player_position, 5, (0, 255, 0), -1)
#     cv2.putText(frame, "X", (player_position[0] + 10, player_position[1]),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
#     return frame, player_position


def detect_player_with_appendix_and_aim(frame):
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2
    search_radius = 10

    roi = frame[center_y - search_radius:center_y + search_radius,
                center_x - search_radius:center_x + search_radius]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Couleurs du joueur
    color_ranges = [
        ((192, 99, 88), (194, 101, 88)),  # bleu = 193, 100, 88
        # On verra après pour les autres modes de jeu
        # ((50, 100, 50), (80, 255, 255)),    # vert
        # ((0, 150, 50), (10, 255, 255)),     # rouge clair
        # ((160, 150, 50), (179, 255, 255)),  # rouge foncé
        # ((20, 150, 50), (30, 255, 255))     # jaune
    ]

    player_mask = np.zeros(roi.shape[:2], dtype=np.uint8)

    for lower, upper in color_ranges:
        mask = cv2.inRange(hsv_roi, np.array(lower), np.array(upper))
        player_mask = cv2.bitwise_or(player_mask, mask)

    contours, _ = cv2.findContours(player_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    player_position = (center_x, center_y)
    has_appendix = False
    appendix_center = None

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 5:
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"]) + center_x - search_radius
                cy = int(M["m01"] / M["m00"]) + center_y - search_radius
                player_position = (cx, cy)

                # Détection de l'appendice
                appendix_search_radius = 10
                appendix_roi = frame[cy - appendix_search_radius:cy + appendix_search_radius,
                                     cx - appendix_search_radius:cx + appendix_search_radius]
                
                hsv_appendix_roi = cv2.cvtColor(appendix_roi, cv2.COLOR_BGR2HSV)
                lower_gray = np.array([0, 0, 40])
                upper_gray = np.array([180, 50, 200])
                gray_mask = cv2.inRange(hsv_appendix_roi, lower_gray, upper_gray)

                gray_contours, _ = cv2.findContours(gray_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if gray_contours:
                    largest_gray = max(gray_contours, key=cv2.contourArea)
                    if cv2.contourArea(largest_gray) > 3:
                        M2 = cv2.moments(largest_gray)
                        if M2["m00"] != 0:
                            ax = int(M2["m10"] / M2["m00"]) + cx - appendix_search_radius
                            ay = int(M2["m01"] / M2["m00"]) + cy - appendix_search_radius
                            appendix_center = (ax, ay)
                            has_appendix = True

                            # Ligne de mire : direction joueur -> appendice, prolongée
                            dx = ax - cx
                            dy = ay - cy
                            norm = np.sqrt(dx**2 + dy**2)
                            if norm != 0:
                                dx /= norm
                                dy /= norm
                                length = 500  # longueur de la ligne
                                end_x = int(cx + dx * length)
                                end_y = int(cy + dy * length)
                                cv2.line(frame, (cx, cy), (end_x, end_y), (0, 0, 255), 2)

                            # Affichage du centre d'appendice
                            cv2.circle(frame, (ax, ay), 4, (255, 0, 255), -1)

                # Affichage du joueur
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                label = "Player + aim" if has_appendix else "Player"
                cv2.putText(frame, label, (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 0, 255) if has_appendix else (0, 255, 0), 2)

    return frame, player_position, has_appendix, appendix_center



# def detect_bullets(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 1)

#     circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=10,
#                                param1=100, param2=20, minRadius=2, maxRadius=25)

#     bullet_positions = []

#     if circles is not None:
#         circles = np.uint16(np.around(circles))
#         for (x, y, r) in circles[0, :]:
#             bullet_positions.append((x, y))
#             cv2.circle(frame, (x, y), r, (0, 0, 255), 2)
#             cv2.putText(frame, "Bullet", (x + 5, y),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

#     return frame, bullet_positions



def detect_my_bullets(frame):
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2

    # Extraire la couleur moyenne du tank (petite zone autour du centre)
    center_region = frame[center_y - 3:center_y + 3, center_x - 3:center_x + 3]
    tank_color_bgr = np.mean(center_region.reshape(-1, 3), axis=0)

    # Convertir en HSV pour mieux gérer les couleurs (meilleur que BGR)
    tank_color_hsv = cv2.cvtColor(np.uint8([[tank_color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]

    # Détection des cercles (balle potentielle)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=10,
                               param1=50, param2=20, minRadius=2, maxRadius=10)

    my_bullet_positions = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for (x, y, r) in circles[0, :]:
            # Distance du centre
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)

            # Filtrer : trop loin ? → probablement pas ta balle
            if distance > min(width, height) // 2:
                continue

            # Vérifier la couleur du cercle en HSV
            region = hsv_frame[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2]
            if region.size == 0:
                continue
            bullet_color = np.mean(region.reshape(-1, 3), axis=0)

            # Tolérance sur la couleur (H ± 10, S et V ± 40)
            if (abs(bullet_color[0] - tank_color_hsv[0]) <= 10 and
                abs(bullet_color[1] - tank_color_hsv[1]) <= 40 and
                abs(bullet_color[2] - tank_color_hsv[2]) <= 40):

                my_bullet_positions.append((x, y))
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.putText(frame, "My Bullet", (x + 5, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    return frame, my_bullet_positions




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
