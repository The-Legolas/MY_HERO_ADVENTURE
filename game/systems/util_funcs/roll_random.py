import random

from game.systems.enums.room_types import Room_Types

from game.engine.item_spawner import spawn_item



def roll_loot(enemy):
        loot_result = []
        gold_gained = enemy.gold_reward

        for drop_entry in enemy.loot_table:
            item_id = drop_entry["item"]
            chance = drop_entry["chance"]

            roll = random.random()

            if roll <= chance:
                item_object = spawn_item(item_id)
                loot_result.append(item_object)
        
        return {
            "gold": gold_gained,
            "items": loot_result
        }

def roll_enemy_count() -> int:
        rnd = random.random()
        if rnd < 0.55:
            return 1
        elif rnd < 0.95:
            return 2
        else:
            return 3
        

def roll_room_type(day_counter: int, depth: int) -> Room_Types:
    if depth >= 6:
        if random.random() < 0.08:
            return Room_Types.REST_ROOM

    # The real versions
    enemy_chance = min(0.50 + day_counter * 0.01, 0.90)
    treasure_chance = max(0.20 - day_counter * 0.005, 0.025)

    # Debug version
    #enemy_chance = max(0.50 + day_counter * 0.01, 0.99999)
    #treasure_chance = min(0.20 - day_counter * 0.005, 0.0001)



    rnd = random.random()

    if rnd < enemy_chance:
        return Room_Types.ENEMY_ROOM
    elif rnd < (enemy_chance + treasure_chance):
        return Room_Types.TREASURE_ROOM
    else:
        return Room_Types.EMPTY
    