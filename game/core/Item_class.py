from __future__ import annotations
from enum import Enum
import random
from game.core.Status import Status



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
        self.id = None
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

        # ─── STATS ───────────────────────────────────────────
        if self.stats:
            for k, v in self.stats.items():
                name = k.replace("_", " ").title()

                if isinstance(v, float):
                    lines.append(f"\t{name}: +{int(v * 100)}%")
                else:
                    sign = "+" if v > 0 else ""
                    lines.append(f"\t{name}: {sign}{v}")

        # ─── PASSIVE MODIFIERS (resists, etc.) ───────────────
        if self.passive_modifiers:
            for k, v in self.passive_modifiers.items():
                name = k.replace("_", " ").replace("resist", "Resist").title()
                lines.append(f"\t{name}: +{int(v * 100)}%")

        # ─── NO EFFECT ───────────────────────────────────────
        if not self.effect:
            return "\n".join(lines)

        # ─── CONSUMABLE EFFECTS (dict) ───────────────────────
        if isinstance(self.effect, dict):
            summary_parts = []
            detail_lines = []

            if "apply_status" in self.effect:
                status_data = self.effect["apply_status"]
                status_name = status_data["id"].replace("_", " ").title()
                duration = status_data.get("duration")

                summary_parts.append(f"applies {status_name.lower()}")
                if duration:
                    detail_lines.append(f"\t• {status_name} for {duration} turns")
                else:
                    detail_lines.append(f"\t• {status_name}")

            if "heal" in self.effect:
                amount = self.effect["heal"]
                summary_parts.append("restores health")
                detail_lines.append(f"\t• Heals {amount} HP")

            if "damage" in self.effect:
                amount = self.effect["damage"]
                summary_parts.append("deals damage")
                detail_lines.append(f"\t• Deals {amount} damage")

            if "remove_status" in self.effect:
                status = self.effect["remove_status"].replace("_", " ").title()
                summary_parts.append(f"cures {status.lower()}")
                detail_lines.append(f"\t• Removes {status}")

            if "restore_resource" in self.effect:
                amount = self.effect["restore_resource"]
                summary_parts.append("restores stamina")
                detail_lines.append(f"\t• Restores {amount} stamina")

            if summary_parts:
                lines.append(f"\tUse: {' and '.join(summary_parts).capitalize()}")
                for d in detail_lines:
                    lines.append(f"  {d}")

            return "\n".join(lines)

        # ─── TRIGGERED / PASSIVE EFFECTS (list) ──────────────
        if isinstance(self.effect, list):
            for entry in self.effect:
                trigger = entry.get("trigger", "unknown")
                chance = entry.get("chance", 1.0)
                status = entry.get("status")

                if not status:
                    continue

                status_name = status["id"].replace("_", " ").title()
                duration = status.get("duration")
                magnitude = status.get("magnitude")

                # Human-readable trigger
                trigger_text = {
                    "on_hit": "On hit",
                    "on_equip": "On equip",
                    "on_turn": "Each turn",
                }.get(trigger, trigger.replace("_", " ").title())

                line = f"\t{trigger_text}: {status_name}"
                
                if duration is not None:
                    if duration < 0:
                        line += " (while equipped)"
                    else:
                        line += f" ({duration} turns)"

                if chance < 1.0:
                    line += f" — {int(chance * 100)}% chance"

                lines.append(line)

            return "\n".join(lines)

        return "\n".join(lines)



    def use(self, player, target):
        if not self.effect:
            return make_outcome(player.name, "use_item_fail", getattr(target, "name", None),
                                extra={"reason": "not_consumable", "item": self.name})
        
        if self.category != Item_Type.CONSUMABLE:
            return make_outcome(player.name, "use_item_fail", getattr(target, "name", None),
                                extra={"reason": "no_effect", "item": self.name})
        
        did_something = False        

        total_damage = 0
        total_heal = 0
        details = []

        if isinstance(self.effect, dict):
            for effect_type, amount in self.effect.items():
                if effect_type in ("heal", "damage"):
                    action = EFFECT_ACTIONS.get(effect_type)
                    if not action:
                        continue

                    action(target, amount)

                    if effect_type == "heal":
                        total_heal += amount
                    elif effect_type == "damage":
                        total_damage += amount
                        
                    details.append({
                        "effect": effect_type,
                        "amount": amount
                    })

                    did_something = True
                    continue

                # ─── APPLY STATUS ──────────────────────────────
                if effect_type == "apply_status":
                    status = Status(
                        id=amount["id"],
                        remaining_turns=amount["duration"],
                        magnitude=amount.get("magnitude"),
                        source=self.name
                    )

                    result = target.apply_status(status)

                    details.append({
                        "effect": "apply_status",
                        "status": status.id,
                        "applied": result
                    })

                    if result:
                        did_something = True
                    continue

                # ─── REMOVE STATUS ─────────────────────────────
                if effect_type == "remove_status":
                    success = apply_remove_status(target, amount)

                    details.append({
                        "effect": "remove_status",
                        "status": amount,
                        "success": success
                    })

                    if success:
                        did_something = True
                    continue

                if effect_type == "restore_resource":
                    before = target.resource_current
                    target.resource_current = min(
                        target.resource_max,
                        target.resource_current + amount
                    )

                    details.append({
                        "effect": "restore_resource",
                        "amount": amount,
                        "before": before,
                        "after": target.resource_current,
                    })

                    did_something = True
                    continue

            if not did_something:
                return make_outcome(
                    player.name,
                    "use_item_fail",
                    getattr(target, "name", None),
                    extra={"reason": "no_effect", "item": self.name}
                )

            return make_outcome(
                player.name,
                "use_item",
                getattr(target, "name", None),
                damage=total_damage,
                blocked=False,
                critical=False,
                died=hasattr(target, "is_alive") and not target.is_alive(),
                extra={
                    "item": self.name,
                    "details": details
                }
            )

        # CASE 2 — status effects
        elif isinstance(self.effect, list):
            for entry in self.effect:
                if entry.get("type") != "status":
                    continue

                status_data = entry.get("status")
                if not status_data:
                    continue

                status = Status(
                    id=status_data["id"],
                    remaining_turns=status_data["duration"],
                    magnitude=status_data.get("magnitude"),
                    source=self.name
                )

                result = target.apply_status(status)
                if result:
                    did_something = True

                details.append({
                    "effect": "status",
                    "status": status.id,
                    "applied": result
                })

        if did_something:
            return make_outcome(
                player.name,
                "use_item",
                getattr(target, "name", None),
                damage=total_damage,
                blocked=False,
                critical=False,
                died=hasattr(target, "is_alive") and not target.is_alive(),
                extra={
                    "item": self.name,
                    "details": details
                }
            )

        return make_outcome(
            player.name,
            "use_item_fail",
            getattr(target, "name", None),
            extra={
                "reason": "no_effect",
                "item": self.name
            }
        )
        

