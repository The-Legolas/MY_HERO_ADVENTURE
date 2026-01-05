import random
from enum import Enum
from game.core.Item_class import Items, spawn_item
from game.core.Enemy_class import Enemy, Enemy_type, spawn_enemy

class Room_Types(Enum):
    EMPTY = "empty"
    ENEMY_ROOM = "enemy room"
    TREASURE_ROOM  = "treasure room"
    REST_ROOM = "rest room"
    BOSS_ROOM = "boss room"


class Room(): 
    def __init__(self, room_type: Room_Types, pos_x: int =0, pos_y: int =0, day_counter: int =1):
        self.room_type = room_type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.contents = {
            "enemies": [], 
            "items": []
        }
        self.day_counter = day_counter
        self.visited: bool = False
        self.cleared: bool = False
        self.treasure_opened: bool = False
        self.is_miniboss_room = False
        self.rest_used_day: int | None = None


        match room_type:
            case Room_Types.TREASURE_ROOM:
                item_list = treasure_room_spawner()
                for item in item_list:
                    if item is None:
                        continue
                    self.contents["items"].append(item)
                            
            case Room_Types.BOSS_ROOM:
                for enemy in boss_room_spawner(self.day_counter):
                    self.contents["enemies"].append(enemy)
            
            case _: #Types.EMPTY
                pass

    def __str__(self):
        enemy_list = ", ".join([f"{enemy.name}, ({enemy.hp} HP), {enemy.type}" for enemy in self.contents["enemies"]]) or "None"
        item_list = ", ".join([f"{item.name}" for item in self.contents["items"]]) or "None"
        return f"{self.room_type.value}: Enemies - {enemy_list}, Items - {item_list}"


def treasure_room_spawner() -> list['Items']:
    item_list = []
    item_list_type = [
        "small_healing_potion", "medium_healing_potion", "grand_healing_potion", "explosive_potion", None,
        "venom_fang_dagger", "cracked_warhammer", "frostbrand_sword", "bloodletter_axe", "basic_armor", 
        "ring_of_vital_flow", "ring_of_iron_will", "ring_of_corruption", "stamina_tonic", "second_wind_potion",
        "antivenom_vial", "cooling_salve", "coagulant_tonic", "battle_elixir", "reinforcement_draught",
        "lesser_fortitude_draught", "volatile_concoction", "sluggish_brew", "poison_flask",
        "strength_elixir", "regeneration_draught", "slime_goop", "broken_helm",
        ]
    target_amount  = random.randint(2, 4)
    attempts = 0
    MAX_ATTEMPTS = 20
    unique_added = False

    while len(item_list) < target_amount and attempts < MAX_ATTEMPTS:
        attempts += 1
        rnd = random.choice(item_list_type)

        if rnd is None:
            continue

        item_obj = spawn_item(rnd)
        
        if item_obj.unique:
            if unique_added:
                continue
            unique_added = True
        
        item_list.append(item_obj)

    return item_list

def boss_room_spawner(day_counter:int = 1) -> list['Enemy']:
    enemy_list = []
    enemy_type = [Enemy_type.ENEMY_WOLF, Enemy_type.ENEMY_GOBLIN]

    if day_counter > 20:
        choice = random.choice(enemy_type)
        enemy = spawn_enemy(choice)
        enemy_list.append(enemy)

    boss = spawn_enemy(Enemy_type.ENEMY_BOSS_DRAGON)
    enemy_list.append(boss)

    return enemy_list

