import cv2
import numpy as np
import mss
import time

# Initialisation de la capture d'écran
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Écran principal (modifier si nécessaire)

    screen_width = monitor["width"]
    screen_height = monitor["height"]
    half_screen = {
        "top": monitor["top"],
        "left": monitor["left"] + screen_width // 2,
        "width": screen_width // 2,
        "height": screen_height
    }

    while True:
        # Capture de la moitié droite
        screenshot = np.array(sct.grab(half_screen))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # Conversion en HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Masque 
        lower_gray = np.array([0,0,193])
        upper_gray = np.array([0,0,203])
        gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)

        # Affichage
        cv2.imshow("Masque", gray_mask)
        # cv2.imshow("Image source", frame)

        # Déplacer les fenêtres
        cv2.moveWindow("Masque", 0, 0)                     # à gauche
        # cv2.moveWindow("Image source", screen_width // 2, 0)

        # Ajuster leur taille
        cv2.resizeWindow("Masque", screen_width // 2, screen_height)
        # cv2.resizeWindow("Image source", screen_width // 2, screen_height) 

        # Quitter avec k
        if cv2.waitKey(1) & 0xFF == ord('k'):
            break

    cv2.destroyAllWindows()
