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
                 trigger: Literal["immediate", "on_turn_start"] = "immediate", cost: dict | None = None,
                 forbid_if_target_has: list[str] = None, cooldown_turns: int = None, locks_actor: dict[str, str|int] = None,
                 allowed_while_locked: bool = None, requires_target_alive: bool = None):
        
        self.id = id
        self.name = name
        self.description = description
        self.target = target

        self.damage = damage
        self.hit_chance = hit_chance

        self.apply_status = apply_status
        self.trigger = trigger
        self.cost = cost

        self.forbid_if_target_has = forbid_if_target_has or []
        self.cooldown_turns = cooldown_turns
        self.locks_actor = locks_actor
        self.allowed_while_locked = allowed_while_locked if allowed_while_locked is not None else False
        self.requires_target_alive = requires_target_alive if requires_target_alive is not None else True
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
        forbid_if_target_has=["stun"],
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
        hit_chance=0.9, #0.9
        apply_status={
            "id": "poison",
            "duration": 3,
            "magnitude": 2,
            "chance": 0.8,
        },
        trigger="on_turn_start",
    ),

    # ENEMY SKILLS
    # UNDEAD
    "rotting_claw": Skill(
        id="rotting_claw",
        name="Rotting Claw",
        description="A decayed claw that spreads infection.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.8,
            "can_crit": False,
        },
        apply_status={
            "id": "poison",
            "duration": 3,
            "magnitude": 2,
            "chance": 0.5,
        },
        forbid_if_target_has=["poison"],
    ),

    "grave_chill": Skill(
        id="grave_chill",
        name="Grave Chill",
        description="A freezing aura that saps strength.",
        target="enemy",
        damage=None,
        hit_chance=0.85,
        apply_status={
            "id": "weakened",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["weakened"],
    ),

    "death_coil": Skill(
        id="death_coil",
        name="Death Coil",
        description="The undead gathers necrotic energy into a dark spiral.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 2,
            "stat": "damage",
            "mult": 0.8,
            "can_crit": False,
        },
        hit_chance=1.0,
        locks_actor={
            "state": "channeling",
            "turns": 2,
            "forced_action": "skill",
        },
        cooldown_turns=4,
    ),


    # HUMANOID
    "dirty_strike": Skill(
        id="dirty_strike",
        name="Dirty Strike",
        description="A cheap attack aimed at weak points, reducing the target's damage.",
        intent_hint="Preparing a vicious strike",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.7, #0.7
            "can_crit": True,
        },
        hit_chance=0.9,
        apply_status={
            "id": "weakened",
            "duration": 2,
            "magnitude": None,
            "chance": 0.4, #0.4
        },
        forbid_if_target_has=["weakened"],
    ),

    "battle_shout": Skill(
        id="battle_shout",
        name="Battle Shout",
        description="A rallying cry that boosts strength.",
        intent_hint="Drawing breath for a rallying cry",
        target="self",
        damage=None,
        apply_status={
            "id": "strength_up",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["strength_up"],
        cooldown_turns=4
    ),
  
    "shield_wall": Skill(
        id="shield_wall",
        name="Shield Wall",
        description="The enemy braces behind its shield.",
        target="self",
        damage=None,
        apply_status={
            "id": "defending",
            "duration": 2,
            "magnitude": None,
            "chance": 1.0,
        },
        locks_actor={
            "state": "bracing",
            "turns": 2,
            "forced_action": None,
        },
        cooldown_turns=5,
    ),


    # OOZE
    "acid_splash": Skill(
        id="acid_splash",
        name="Acid Splash",
        description="Corrosive acid burns through armor.",
        target="enemy",
        damage={
            "type": "flat",
            "amount": 4,
            "can_crit": False,
        },
        apply_status={
            "id": "weakened",
            "duration": 2,
            "magnitude": None,
            "chance": 0.5,
        },
        forbid_if_target_has=["weakened"],
    ),

    "engulf": Skill(
        id="engulf",
        name="Engulf",
        description="The ooze engulfs its prey, immobilizing them.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.5,
            "can_crit": False,
        },
        hit_chance=0.75,
        apply_status={
            "id": "stun",
            "duration": 1,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["stun"],
        cooldown_turns=3
    ),

    "corrosive_buildup": Skill(
        id="corrosive_buildup",
        name="Corrosive Build-Up",
        description="The ooze thickens with burning acid.",
        target="enemy",
        damage=None,
        apply_status={
            "id": "poison",
            "duration": 4,
            "magnitude": 3,
            "chance": 1.0,
        },
        locks_actor={
            "state": "seething",
            "turns": 2,
            "forced_action": None,
        },
        cooldown_turns=4,
    ),


    # BEAST
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
        forbid_if_target_has=["poison"],
    ),

    "rending_bite": Skill(
        id="rending_bite",
        name="Rending Bite",
        description="A vicious bite that tears flesh.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
            "can_crit": True,
        },
    ),

    "pounce": Skill(
        id="pounce",
        name="Pounce",
        description="A sudden leap that overwhelms the target.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.2,
            "can_crit": True,
        },
        hit_chance=0.85,
        apply_status={
            "id": "stun",
            "duration": 1,
            "magnitude": None,
            "chance": 0.4,
        },
        forbid_if_target_has=["stun"],
        cooldown_turns=3
    ),

    "savage_howl": Skill(
        id="savage_howl",
        name="Savage Howl",
        description="The beast howls, stirring its bloodlust.",
        target="self",
        damage=None,
        apply_status={
            "id": "strength_up",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        locks_actor={
            "state": "howling",
            "turns": 1,
            "forced_action": None,
        },
        cooldown_turns=3,
    ),

    
    # DRAGON
    "flame_breath": Skill(
        id="flame_breath",
        name="Flame Breath",
        description="Unleashes a cone of fire dealing heavy damage.",
        intent_hint="Inhales deeply...",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 5,
            "stat": "damage",
            "mult": 1.25,
            "can_crit": False,
        },
        hit_chance=1.0,
        locks_actor={
            "state": "charging",
            "turns": 2,
            "forced_action": "attack",
        },
    ),

    "terrifying_roar": Skill(
        id="terrifying_roar",
        name="Terrifying Roar",
        description="A roar that crushes the will to fight.",
        target="enemy",
        damage=None,
        apply_status={
            "id": "weakened",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["weakened"],
    ),

    "skyward_ascension": Skill(
        id="skyward_ascension",
        name="Skyward Ascension",
        description="The dragon takes to the air, preparing a deadly dive.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 2.0,
            "can_crit": False,
        },
        hit_chance=1.0,
        locks_actor={
            "state": "airborne",
            "turns": 2,
            "forced_action": "attack",
        },
        cooldown_turns=6,
    ),
}

