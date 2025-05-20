import time

# from bullet_avoidance import is_dangerous_bullet
from farm import farm


last_farm_time = 0

def actions_decider(all_draw_instructions, auto_fire_on):
    global last_farm_time

    now = time.time()

    threat = {"ennemy_bullet", 'ennemy_player'}
    object_to_avoid = {"ennemy_bullet"}
    tank_to_fight = {"ennemy_player"}

    if threat is True:
        return

    else:
        shapes_to_farm = {"yellow_square", "red_triangle", "blue_pentagon"}
        farm_targets = [
            item for item in all_draw_instructions
            if item.get("type") in shapes_to_farm
        ]

        # Farmer
        if (farm_targets or auto_fire_on) and (now - last_farm_time > 0.1): # 0.1 =  max 10 FPS
            auto_fire_on = farm(farm_targets, auto_fire_on)
            last_farm_time = now


    return auto_fire_on