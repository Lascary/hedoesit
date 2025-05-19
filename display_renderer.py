import mss
import numpy as np
import cv2
import pygetwindow as gw
import win32con
import win32gui
import time


# def create_display():
#     with mss.mss() as sct:
#         cv2.namedWindow("Game View", cv2.WINDOW_NORMAL)  # crée la fenêtre une fois
            
#         cv2.moveWindow("Game View", 0, 0)  # Positionne la fenêtre en haut à gauche
#         #time.sleep(2)



def create_display():
    # retour image
    width = 680
    height = 610

    cv2.namedWindow("Game View", cv2.WINDOW_NORMAL)  # crée la fenêtre une fois
    cv2.resizeWindow("Game View", width, height)  # fixe la taille de la fenêtre

    # Affiche une image noire pour forcer la création effective de la fenêtre
    black_img = np.zeros((680, 100, 3), dtype=np.uint8)
    cv2.imshow("Game View", black_img)
    cv2.waitKey(1)  # force l'affichage
    
    # Laisse un petit temps pour que la fenêtre s'initialise
    time.sleep(0.1)
    
    cv2.moveWindow("Game View", -17, 0)  # Positionne la fenêtre en haut à gauche

    # écran de contrôle
    width, height = 680, 45
    cv2.namedWindow("Bot Status", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Bot Status", width, height)
    cv2.moveWindow("Bot Status", -17, 640)  # à adapter à ton écran
    


# reçoit une liste des coordonnées et des trucs à dessiner sur capture, le fait, retourne frame
def draw_shapes_on_frame(frame, all_draw_instructions):
    for item in all_draw_instructions:
        for draw_cmd in item["draw"]:
            if draw_cmd[0] == "circle":
                _, center, radius, color, thickness = draw_cmd
                cv2.circle(frame, center, int(radius), color, thickness)
            elif draw_cmd[0] == "text":
                _, position, text, font, size, color, thickness = draw_cmd
                cv2.putText(frame, text, position, font, size, color, thickness)
            elif draw_cmd[0] == "line":
                _, pt1, pt2, color, thickness = draw_cmd
                cv2.line(frame, pt1, pt2, color, thickness)
            elif draw_cmd[0] == "rect":
                _, pt1, pt2, color, thickness = draw_cmd
                cv2.rectangle(frame, pt1, pt2, color, thickness)
    return frame


def frame_display(frame):
    cv2.imshow("Game View", frame)# affiche dans une fenêtre "game view"


# Crée une base avec les textes statiques
img_base = np.zeros((45, 680, 3), dtype=np.uint8)
cv2.putText(img_base, "FPS:", (10, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 1)

def debug_display(fps):
    img = img_base.copy()  # copie l’image de base
    cv2.putText(img, f"FPS: {fps}", (10, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 1)
    cv2.imshow("Bot Status", img)
    cv2.waitKey(1)





