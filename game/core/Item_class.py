from __future__ import annotations
from enum import Enum
import random



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
    RING = "ring"


class Items():
    def __init__(self, name: str, category: Item_Type, stackable: bool, unique: bool,
                 stats: dict[str, any] | None = None, effect: dict[str, any] | None = None, 
                 passive_modifiers: dict[str, float] | None = None,
                 on_hit_status: dict | None = None, value: int = 0):
        self.name = name
        self.category = category
        self.stackable = stackable
        self.unique = unique
        self.value = value

        self.effect = effect
        self.stats = stats or {}
        self.passive_modifiers = passive_modifiers or {}
        self.on_hit_status = on_hit_status

    def get_tooltip(self) -> str:
        lines = []

        if self.stats:
            for k, v in self.stats.items():
                name = k.replace("_", " ").title()

                if isinstance(v, float):
                    lines.append(f"{name}: +{int(v * 100)}%")
                else:
                    sign = "+" if v > 0 else ""
                    lines.append(f"{name}: {sign}{v}")

        if self.passive_modifiers:
            for k, v in self.passive_modifiers.items():
                name = k.replace("_", " ").replace("resist", "Resist").title()
                lines.append(f"{name}: +{int(v * 100)}%")


        if isinstance(self.effect, dict):
            for effect, amount in self.effect.items():
                verb = effect.replace("_", " ").title()
                lines.append(f"Use: {verb} {amount}")



        elif isinstance(self.effect, list):
            for entry in self.effect:
                trigger = entry.get("trigger")
                chance = entry.get("chance", 1.0)
                status = entry.get("status")

                if not status:
                    continue

                status_name = status["id"].replace("_", " ").title()
                duration = status.get("duration")
                magnitude = status.get("magnitude")

                if magnitude is not None:
                    effect_text = f"{status_name} x{magnitude}"
                else:
                    effect_text = status_name

                if trigger == "on_hit":
                    lines.append(
                        f"\tOn hit: {int(chance * 100)}% chance to apply "
                        f"{effect_text} for {duration} turns"
                    )

                elif trigger == "on_turn":
                    lines.append(
                        f"Each turn: {int(chance * 100)}% chance to gain "
                        f"{effect_text} for for {duration} turns"
                    )

                elif trigger == "on_equip":
                    lines.append(
                        f"On equip: gain {effect_text}"
                    )

        return "\n".join(lines) if lines else ""



    def use(self, player, target):
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
    target.heal(amount)
    #target.hp += amount   #old version

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
        name      = template["name"],
        category  = template["category"],
        stackable = template["stackable"],
        unique    = template["unique"],
        stats     = template.get("stats"),
        effect    = template.get("effect"),      # ← SAFE ACCESS
        value     = template["value"],
    )

    # Attach optional behavior data
    if "on_hit_status" in template:
        item_obj.on_hit_status = template["on_hit_status"]

    if "on_equip_status" in template:
        item_obj.on_equip_status = template["on_equip_status"]

    return item_obj


def roll_loot(enemy):
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
    "venom_fang_dagger": {
    "name": "Venom Fang Dagger",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": False,
    "stats": {"damage": +3},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.80,
        "status": {
            "id": "poison",
            "magnitude": 2,
            "duration": 3,
        }
        }
    ],
    "value": 45
    },
    "cracked_warhammer": {
    "name": "Cracked Warhammer",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": False,
    "stats": {"damage": +6},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.45,
        "status": {
            "id": "weakened",
            "duration": 4,
            "magnitude": {"damage_mult": 0.8},
        }
        }
    ],
    "value": 60
    },
    "frostbrand_sword": {
    "name": "Frostbrand Sword",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": False,
    "stats": {"damage": +5},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.70, #0,15
        "status": {
            "id": "stun",
            "duration": 1,
            "magnitude": None,
        }
        }
    ],
    "value": 80
    },
    "bloodletter_axe": {
    "name": "Bloodletter Axe",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": False,
    "stats": {"damage": +7},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.60,
        "status": {
            "id": "strength_up",
            "duration": 2,
            "magnitude": {
                "damage_mult": 1.25
            },
            "target": "self"
        }
        }
    ],
    "value": 90
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
    "ring_of_vital_flow": {
    "name": "Ring of Vital Flow",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": False,
    "stats": None,
    "effect": [
        {
        "trigger": "on_equip",
        "status": {
            "id": "regen",
            "duration": -1,   # infinite while equipped
            "magnitude": 1
        }
        }
    ],
    "value": 75
    },
    "ring_of_iron_will": {
    "name": "Ring of Iron Will",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": False,
    "stats": {"stun_resist": 0.50},
    "effect": None,
    "value": 65
    },
    "ring_of_corruption": {
    "name": "Ring of Corruption",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": False,
    "stats": None,
    "effect": [
        {
        "trigger": "on_turn",
        "status": {
            "id": "strength_up",
            "duration": 2,
            "magnitude": {
                "damage_mult": 1.15
            }
        }
        }
    ],
    "value": 100
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
