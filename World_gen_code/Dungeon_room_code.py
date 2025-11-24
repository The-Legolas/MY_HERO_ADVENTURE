import sys
import os
# Add the project's root folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from enum import Enum
from Game_systems.Item_class import Items
from Game_systems.Enemy_class import Enemy

class Room_Types(Enum):
    EMPTY = "empty"
    ENEMY_ROOM = "enemy room"
    TREASURE_ROOM  = "treassure room"
    TAVERN = "tavern"
    SHOP = "shop"
    INN = "inn"
    BOSS_ROOM = "boss room"


class Room(): 
    def __init__(self, room_type, pos_x=0, pos_y=0, day_counter=1):
        self.room_type = room_type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.connections = {}
        self.contents = {
            "enemies": [], 
            "items": []
        }
        self.day_counter = day_counter
        self.enemy_template = None

        match room_type:
            case Room_Types.TREASURE_ROOM:
                for _ in range(random.randint(0, 2)):
                    self.contents["items"].append(random.choice(Items.list()))
                
            case Room_Types.ENEMY_ROOM:
                for _ in range(random.randint(1, 4)):
                    base_enemy = random.choice(Enemy.list())
        
                    # Calculate modifier (e.g., 10% increase per day after day 1)
                    modifier = 1 + (self.day_counter - 1) * 0.1
                    
                    modified_hp = int(base_enemy.hp * modifier)
                    modified_damage = int(base_enemy.damage * modifier)
                    new_enemy = Enemy(base_enemy.name, modified_hp, modified_damage)

                    self.contents["enemies"].append(new_enemy)

                    if len(self.contents["enemies"]) >= 2:
                        break

                    has_ogre = False
                    for enemy in self.contents["enemies"]:
                        if enemy.name == "ogre":
                            has_ogre = True
                            break
                    if has_ogre:
                        break
                
                self.contents["items"].append(random.choice(Items.list()))
            
            case Room_Types.BOSS_ROOM:
                self.contents["enemies"].append(Enemy("Dragon", 50, 20))
                self.contents["items"].append(Items("Magic Potion", "potion", None, 30))
            
            case _: #Types.EMPTY
                pass
        
    def visualize_encounter(self):
        if self.room_type not in Room_Types:
            return
        
        text_block = ""
        text_block += "===== ENCOUNTER DEBUG VIEW =====\n"
        text_block += f"Room Type: {self.room_type} \n"
        text_block += f'Position: ({self.pos_x}, {self.pos_y})\n'

        text_block += "Enemies\n"
        if self.contents["enemies"]:
            for enemy in self.contents["enemies"]:
                text_block += f"{enemy.name} (hp: {enemy.hp}, damage: {enemy.damage})\n"
        else:
            text_block += "No enemies present.\n"
        

        text_block += "Items\n"
        if self.contents["items"]:
            for item in self.contents["items"]:
                text_block += item.name + "\n"
            
        else:
            text_block += "No items present.\n"

        return text_block
    
    def set_enemy_template(self, enemy_type):
        self.enemy_template = enemy_type

    def __str__(self):
        enemy_list = ", ".join([f"{enemy.name} ({enemy.hp} HP)" for enemy in self.contents["enemies"]]) or "None"
        item_list = ", ".join([f"{item.name}" for item in self.contents["items"]]) or "None"
        return f"{self.room_type.value}: Enemies - {enemy_list}, Items - {item_list}"
