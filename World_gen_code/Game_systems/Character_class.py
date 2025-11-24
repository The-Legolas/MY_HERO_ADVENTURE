import random
from enum import Enum

class Character():
    def __init__(self, name: str, hp: int, damage: int, defence: int, equipment: dict[str, any], level: int | None = None):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.defence = defence
        self.equipment = equipment
        self.level = level

    def take_damage(self, damage: int) -> None:
        self.hp -= damage
    
    def is_alive(self) -> bool:
        return True if self.hp > 0 else False
    
    def debug_attack(self, other: 'Character') -> None:
        text_block = ""

        text_block += f"{self.name} is attacking {other.name}"

        temp_damage = self.damage
        if random.random() >= 0.95:
            temp_damage *= 2

        if temp_damage > other.defence:
            damage_dealt = temp_damage - other.defence
            other.take_damage(damage_dealt)
            text_block += f" and deals {damage_dealt} damage!\n"

        else:
            text_block += " but it was blocked!\n"

        return text_block
    
    def attack(self, other: 'Character') -> None:
        outcome_table = {
            "attacker": self.name,
            "target": other.name,
            "damage": 0,
            "critical_hit": False,
            "blocked": False,
            "died": False
        }

        temp_damage = self.damage

        if random.random() >= 0.95:
            temp_damage *= 2
            outcome_table["critical_hit"] = True
        
        if temp_damage > other.defence:
            damage_dealt = temp_damage - other.defence
            outcome_table["damage"] = damage_dealt
            other.take_damage(damage_dealt)
        
        else:
            outcome_table["blocked"] = True
        
        if not other.is_alive():
            outcome_table["died"] = True
        
        return outcome_table
    
    def level_up(self) -> None:
        pass

    def __str__(self):
        return f"name:{self.name}, hp:{self.hp}, damage:{self.damage}, level:{self.level}, defence: {self.defence}, equipment: {self.equipment}"

def render_attack_text(outcome: dict) -> str:

        text_block = ""

        text_block += "ATTACK RESULT:"
        text_block += outcome["attacker"] + " attacks " + outcome["target"] + "\n"

        if outcome["critical_hit"] is True:
            text_block += "critical hit\n"

        if outcome["blocked"] is True:
            text_block += "The attack was blocked.\n"
        else:
            text_block += f"Damage dealt: {outcome["damage"]}\n"

        if outcome["warrior_rage"] == True:
            text_block += "Warrior enters RAGE and deals extra damage!\n"

        if outcome["died"] == True:
            text_block += outcome["target"] + " has fallen.\n"

        return text_block






def calculate_room_distance(room):
    x = room.pos_x
    y = room.pos_y

    depth = max(abs(x), abs(y))

    return depth