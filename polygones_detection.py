import cv2
import numpy as np

def passive_polygons_detector(hsv):


    masks = {
        "yellow_square": create_color_mask(hsv, 25, 150, 255),
        "red_triangle":  create_red_mask(hsv),
        "blue_pentagon": create_color_mask(hsv, 115, 135, 252),
    }

    detections = []

    for shape_name, mask in masks.items():
        color_bgr = {
            "yellow_square": (0, 255, 255),
            "red_triangle": (0, 0, 255),
            "blue_pentagon": (255, 0, 0),
        }[shape_name]

        centers = detect_centers(mask)
        for cx, cy in centers:
            detections.append({
                "type": shape_name,
                "position": (cx, cy),
                "draw": [
                    ("rect", (cx, cy), 5, (0, 0, 0), 1)
                    # ("circle", (cx, cy), 5, (255, 0, 255), 1),  # magenta cercle
                    ("circle", (cx, cy), 1, (0, 0, 0), -1),     # petit point noir
                ]
            })

    return detections

def create_color_mask(hsv, h, s, v):
    lower = np.array([h - 1, s - 1, v - 1])
    upper = np.array([h + 1, s + 1, v + 1])
    return cv2.inRange(hsv, lower, upper)

def create_red_mask(hsv):
    s, v = 135, 252
    lower1 = np.array([0, s - 1, v - 1])
    upper1 = np.array([1, s + 1, v + 1])
    lower2 = np.array([178, s - 1, v - 1])
    upper2 = np.array([179, s + 1, v + 1])
    return cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)


# Utile pour marquer le centre des passive forms.
def detect_centers(mask):
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

    return centers