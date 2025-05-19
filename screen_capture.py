import mss
import numpy as np
import pygetwindow as gw
import time


# Trouve la fenêtre Firefox
def get_firefox_window():
    windows = gw.getWindowsWithTitle("diep.io — Mozilla Firefox")
    diep_window = windows[0] if windows else None
    
    return diep_window

# Met la fenêtre diep au premier plan
def focus_and_maximize_window(diep_window):
    # win32gui.ShowWindow(diep_window._hWnd, win32con.SW_RESTORE)  # Si minimisée
    # win32gui.SetForegroundWindow(diep_window._hWnd)              # La met devant
    # win32gui.ShowWindow(diep_window._hWnd, win32con.SW_MAXIMIZE)  # La met en FULL SCREEN
    time.sleep(0.1)  # Laisse le temps de se rafraîchir

# 
def screen_init():
    diep_window = get_firefox_window()
    if not diep_window:
        raise RuntimeError("Fenêtre Firefox 'diep.io' introuvable.")
    else:
        diep_window.activate()
    # focus_and_maximize_window() // pas utiles pour le moment, je mets moi-même la fenêtre du jeu au bon endroit
    # Affiche position et taille pour debug
    # print(f"Fenêtre Firefox: Left={diep_window.left}, Top={diep_window.top}, Width={diep_window.width}, Height={diep_window.height}")

# capture du jeu
def game_screener():
    capture_area = {
            # Version diep 1/2 droite
            "top": 114, # enlevé en haut
            "left": 685,  # enlevé à gauche
            "width": 680,
            "height": 610 # hauteur, enlève des px en bas
             
            # VERSION full screen:
            # "top": 114, # enlevé en haut
            # "left": 1,  # enlevé à gauche
            # "width": 1363, # 1366 -3 enlevés à droite
            # "height": 615 # hauteur, enlève des px en bas
    }
    # capture l'écran, 
    # convertit l'img en tableau NumPy, pour la traiter avec  OpenCv
    with mss.mss() as sct:          
        capture = np.array(sct.grab(capture_area))

    return capture