def apply_heal(target, amount):
    target.heal(amount)

def apply_damage(target, amount):
    target.hp -= amount

def apply_status_effect(target, status_data):
    status = Status(
        id=status_data["id"],
        remaining_turns=status_data["duration"],
        magnitude=status_data.get("magnitude"),
        source="item"
    )
    target.apply_status(status, None)

def apply_remove_status(target, status_id):
    if not hasattr(target, "statuses"):
        return False

    before = len(target.statuses)
    target.statuses = [s for s in target.statuses if s.id != status_id]
    after = len(target.statuses)

    return before != after

EFFECT_VERBS = {
    "heal": "heals",
    "damage": "damages",
}

EFFECT_ACTIONS = {
    "heal": apply_heal,
    "damage": apply_damage,
    "apply_status": apply_status_effect,
    "remove_status": apply_remove_status,
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
    item_obj.id = item_type

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
        "stats": {"damage": +7},
        "effect": None,
        "value": 90
    },
    
    "improved_sword": {
        "name": "Improved Sword",
        "category": Item_Type.WEAPON,
        "stackable": False,
        "unique": True,
        "stats": {"damage": +20},
        "effect": None,
        "value": 300
    },

    "venom_fang_dagger": {
    "name": "Venom Fang Dagger",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +3},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.99, # 0.80
        "status": {
            "id": "poison",
            "magnitude": 2,
            "duration": 3,
        }
        }
    ],
    "value": 150
    },

    "cracked_warhammer": {
    "name": "Cracked Warhammer",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +6},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.96, #0,45
        "status": {
            "id": "weakened",
            "duration": 4,
            "magnitude": 0.8,
        }
        }
    ],
    "value": 160
    },

    "frostbrand_sword": {
    "name": "Frostbrand Sword",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +5},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.99, #0,15
        "status": {
            "id": "stun",
            "duration": 2,
            "magnitude": None,
        }
        }
    ],
    "value": 145
    },

    "bloodletter_axe": {
    "name": "Bloodletter Axe",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +7},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.95, # 0,60
        "status": {
            "id": "strength_up",
            "duration": 2,
            "magnitude": 1.25,
            "target": "self"
        }
        }
    ],
    "value": 170
    },

    "basic_armor": {
        "name": "Basic Armor",
        "category": Item_Type.ARMOR,
        "stackable": False,
        "unique": True,
        "stats": {"defence": +8},
        "effect": None,
        "value": 90
    },

    "improved_armor": {
        "name": "Improved Armor",
        "category": Item_Type.ARMOR,
        "stackable": False,
        "unique": True,
        "stats": {"defence": +25},
        "effect": None,
        "value": 400
    },

    "ring_of_vital_flow": {
    "name": "Ring of Vital Flow",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": True,
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
    "unique": True,
    "stats": {"stun_resist": 0.50},
    "effect": None,
    "value": 65
    },

    "ring_of_corruption": {
    "name": "Ring of Corruption",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": True,
    "stats": None,
    "effect": [
        {
        "trigger": "on_turn",
        "status": {
            "id": "strength_up",
            "duration": 2,
            "magnitude": 1.15
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

    "stamina_tonic": {
        "name": "Stamina Tonic",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "restore_resource": 20
        },
        "value": 18
    },

    "second_wind_potion": {
        "name": "Second Wind Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "restore_resource": 40
        },
        "value": 32
    },

    "antivenom_vial": {
        "name": "Antivenom Vial",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "poison"
        },
        "value": 30
    },

    "cooling_salve": {
        "name": "Cooling Salve",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "burn"
        },
        "value": 30
    },

    "coagulant_tonic": {
        "name": "Coagulant Tonic",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "bleed"
        },
        "value": 30
    },

    "battle_elixir": {
        "name": "Battle Elixir",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "weakened"
        },
        "value": 30
    },

    "reinforcement_draught": {
        "name": "Reinforcement Draught",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "armor_down"
        },
        "value": 30
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

    "lesser_fortitude_draught": {
        "name": "Lesser Fortitude Draught",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "defending",
                "duration": 2,
                "magnitude": None
            }
        },
        "value": 20
    },

    "strength_elixir": {
        "name": "Strength Elixir",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "effect": {
            "apply_status": {
                "id": "strength_up",
                "duration": 3,
                "magnitude": None
            }
        },
        "value": 30
    },
    
    "volatile_concoction": {
        "name": "Volatile Concoction",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "strength_up",
                "duration": 2,
                "magnitude": None
            },
            "damage": 5
        },
        "value": 40
    },

    "sluggish_brew": {
        "name": "Sluggish Brew",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "weakened",
                "duration": 2,
                "magnitude": None
            }
        },
        "value": 25
    },

    "poison_flask": {
        "name": "Poison Flask",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "poison",
                "duration": 3,
                "magnitude": 1
            }
        },
        "value": 30
    },
    "regeneration_draught": {
        "name": "Regeneration Draught",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "effect": {
            "apply_status": {
                    "id": "regen",
                    "duration": 3,
                    "magnitude": 2
            }
        },
        "value": 40
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
    
    "broken_helm": {
        "name": "Broken Helm",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 13
    },

    "tarnished_insignia": {
        "name": "Tarnished Insignia",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 14
    },
    
    "rotted_bone": {
        "name": "Rotted Bone",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 4
    },
    
    "boar_tusk": {
        "name": "Boar Tusk",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 6
    },

    "matted_hide": {
        "name": "Matted Hide",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 15
    },
  
    "hardened_slime_core": {
        "name": "Hardened Slime Core",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 50
    },

    "charred_scale": {
        "name": "Charred Scale",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 140
    },

    "ashen_drake_claw": {
        "name": "Ashen Drake Claw",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 270
    },
}
