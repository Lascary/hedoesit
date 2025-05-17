from farm import farm

def actions_decider(all_draw_instructions, auto_fire_on):
    shapes_to_farm = {"yellow_square", "red_triangle", "blue_pentagon"}

    farm_targets = [
        item for item in all_draw_instructions
        if item.get("type") in shapes_to_farm
    ]

    if farm_targets:
        auto_fire_on = farm(farm_targets, auto_fire_on)

    elif auto_fire_on:
        # Si plus rien à farmer mais le tir auto est actif, on le coupe
        auto_fire_on = farm([], auto_fire_on)

    return auto_fire_on