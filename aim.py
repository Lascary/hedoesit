import math
import pyautogui
import time
import random


# vitesses en pixels par frame
def predict_aim_point(enemy_x, enemy_y, enemy_vx, enemy_vy, 
                      player_x, player_y, player_vx, player_vy, bullet_speed):

    # Vitesse relative
    rel_vx = enemy_vx - player_vx
    rel_vy = enemy_vy - player_vy

    dx = enemy_x - player_x
    dy = enemy_y - player_y
    distance = math.hypot(dx, dy)

    # Temps estimé pour que le projectile atteigne la cible
    time_to_hit = distance / bullet_speed

    # Position prédite de l’ennemi selon la vitesse relative
    predicted_x = enemy_x + rel_vx * time_to_hit
    predicted_y = enemy_y + rel_vy * time_to_hit

    predicted_x, predicted_y = convert_relative_to_screen_coords(predicted_x, predicted_y)

    return int(predicted_x), int(predicted_y)


CAPTURE_TOP = 114
CAPTURE_LEFT = 685
# adapter les coordonnées à la taille de l'écran
def convert_relative_to_screen_coords(predicted_x, predicted_y):
    predicted_x = CAPTURE_LEFT + predicted_x
    predicted_y = CAPTURE_TOP + predicted_y
    return predicted_x, predicted_y

# souris fluide
def human_move_mouse(target_x, target_y, duration=0.3):
    current_x, current_y = pyautogui.position()
    steps = int(duration * 100)  # ex : 30 ms → ~10 étapes

    for i in range(steps):
        t = i / steps
        # interpolation non linéaire : accélération/décélération
        t = t ** 1.5 if t < 0.5 else 1 - (1 - t) ** 1.5

        x = int(current_x + (target_x - current_x) * t + random.uniform(-1, 1))
        y = int(current_y + (target_y - current_y) * t + random.uniform(-1, 1))

        pyautogui.moveTo(x, y)
        time.sleep(0.01 + random.uniform(0.002, 0.005))  # petit délai

# viser un point légèrement autour de la cible, comme un humain qui n’est jamais parfait :
def get_human_aim_point(x, y, jitter=3):
    jitter_x = random.uniform(-jitter, jitter)
    jitter_y = random.uniform(-jitter, jitter)
    return int(x + jitter_x), int(y + jitter_y)

# fonction générale de visée "humaine"
def aim(enemy_x, enemy_y, enemy_vx, enemy_vy, 
                      player_x, player_y, player_vx, player_vy, bullet_speed):
    
    
    # anticiper future position de la cible
    aim_x, aim_y = predict_aim_point(enemy_x, enemy_y, enemy_vx, enemy_vy, 
                      player_x, player_y, player_vx, player_vy, bullet_speed)
    
    # viser un peu à côté 
    aim_x, aim_y = get_human_aim_point(aim_x, aim_y, jitter=3)
    
    # souris fluide
    human_move_mouse(aim_x, aim_y, duration=0.25)

    # délai de réaction humain
    # time.sleep(random.uniform(0.01, 0.1))
    pyautogui.click()

