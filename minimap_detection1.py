import cv2
import numpy as np

# zone de mon écran qui est capturée
# "top": 114, # enlevé en haut
# "left": 685,  # enlevé à gauche
# "width": 680,
# "height": 610 # hauteur, enlève des px en bas




CAPTURE_TOP = 114
CAPTURE_LEFT = 685

# version gpt
def annotate_minimap(image: np.ndarray) -> np.ndarray:
    output = image.copy()

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 1. Détection des zones noires (minimap)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 40])
    mask_black = cv2.inRange(hsv, lower_black, upper_black)

    contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    minimap_box = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / h
        if 0.9 < aspect_ratio < 1.1 and 30 < w < 200:
            minimap_box = (x, y, w, h)
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)  # vert fluo
            break

    if not minimap_box:
        return output  # mini-map non trouvée

    # 2. Chercher les 4 carrés colorés dans les coins
    x, y, w, h = minimap_box
    minimap = image[y:y+h, x:x+w]
    minimap_hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)

    corner_coords = {
        "top_left": (2, 2),
        "top_right": (w - 12, 2),
        "bottom_left": (2, h - 12),
        "bottom_right": (w - 12, h - 12),
    }

    for name, (cx, cy) in corner_coords.items():
        region = minimap[cy:cy+10, cx:cx+10]
        avg_color = np.mean(region.reshape(-1, 3), axis=0)
        # Dessiner contour de chaque coin (sur l'image de sortie globale)
        cv2.rectangle(output, (x+cx, y+cy), (x+cx+10, y+cy+10), (0, 255, 0), 1)

    # 3. Détection du joueur (pixel noir unique au centre ?)
    player_mask = cv2.inRange(minimap_hsv, lower_black, upper_black)
    player_pixels = cv2.findNonZero(player_mask)

    if player_pixels is not None:
        # Trouver le pixel noir le plus proche du centre de la mini-carte
        center = np.array([w // 2, h // 2])
        closest = min(player_pixels, key=lambda pt: np.linalg.norm(pt[0] - center))

        px, py = closest[0]
        cv2.drawMarker(output, (x + px, y + py), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)

    return output




# pour n'analyser que le carré où se trouve la minimap // FONCTION A REGLER : REPLACER LE CARRE DE DECOUPE

# image : un tableau NumPy représentant une image (généralement une capture d'écran de mss).
# size : un entier (par défaut 150), représentant la taille du carré à découper.
# Elle renvoie aussi une image, sous forme de tableau NumPy (annotation -> np.ndarray).
def crop_bottom_right_square_np(capture: np.ndarray, size: int = 150) -> np.ndarray:
    
# Récupère les dimensions de l’image :
# height : nombre de lignes (hauteur de l’image en pixels).
#  width : nombre de colonnes (largeur de l’image en pixels).
# _ : nombre de canaux de couleur (généralement 4 avec mss : B, G, R, A → ignoré ici).
# Exemple : si l'image a shape = (720, 640, 4) :
    height = 720, width = 640

# Utilise la notation de découpage NumPy (slicing) pour extraire un carré de pixels de size × size depuis le coin bas droit de l’image.

# Détail :
# height - size : height → lignes allant de height - 150 jusqu’à height (donc les 150 dernières lignes).
# width - size : width → colonnes allant de width - 150 jusqu’à width (les 150 dernières colonnes).
# Résultat : une image de taille 150 × 150 pixels, correspondant au coin inférieur droit de l’image initiale.
    height, width, _ = capture.shape
    return capture[height - size : height, width - size : width]




# copie de polygones detector
def minimap_detector(capture):

    hsv = cv2.cvtColor(capture, cv2.COLOR_BGR2HSV)

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
            # suite ok ?
            crop_bottom_right_square_np(capture: np.ndarray, size: int = 150)
            x, y, w, h = minimap_box
            cx, cy = x + w // 2, y + h // 2  # centre du rectangle
            detections.append({
                "type": "minimap",
                "position": (cx, cy),
                "draw": [
                    ("rect", (x, y), (x + w, y + h), (0, 255, 0), 2),  # rectangle vert
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