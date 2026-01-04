import random
from .character import Character

class Warrior(Character):
    def __init__(self, name: str, starting_items: dict[str, int] | None = None, gold: int = 0):
        base_hp = 70 # 30
        base_damage = 500 # 6
        base_defence = 1 # 3

        scaled_hp = int(base_hp * 1.2)
        scaled_damage = int(base_damage * 0.9)
        scaled_defence = int(base_defence * 1.2)

        super().__init__(name,  hp=scaled_hp, damage=scaled_damage, defence=scaled_defence, starting_items=starting_items, gold=gold)
        self.class_id = "warrior"
        self.usable_skills = ["poison_strike"]
        self.resource_name = "Stamina"
        self.resource_max = 40
        self.resource_current = self.resource_max

    
    def take_damage(self, damage: int):
        reduced_damage = int(damage * 0.9)
        return super().take_damage(reduced_damage)
    
   
    
