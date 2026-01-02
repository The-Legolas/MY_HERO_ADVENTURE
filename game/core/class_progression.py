from game.core.Skill_class import Skill


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
        cost = {
            "resource": "stamina",
            "amount": 10
        },
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
        cost = {
            "resource": "stamina",
            "amount": 15
        },
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
        hit_chance=1.0, #0.9
        cost = {
            "resource": "stamina",
            "amount": 14
        },
        apply_status={
            "id": "poison",
            "duration": 3,
            "magnitude": 2,
            "chance": 1.0, #0.8
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
        intent_hint="missing: shield wall",
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
        intent_hint="missing: acid splash",
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
        intent_hint="missing: engulf",
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
        intent_hint="missing: Corrosive Build-Up",
        target="enemy",
        damage=None,
        apply_status={
            "id": "poison",
            "duration": 4,
            "magnitude": 4, #3
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
        intent_hint="missing: poison_bite",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 3,
            "stat": "damage",
            "mult": 0.9,
            "can_crit": True,
        },
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
        intent_hint="missing: rending_bite",
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
        intent_hint="missing: pounce",
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
        intent_hint="missing: savage_howl",
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
            "turns": 2,
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
            "forced_action": None,
        },
    ),

    "terrifying_roar": Skill(
        id="terrifying_roar",
        name="Terrifying Roar",
        description="A roar that crushes the will to fight.",
        intent_hint="Missing: terrifying_roar",
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
        intent_hint="Missing: skyward_ascension",
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
            "forced_action": None,
        },
        cooldown_turns=6,
    ),
}



CLASS_PROGRESSION = {
    "warrior": {
        "level_cap": 10,
        "xp_curve": "linear",
        "xp_per_level": [
            0,    # level 1
            100,  # level 2
            200,
            300,
            400,
            500,
            600,
            700,
            800,
            900,
            1000,  # level 10
        ],
        "level_rewards": {

            2: {
                "stats": {"hp": +10, "damage": +2},
            },
            3: {
                "stats": {"hp": +10, "damage": +2},
                "skills": ["shield_bash"],
            },
            4: {
                "stats": {"defence": +1},
            },
            6: {
                "skills": ["war_cry"],
            },
        },
    },
}
