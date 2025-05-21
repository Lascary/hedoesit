import math
import time
import keyboard

def threat_score(proj_x, proj_y, proj_vx, proj_vy, proj_size,
                 player_x, player_y):

    dx = player_x - proj_x
    dy = player_y - proj_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        dist = 0.01

    speed = math.hypot(proj_vx, proj_vy)
    if speed == 0:
        return 0

    # Angle entre la direction de la balle et le vecteur vers le joueur
    dot = (proj_vx * dx + proj_vy * dy) / (speed * dist)

    # Score basé sur distance inverse, vitesse, taille, et angle
    score = (1 / dist) * speed * proj_size * max(dot, 0)

    return score

def get_repulsion_vector(proj_x, proj_y, proj_vx, proj_vy,
                         player_x, player_y, proj_size):

    dx = player_x - proj_x
    dy = player_y - proj_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        dist = 0.01

    # Normaliser le vecteur de direction balle -> joueur
    nx = dx / dist
    ny = dy / dist

    # Force inversement proportionnelle à la distance (exponentielle possible)
    force = (proj_size * 10) / (dist ** 2)

    # Vecteur répulsif = direction opposée vers balle multipliée par force
    rx = -nx * force
    ry = -ny * force

    return rx, ry

def combined_avoidance_vector(projectiles, player_x, player_y):
    total_rx, total_ry = 0, 0

    # Filtrer les menaces selon un seuil
    threat_threshold = 0.1

    for proj in projectiles:
        px, py, vx, vy, size = proj
        score = threat_score(px, py, vx, vy, size, player_x, player_y)
        if score > threat_threshold:
            rx, ry = get_repulsion_vector(px, py, vx, vy, player_x, player_y, size)
            # Pondérer le vecteur répulsif par le score
            total_rx += rx * score
            total_ry += ry * score

    # Normaliser le vecteur résultant
    mag = math.hypot(total_rx, total_ry)
    if mag == 0:
        return 0, 0
    return total_rx / mag, total_ry / mag

# Exemple d'utilisation dans la boucle principale
def evade(projectiles, player_x, player_y):
    dx, dy = combined_avoidance_vector(projectiles, player_x, player_y)
    if dx == 0 and dy == 0:
        return  # pas de menace

    # Convertir en appui sur touches
    # On choisit la touche dominante selon dx, dy
    keys = []
    if dy < -0.3:
        keys.append("w")
    elif dy > 0.3:
        keys.append("s")
    if dx < -0.3:
        keys.append("a")
    elif dx > 0.3:
        keys.append("d")

    # Appuyer sur ces touches quelques instants
    for k in keys:
        keyboard.press(k)
    time.sleep(0.15)
    for k in keys:
        keyboard.release(k)


# Conseils:
#     Ajuste les coefficients dans threat_score et get_repulsion_vector pour correspondre à ta situation.

#     Tu peux affiner le champ de force avec des fonctions exponentielles pour donner plus de poids aux balles très proches.

#     Ajoute un seuil minimal de vitesse pour ignorer les balles lentes qui ne représentent pas de menace.

#     Essaie différentes durées d’appui des touches pour un mouvement fluide.