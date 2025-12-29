import random
from .Character_class import Character

class Warrior(Character):
    def __init__(self, name: str, starting_items: dict[str, int] | None = None, gold: int = 0):
        base_hp = 70 # 30
        base_damage = 9 # 6
        base_defence = 1 # 3

        scaled_hp = int(base_hp * 1.2)
        scaled_damage = int(base_damage * 0.9)
        scaled_defence = int(base_defence * 1.2)

        super().__init__(name,  hp=scaled_hp, damage=scaled_damage, defence=scaled_defence, starting_items=starting_items, gold=gold)
        self.class_id = "warrior"
        self.usable_skills = []
    
    def take_damage(self, damage: int):
        reduced_damage = int(damage * 0.9)
        return super().take_damage(reduced_damage)
    
    def attack(self, other: 'Character'):
        outcome = super().attack(other)
        if outcome["blocked"] == True:
            return outcome

        if self.hp <= (self.max_hp * 0.40) and random.random() >= 0.30: #extra damage eg. rage which will be implemented later
            outcome["warrior_rage"] = True

            extra_damage = int(outcome["damage"] * 0.5)
            if extra_damage > 0 and other.is_alive():
                other.take_damage(extra_damage)
                outcome["damage"] += extra_damage
                if not other.is_alive():
                    outcome["died"] = True

        return outcome
    
