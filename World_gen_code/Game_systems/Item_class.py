from enum import Enum
import random
from Game_systems.Character_class import Character
from Game_systems.Enemy_class import Enemy, ENEMY_DEFINITIONS

class Item_Type(Enum):
    CONSUMABLE = "consumable"
    WEAPON = "weapon"
    ARMOR = "armor"
    SCRAP = "scrap"


class Items():
    def __init__(self, name: str, category: Item_Type, stackable: bool, unique: bool,
                 stats: dict[str, any] | None = None, 
                 effect: dict[str, any] | None = None, value: int = 0):
        self.name = name
        self.category = category
        self.stackable = stackable
        self.unique = unique
        self.stats = stats
        self.effect = effect
        self.value = value

    def use(self, target: 'Character'):
        if not self.effect:
            return "No effect to apply."
        
        if self.category != Item_Type.CONSUMABLE:
            return "Item cannot be used."
        

        text_block = ""

        for effect_type, amount in self.effect.items():
            action = EFFECT_ACTIONS.get(effect_type)
            if action:
                action(target, amount)

            verb = EFFECT_VERBS.get(effect_type, effect_type)

            text_block += f"{target.name.capitalize()} has been {verb} by {self.name} for {amount}.\n"

        return text_block



def apply_heal(target, amount):
    target.hp += amount

def apply_damage(target, amount):
    target.hp -= amount

EFFECT_VERBS = {
    "heal": "healed",
    "damage": "damaged",
}

EFFECT_ACTIONS = {
    "heal": apply_heal,
    "damage": apply_damage,
}


def spawn_item(item_type):
    template = ITEM_DEFINITIONS[item_type].copy()

    item_obj = Items(
            name        = template["name"],
            category    = template["category"],
            stackable   = template["stackable"],
            unique      = template["unique"],
            stats       = template["stats"],
            effect      = template["effect"],
            value       = template["value"],
        )

    return item_obj


def roll_loot(enemy: Enemy):
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



ITEM_DEFINITIONS = {
    "basic_sword": {
        "name": "Basic Sword",
        "category": Item_Type.WEAPON,
        "stackable": False,
        "unique": True,
        "stats": {"damage": +5},
        "effect": None,
        "value": 15
    },
    "improved_sword": {
        "name": "Improved Sword",
        "category": Item_Type.WEAPON,
        "stackable": False,
        "unique": True,
        "stats": {"damage": +20, "crit_chance": +0.05},
        "effect": None,
        "value": 40
    },
    "basic_armor": {
        "name": "Basic Armor",
        "category": Item_Type.ARMOR,
        "stackable": False,
        "unique": True,
        "stats": {"defence": +8},
        "effect": None,
        "value": 10
    },
    "improved_armor": {
        "name": "Improved Armor",
        "category": Item_Type.ARMOR,
        "stackable": False,
        "unique": True,
        "stats": {"defence": +25},
        "effect": None,
        "value": 50
    },
    "small_healing_potion": {
        "name": "Small Healing Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"heal": 30},
        "value": 15
    },
    "medium_healing_potion": {
        "name": "Medium Healing Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"heal": 70},
        "value": 30
    },
    "grand_healing_potion": {
        "name": "Grand Healing Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"heal": 150},
        "value": 60
    },
    "explosive_potion": {
        "name": "Explosive Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"damage": 25},
        "value": 25
    },
    "wolf_tooth": {
        "name": "Wolf Tooth",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 8
    },
    "slime_goop": {
        "name": "Slime Goop",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 5
    },
    "goblin_ear": {
        "name": "Goblin Ear",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 3
    },
}