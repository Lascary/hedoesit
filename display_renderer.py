import mss
import numpy as np
import cv2
import pygetwindow as gw
import win32con
import win32gui
import time


def create_display():
    with mss.mss() as sct:
        cv2.namedWindow("Game View", cv2.WINDOW_NORMAL)  # crée la fenêtre une fois
            
        cv2.moveWindow("Game View", 0, 0)  # Positionne la fenêtre en haut à gauche
        #time.sleep(2)


# reçoit une liste des coordonnées et des trucs à dessiner sur capture, le fait, retourne frame
def draw_shapes_on_frame(frame, all_draw_instructions):
    for item in all_draw_instructions:
        for draw_cmd in item["draw"]:
            if draw_cmd[0] == "circle":
                _, center, radius, color, thickness = draw_cmd
                cv2.circle(frame, center, radius, color, thickness)
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
      





