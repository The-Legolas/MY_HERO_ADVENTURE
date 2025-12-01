from enum import Enum
import random
from game.core.Character_class import Character
from game.core.Enemy_class import Enemy, ENEMY_DEFINITIONS

def make_outcome(actor_name, action, target_name=None, damage=0, blocked=False, critical=False, died=False, extra=None):
    return {
        "actor": actor_name,
        "action": action,
        "target": target_name,
        "damage": int(damage),
        "blocked": bool(blocked),
        "critical": bool(critical),
        "died": bool(died),
        "extra": extra or {}
    }


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

    def use(self, player: Character, target: Character):
        if not self.effect:
            return make_outcome(player.name, "use_item_fail", getattr(target, "name", None),
                                extra={"reason": "not_consumable", "item": self.name})
        
        if self.category != Item_Type.CONSUMABLE:
            return make_outcome(player.name, "use_item_fail", getattr(target, "name", None),
                                extra={"reason": "no_effect", "item": self.name})
        

        total_damage = 0
        total_heal = 0
        details = []

        for effect_type, amount in self.effect.items():
            action = EFFECT_ACTIONS.get(effect_type)
            if not action:
                details.append({"effect": effect_type, "skipped": True})
                continue

            action(target, amount)

            if effect_type == "damage":
                total_damage += amount
            elif effect_type == "heal":
                total_heal += amount

            details.append({"effect": effect_type, "amount": amount})

        extra = {"item": self.name, "details": details}
        died = not target.is_alive() if hasattr(target, "is_alive") else False
        outcome = make_outcome(player.name, "use_item", getattr(target, "name", None),
                               damage=total_damage, blocked=False, critical=False, died=died, extra=extra)

        return outcome
        



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