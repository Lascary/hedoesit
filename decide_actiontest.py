import time

# from bullet_avoidance import is_dangerous_bullet
from farm import farm
from attack import attack
from flew import flew
from evade import avoid_bullets

last_farm_time = 0

def actions_decider(all_draw_instructions, auto_fire_on):
    global last_farm_time

    now = time.time()

    farm_targets = []
    ennemy_bullets = []
    ennemy_players = []
    # threat = is_threat(all_draw_instructions)
    for item in all_draw_instructions:
        if "type" == "ennemy_bullet":
            ennemy_bullets.append(item)
        elif "type" == "ennemy_player":
            ennemy_players.apped(item)
        elif"type" == "yellow_square"or "red_triangle"or "blue_pentagon":
            farm_targets.append(item)
        elif "type" == "self":
            player = item

    if ennemy_bullets:
        avoid_bullets(ennemy_bullets, player_x, player_y)

    if ennemy_players:
        aim(enemy_x, enemy_y, enemy_vx, enemy_vy, 
                      player_x, player_y, player_vx, player_vy, bullet_speed)

    if (farm_targets or auto_fire_on) and (now - last_farm_time > 0.05): # 0.1 =  max 10 FPS
        auto_fire_on = farm(farm_targets, auto_fire_on)
        last_farm_time = now


    return auto_fire_on


# def is_collision_trajectory():
#     for item in all_draw_instructions:
#         if "type" == "self":
#             self_vx = item["speed_x"]
#             self_vy = item["speed_y"]
#             self_x, y = item.get("position", (0, 0))
#         if "type" == "ennemy_bullet":
#             bullet_vx = item["speed_x"]
#             bullet_vy = item["speed_y"]
#             bullet_x, y = item.get("position", (0, 0))
#         if "type" == "ennemy_player":
#             ennemy_vx = item["speed_x"]
#             ennemy_vy = item["speed_y"]
#             ennemy_x, y = item.get("position", (0, 0))
