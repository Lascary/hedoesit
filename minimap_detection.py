import cv2
import numpy as np





def minimap_detector(capture: np.ndarray, width: int = 102, height: int = 102, offset_x: int = 10, offset_y: int = 7):
    detections = []

    # photo découpee de la minimap en bas à droite
    minimap = crop_bottom_right_area(capture, width=width, height=height, offset_x=offset_x, offset_y=offset_y)

    # Coordonnées du rectangle dans l’image d’origine
    img_height, img_width, _ = capture.shape
    x = img_width - width - offset_x
    y = img_height - height - offset_y
    w, h = width, height
    cx, cy = x + w // 2, y + h // 2

    # Ajout à la liste des détections: carré autour minimap
    detections.append({
        "type": "minimap",
        "position": (cx, cy),
        "draw": [
            ("rect", (x, y), (x + w, y + h), (0, 255, 0), 1)  # rectangle vert
        ]
    })

    return detections  # , minimap si tu veux l'image extraite





# pour n'analyser que le carré où se trouve la minimap // FONCTION A REGLER : REPLACER LE CARRE DE DECOUPE

# image : un tableau NumPy représentant une image (généralement une capture d'écran de mss).
# size : un entier (par défaut 150), représentant la taille du carré à découper.
# Elle renvoie aussi une image, sous forme de tableau NumPy (annotation -> np.ndarray).
# def crop_bottom_right_square_np(capture: np.ndarray, size: int = 150) -> np.ndarray:
    
# # Récupère les dimensions de l’image :
# # height : nombre de lignes (hauteur de l’image en pixels).
# #  width : nombre de colonnes (largeur de l’image en pixels).
# # _ : nombre de canaux de couleur (généralement 4 avec mss : B, G, R, A → ignoré ici).
# # Exemple : si l'image a shape = (720, 640, 4) :
#     height == 720, width == 680

# # Utilise la notation de découpage NumPy (slicing) pour extraire un carré de pixels de size × size depuis le coin bas droit de l’image.

# # Détail :
# # height - size : height → lignes allant de height - 150 jusqu’à height (donc les 150 dernières lignes).
# # width - size : width → colonnes allant de width - 150 jusqu’à width (les 150 dernières colonnes).
# # Résultat : une image de taille 150 × 150 pixels, correspondant au coin inférieur droit de l’image initiale.
#     height, width, _ = capture.shape
#     return capture[height - size : height, width - size : width]

def crop_bottom_right_area(capture: np.ndarray, width: int = 150, height: int = 150, offset_x: int = 0, offset_y: int = 0) -> np.ndarray:
    img_height, img_width, _ = capture.shape
    return capture[
        img_height - height - offset_y : img_height - offset_y,
        img_width - width - offset_x : img_width - offset_x
    ]

