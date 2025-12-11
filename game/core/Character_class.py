import random
from .Item_class import Item_Type, Items, make_outcome


class Character():
    def __init__(self, name: str, hp: int, damage: int, defence: int):
        self.name = name
        self.hp = hp
        self.max_hp = self.hp
        self.damage = damage
        self.defence = defence
        self.xp = 0
        

        self.equipment = {
            "weapon": None,
            "armor": None,
            "ring1": None,
            "ring2": None
        }

        self.inventory = {
            "items": {},
            "gold": 0
        }
    
    def add_item(self, item: Items, amount:int = 1) -> None:
        if item.name not in self.inventory["items"]:
            self.inventory["items"][item.name] = {
                "item": item, 
                "count": amount
                }
            return
        
        if item.stackable:
            self.inventory["items"][item.name]["count"] += amount
    

    def remove_item(self, item_id: str, amount: int = 1) -> None:
        items = self.inventory["items"]

        if item_id not in items:
            return  # nothing to remove

        entry = items[item_id]
        item_obj = entry["item"]

        # stackable items
        if item_obj.stackable:
            entry["count"] -= amount
            if entry["count"] <= 0:
                del items[item_id]

        # unique / non-stackable
        else:
            del items[item_id]

    def use_item(self, item: Items, target: 'Character') -> None:
        if isinstance(item, str):
            entry = self.inventory["items"].get(item)
            if not entry:
                return make_outcome(self.name, "use_item_fail", getattr(target, "name", None),
                                    extra={"reason": "item_key_missing", "item_key": item})
            item_obj = entry["item"]
        else:
            item_obj = item

        outcome = item_obj.use(self, target)

        inventory = self.inventory["items"]
        if item_obj.name in inventory:
            entry = inventory[item_obj.name]
            if item_obj.stackable:
                entry["count"] -= 1
                if entry["count"] <= 0:
                    del inventory[item_obj.name]
            else:
                del inventory[item_obj.name]

        return outcome
        

    def equip_item(self, item: Items) -> None:
        if item.category not in (Item_Type.WEAPON, Item_Type.ARMOR):
            return f"Cannot equip {item.category}"

        slot = "weapon" if item.category == Item_Type.WEAPON else "armor"

        if self.equipment[slot] is not None:
            self.unequip_item(self.equipment[slot])
        
        self.equipment[slot] = item

        for stat, value in item.stats.items():
            if stat == "damage":
                self.damage += value
            elif stat == "defence":
                self.defence += value
            elif stat == "hp":
                self.hp += value
            elif stat == "crit_chance":
                pass #not implemented yet

        self.remove_item(item, 1)
        

    def unequip_item(self, item: Items) -> None:
        slot = item.category

        for stat, value in item.stats.items():
            if stat == "damage":
                self.damage -= value
            elif stat == "defence":
                self.defence -= value
            elif stat == "hp":
                self.hp -= value
            elif stat == "crit_chance":
                pass #not implemented yet

        self.add_item(item, 1)

        self.equipment[slot] = None


    def sell_item(self, item: Items) -> None:
        if item.value == 0:
            return "Failed to sell"
        self.inventory["gold"] += item.value
        self.remove_item(item, 1)


    def take_damage(self, damage: int) -> None:
        self.hp -= damage


    def is_alive(self) -> bool:
        return True if self.hp > 0 else False


    def debug_attack(self, other: 'Character') -> str:
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
    

    def attack(self, other: 'Character') -> dict:
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

