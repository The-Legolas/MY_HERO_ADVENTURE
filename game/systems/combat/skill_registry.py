from typing import Literal

SkillTarget = Literal[
    "self",
    "enemy",
    "all_enemies",
    "random_enemy"
]


class Skill:
    def __init__(self, id: str, name: str, description: str, target: SkillTarget, damage: dict | None = None,
                 hit_chance: float = 1.0, apply_status: dict | None = None,
                 trigger: Literal["immediate", "on_turn_start"] = "immediate", cost: dict | None = None):
        
        self.id = id
        self.name = name
        self.description = description
        self.target = target

        self.damage = damage
        self.hit_chance = hit_chance

        self.apply_status = apply_status
        self.trigger = trigger
        self.cost = cost
"""
dmg types
damage = {
    "type": "flat" | "multiplier" | "hybrid",

    # flat
    "amount": 5,

    # multiplier
    "stat": "damage",
    "mult": 1.2,

    # hybrid
    "base": 3,
    "stat": "damage",
    "mult": 0.6,

    # optional
    "can_crit": True,
}

"""

SKILL_REGISTRY: dict[str, Skill] = {
    "attack": Skill(
        id="attack",
        name="Attack",
        description="A basic weapon attack.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
            "can_crit": True,
        },
        hit_chance=0.95,
    ),

    # PLAYER SKILLS
    "shield_bash": Skill(
        id="shield_bash",
        name="Shield Bash",
        description="A heavy bash that may stun the enemy.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 5,
            "stat": "damage",
            "mult": .7,
        },
        hit_chance=0.85,
        apply_status={
            "id": "stun",
            "duration": 1,
            "magnitude": None,
            "chance": 0.5,
        },
    ),

    "war_cry": Skill(
        id="war_cry",
        name="War Cry",
        description="Bolster your strength for a short time.",
        target="self",
        apply_status={
            "id": "strength_up",
            "duration": 3,
            "magnitude": {"damage_mult": 1.25},
            "chance": 1.0,
        },
    ),

    "power_strike": Skill(
        id="power_strike",
        name="Power Strike",
        description="A heavy blow.",
        target="enemy",
        damage=8,
        hit_chance=0.85
    ),

    "poison_strike": Skill(
        id="poison_strike",
        name="Poison Strike",
        description="A blade coated with poisen.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 3,
            "stat": "damage",
            "mult": 0.5,
            "can_crit": True,
        },
        hit_chance=1.0, #0.9
        apply_status={
            "id": "poison",
            "duration": 3,
            "magnitude": 2,
            "chance": 0.8,
        },
        trigger="on_turn_start",
    ),

    # ENEMY SKILLS
    "poison_bite": Skill(
        id="poison_bite",
        name="Poison Bite",
        description="A vicious bite that injects poison.",
        target="enemy",
        damage=3,
        hit_chance=0.9,
        apply_status={
            "id": "poison",
            "duration": 3,
            "magnitude": 2,
            "chance": 0.8,
        },
    ),
}
