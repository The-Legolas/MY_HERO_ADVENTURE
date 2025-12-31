import random
from enum import Enum
from ..core.Item_class import Items, spawn_item
from ..core.Enemy_class import Enemy, Enemy_type, spawn_enemy

class Room_Types(Enum):
    EMPTY = "empty"
    ENEMY_ROOM = "enemy room"
    TREASURE_ROOM  = "treasure room"
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
        
    def visualize_encounter(self):        
        text_block = ""
        text_block += "===== ENCOUNTER DEBUG VIEW =====\n"
        text_block += f"Room Type: {self.room_type} \n"
        text_block += f'Position: ({self.pos_x}, {self.pos_y})\n'

        text_block += "Enemies\n"
        if self.contents["enemies"]:
            for enemy in self.contents["enemies"]:
                text_block += f"{enemy.name} (hp: {enemy.hp}, damage: {enemy.damage}, rarity: {enemy.rarity}, type: {enemy.type}, subtype: {enemy.sub_type})\n"
        else:
            text_block += "No enemies spawned yet. (this is normal if room not entered)\n"
        

        text_block += "Items\n"
        if self.contents["items"]:
            for item in self.contents["items"]:
                text_block += f"{item.name}\n"
            
        else:
            text_block += "No items present.\n"

        return text_block

    def __str__(self):
        enemy_list = ", ".join([f"{enemy.name}, ({enemy.hp} HP), {enemy.type}" for enemy in self.contents["enemies"]]) or "None"
        item_list = ", ".join([f"{item.name}" for item in self.contents["items"]]) or "None"
        return f"{self.room_type.value}: Enemies - {enemy_list}, Items - {item_list}"


def treasure_room_spawner() -> list['Items']:
    item_list = []
    item_list_type = ["small_healing_potion", "medium_healing_potion", "grand_healing_potion", "explosive_potion", None]
    amount = random.randint(1, 4)
    if amount == 1:
        amount += 1
    for _ in range(amount):
        rnd = random.choice(item_list_type)
        if rnd is None:
            continue

        item_obj = spawn_item(rnd)
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

