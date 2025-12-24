import random
from .Character_class import Character

class Warrior(Character):
    def __init__(self, name: str):
        base_hp = 70 # 30
        base_damage = 10 # 6
        base_defence = 1 # 3

        hp = int(base_hp * 1.2)
        damage = int(base_damage * 0.9)
        defence = int(base_defence * 1.2)

        super().__init__(name, hp, damage, defence)

        self.level = 1
        self.max_hp = self.hp
        self.xp = 0

        self.known_skills = {
            "shield_bash",
            "poison_strike",
            "war_cry",
        }

        self.usable_skills = [
            "shield_bash",
            "poison_strike",
            "war_cry",
        ]
    
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

    def level_up(self): #this method should be called exp_up but I don't want to implement it before I know how hard to make the enemies
        if self.level == 10:
            return "Cannot increase to more than 10" # should be reworked when xp have been implemented so the xp just go up and level doesn't change
        temp_level = self.level
                
        #add xp gain later for now I will just increase level by 1 when this method is called
        self.level += 1

        if self.level > temp_level:
            if self.level <= 5:
                self.defence *= 1.3
                self.hp *= 1.3
                self.damage *= 1.2
            
            elif self.level <= 8:
                self.defence *= 1.4
                self.hp *= 1.5
                self.damage *= 1.3
            
            elif self.level == 9:
                self.defence *= 1.6
                self.hp *= 1.7
                self.damage *= 1.4
            
            elif self.level == 10:
                self.defence *= 1.8
                self.hp *= 1.9
                self.damage *= 1.6
