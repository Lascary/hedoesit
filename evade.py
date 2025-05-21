import math
import keyboard  # plus réactif que pyautogui pour les touches

def is_threatening(projectile_x, projectile_y, projectile_vx, projectile_vy, 
                   player_x, player_y, safety_radius=30):

    dx = player_x - projectile_x
    dy = player_y - projectile_y
    distance = math.hypot(dx, dy)

    # Normalisation du vecteur vers le joueur
    if distance == 0:
        return True  # situation rare
    dx /= distance
    dy /= distance

    # Normalisation de la direction de la balle
    speed = math.hypot(projectile_vx, projectile_vy)
    if speed == 0:
        return False
    vxn = projectile_vx / speed
    vyn = projectile_vy / speed

    dot_product = dx * vxn + dy * vyn

    return dot_product > 0.9 and distance < safety_radius * 5


def get_evasion_direction(projectile_vx, projectile_vy):
    # direction perpendiculaire (90°)
    return -projectile_vy, projectile_vx  # ou (projectile_vy, -projectile_vx)



def evade(dx, dy):
    if dx > 0: keyboard.press("d")
    if dx < 0: keyboard.press("a")
    if dy > 0: keyboard.press("s")
    if dy < 0: keyboard.press("w")
    keyboard.release("w")
    keyboard.release("a")
    keyboard.release("s")
    keyboard.release("d")


def avoid_bullets(projectiles, player_x, player_y):
    for proj in projectiles:
        px, py, vx, vy = proj
        if is_threatening(px, py, vx, vy, player_x, player_y):
            evasion_dx, evasion_dy = get_evasion_direction(vx, vy)
            evade(evasion_dx, evasion_dy)
            break  # éviter un seul projectile à la fois

