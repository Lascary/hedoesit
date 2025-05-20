import pyautogui
import time

print(pyautogui.size())  # Résolution de l'écran
while True:
    x, y = pyautogui.position()  # Position actuelle de la souris
    print(f"Position actuelle: {x}, {y}")
    time.sleep(3)
        