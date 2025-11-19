import random

class Character():
    def __init__(self, name: str, hp: int, damage: int, defence: int, equipment: dict[str, ], level: int = None,):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.defence = defence
        self.equipment = equipment
        self.level = level
    
    def attack(self, other: 'Character'):
        text_block = ""

        text_block += f"{self.name} is attacking {other.name}"

        temp_damage = self.damage
        if random.random() >= 0.95:
            temp_damage *= 2

        if temp_damage > other.defence:
            damage_dealt = temp_damage - other.defence
            other.hp -= damage_dealt
            text_block += f" and deals {damage_dealt} damage!\n"
        else:
            text_block += " but it was blocked!\n"
        


    




class Enemy():
    def __init__(self, name: str, hp: int, damage: int):
        self.name = name
        self.hp = hp
        self.damage = damage

    def list() -> list:
        list_of_enemies = []
    
        list_of_enemies.append(Enemy("bat", 10, 2))
        list_of_enemies.append(Enemy("skeleton", 5, 10))
        list_of_enemies.append(Enemy("ogre", 100, 30))

        return list_of_enemies


rnd = random.random
print(float(rnd))