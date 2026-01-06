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
            "mult": 0.70,
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
        hit_chance=0.9,
        cost = {
            "resource": "stamina",
            "amount": 14
        },
        apply_status={
            "id": "poison",
            "duration": 3,
            "magnitude": 2,
            "chance": 1.0,
        },
        trigger="on_turn_start",
    ),

    "sundering_blow": Skill(
        id="sundering_blow",
        name="Sundering Blow",
        description="A brutal strike meant to shatter defenses.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 6,
            "stat": "damage",
            "mult": 0.9,
        },
        hit_chance=0.75,
        cost={"resource": "stamina", "amount": 18},
        apply_status={
            "id": "armor_down",
            "duration": 2,
            "magnitude": None,
            "chance": 1.0,
        },
    ),

    "searing_thrust": Skill(
        id="searing_thrust",
        name="Searing Thrust",
        description="A focused thrust that ignites the target from within.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 4,
            "stat": "damage",
            "mult": 0.95,
        },
        hit_chance=0.95,
        cost={"resource": "stamina", "amount": 10},
        apply_status={
            "id": "burn",
            "duration": 2,
            "magnitude": 6,
            "chance": 1.0,
        },
    ),

    "iron_guard": Skill(
        id="iron_guard",
        name="Iron Guard",
        description="Adopt a hardened stance, ready to absorb blows.",
        target="self",
        cost={"resource": "stamina", "amount": 8},
        apply_status={
            "id": "defending",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
    ),

    "concussive_strike": Skill(
        id="concussive_strike",
        name="Concussive Strike",
        description="A forceful blow aimed to rattle the enemy’s senses.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.95,
        },
        hit_chance=0.85,
        cost={"resource": "stamina", "amount": 14},
        apply_status={
            "id": "stun",
            "duration": 1,
            "magnitude": None,
            "chance": 0.6,
        },
        forbid_if_target_has=["stun"],
    ),

    "exhausting_assault": Skill(
        id="exhausting_assault",
        name="Exhausting Assault",
        description="An aggressive attack that leaves the enemy drained.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 5,
            "stat": "damage",
            "mult": 0.8,
        },
        hit_chance=0.8,
        cost={"resource": "stamina", "amount": 17},
        apply_status={
            "id": "weakened",
            "duration": 4,
            "magnitude": None,
            "chance": 1.0,
        },
    ),

    "rallying_breath": Skill(
        id="rallying_breath",
        name="Rallying Breath",
        description="Draw deep resolve, restoring vitality through discipline.",
        target="self",
        cost={"resource": "stamina", "amount": 15},
        apply_status={
            "id": "regen",
            "duration": 4,
            "magnitude": 8,
            "chance": 1.0,
        },
    ),

    "ultimate_rage": Skill(
        id="ultimate_rage",
        name="Ultimate Rage",
        description="Unleash a powerful rowr, purging weakness and igniting fury, but at the cost of ones own health.",
        target="self",
        cost={"resource": "stamina", "amount": 60},
        effects=[
            {
                "type": "cleanse",
                "except": ["bleed"],
            },
            {
                "type": "apply_status",
                "id": "regen",
                "duration": 4,
                "magnitude": 8,
            },
            {
                "type": "apply_status",
                "id": "strength_up",
                "duration": 6,
                "stacks": "max",
            },
            {
                "type": "apply_status",
                "id": "bleed",
                "duration": 10,
                "magnitude": 8,
            },
        ],
    ),

    # ENEMY SKILLS
    # UNDEAD
    "rotting_claw": Skill(
        id="rotting_claw",
        name="Rotting Claw",
        description="A decayed claw that spreads infection.",
        intent_hint="The undead raises a diseased claw.",
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
        intent_hint="A deathly cold spreads through the air.",
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
        intent_hint="Dark power gathers and will not relent.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 2,
            "stat": "damage",
            "mult": 1.4,
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

    "grave_resilience": Skill(
        id="grave_resilience",
        name="Grave Resilience",
        description="Dark energy knits shattered bones back together.",
        intent_hint="Dark energy reinforces its form.",
        target="self",
        damage=None,
        apply_status={
            "id": "regen",
            "duration": 3,
            "magnitude": 3,
            "chance": 1.0,
        },
        cooldown_turns=4,
    ),

    "withering_touch": Skill(
        id="withering_touch",
        name="Withering Touch",
        description="Necrotic power weakens the target’s defenses.",
        intent_hint="A withering hand reaches out.",
        target="enemy",
        damage=None,
        apply_status={
            "id": "armor_down",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["armor_down"],
    ),

    # HUMANOID
    "dirty_strike": Skill(
        id="dirty_strike",
        name="Dirty Strike",
        description="A cheap attack aimed at weak points, reducing the target's damage.",
        intent_hint="Preparing a vicious strike...",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.7,
            "can_crit": True,
        },
        hit_chance=0.9,
        apply_status={
            "id": "weakened",
            "duration": 2,
            "magnitude": None,
            "chance": 0.4,
        },
        forbid_if_target_has=["weakened"],
    ),

    "battle_shout": Skill(
        id="battle_shout",
        name="Battle Shout",
        description="A rallying cry that boosts strength.",
        intent_hint="Drawing breath for a rallying cry.",
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
        intent_hint="It plants its stance and prepares to endure.",
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

    "bloodletting_slash": Skill(
        id="bloodletting_slash",
        name="Bloodletting Slash",
        description="A vicious cut designed to make the target bleed out.",
        intent_hint="A vicious cut aims to draw blood.",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 4,
            "stat": "damage",
            "mult": 0.7,
            "can_crit": True,
        },
        apply_status={
            "id": "bleed",
            "duration": 5,
            "magnitude": 1,
            "chance": 1.0,
        },
    ),

    "cracking_blow": Skill(
        id="cracking_blow",
        name="Cracking Blow",
        description="A focused strike aimed at armor seams.",
        intent_hint="A focused strike seeking a weak point.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.85,
            "can_crit": True,
        },
        apply_status={
            "id": "armor_down",
            "duration": 2,
            "magnitude": None,
            "chance": 0.5,
        },
    ),

    # OOZE
    "acid_splash": Skill(
        id="acid_splash",
        name="Acid Splash",
        description="Corrosive acid burns through armor.",
        intent_hint="Corrosive fluid spatters outward.",
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

    "dissolve_armor": Skill(
        id="dissolve_armor",
        name="Dissolve Armor",
        description="Acid eats away at protective gear.",
        intent_hint="Corrosive slime spreads over exposed gear.",
        target="enemy",
        damage=None,
        apply_status={
            "id": "armor_down",
            "duration": 4,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["armor_down"],
    ),

    "gelatinous_recovery": Skill(
        id="gelatinous_recovery",
        name="Gelatinous Recovery",
        description="The ooze reforms damaged mass.",
        intent_hint="The ooze thickens and stabilizes.",
        target="self",
        damage=None,
        apply_status={
            "id": "regen",
            "duration": 4,
            "magnitude": 4,
            "chance": 1.0,
        },
        cooldown_turns=5,
    ),

    "engulf": Skill(
        id="engulf",
        name="Engulf",
        description="The ooze engulfs its prey, immobilizing them.",
        intent_hint="Gelatinous mass swells and presses in.",
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
        intent_hint="The ooze churns with rising acidity.",
        target="enemy",
        damage=None,
        apply_status={
            "id": "poison",
            "duration": 4,
            "magnitude": 4,
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
        intent_hint="The beast snaps with a tainted bite.",
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
        intent_hint="Fangs bare in a tearing lunge.",
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
        intent_hint="Muscles tense for...",
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
        intent_hint="The beast throws its head back and roars.",
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

    "tear_flesh": Skill(
        id="tear_flesh",
        name="Tear Flesh",
        description="A savage attack that leaves deep wounds.",
        intent_hint="It aims for a deep wound.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.1,
            "can_crit": True,
        },
        apply_status={
            "id": "bleed",
            "duration": 4,
            "magnitude": 2,
            "chance": 0.7,
        },
    ),

    # DRAGON
    "flame_breath": Skill(
        id="flame_breath",
        name="Flame Breath",
        description="Unleashes a cone of fire dealing heavy damage.",
        intent_hint="The dragon inhales, embers glowing within…",
        target="enemy",
        damage={
            "type": "hybrid",
            "base": 15,
            "stat": "damage",
            "mult": 1.4,
            "can_crit": False,
        },
        hit_chance=1.0,
        apply_status={
            "id": "burn",
            "duration": 3,
            "magnitude": 0.1,
            "chance": 1.0,
        },
        locks_actor={
            "state": "charging",
            "turns": 4,
            "forced_action": None,
        },
        cooldown_turns=8,
    ),

    "terrifying_roar": Skill(
        id="terrifying_roar",
        name="Terrifying Roar",
        description="A roar that crushes the will to fight.",
        intent_hint="Its chest swells as a dreadful roar forms.",
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
        intent_hint="Its wings spread as it lifts from the ground.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.7,
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

    "cataclysmic_slam": Skill(
        id="cataclysmic_slam",
        name="Cataclysmic Slam",
        description="The dragon crashes down with devastating force.",
        intent_hint="The air trembles as it prepares to crash down…",
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

    "molten_scales": Skill(
        id="molten_scales",
        name="Molten Scales",
        description="The dragon’s scales glow with molten heat.",
        intent_hint="Its scales glow with seething heat.",
        target="self",
        damage=None,
        apply_status={
            "id": "defending",
            "duration": 2,
            "magnitude": None,
            "chance": 1.0,
        },
        cooldown_turns=6,
    ),

    "crushing_bite": Skill(
        id="crushing_bite",
        name="Crushing Bite",
        description="The dragon snaps its jaws with bone-crushing force.",
        intent_hint="Rows of teeth close in with crushing force.",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.4,
            "can_crit": True,
        },
        hit_chance=0.9,
    ),

    "raking_talons": Skill(
        id="raking_talons",
        name="Raking Talons",
        description="Razor-sharp claws tear through flesh, leaving deep wounds.",
        intent_hint="Claws rake the air as it draws back…",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
            "can_crit": False,
        },
        apply_status={
            "id": "bleed",
            "duration": 4,
            "magnitude": 2,
            "chance": 0.8,
        },
        forbid_if_target_has=["bleed"],
    ),

    "searing_presence": Skill(
        id="searing_presence",
        name="Searing Presence",
        description="The dragon’s heat weakens nearby defenses.",
        intent_hint="Heat rolls outward, warping the air.",
        target="enemy",
        damage=None,
        apply_status={
            "id": "armor_down",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["armor_down"],
        cooldown_turns=4,
    ),

    "ancient_fury": Skill(
        id="ancient_fury",
        name="Ancient Fury",
        description="The dragon taps into its ancient rage, increasing its power.",
        intent_hint="Ancient rage stirs behind its burning eyes.",
        target="self",
        damage=None,
        apply_status={
            "id": "strength_up",
            "duration": 3,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["strength_up"],
        cooldown_turns=5,
    ),

    "smoldering_regeneration": Skill(
        id="smoldering_regeneration",
        name="Smoldering Regeneration",
        description="Flames knit the dragon’s wounds shut.",
        intent_hint="Firelight pulses through torn flesh.",
        target="self",
        damage=None,
        apply_status={
            "id": "regen",
            "duration": 4,
            "magnitude": 6,
            "chance": 1.0,
        },
        cooldown_turns=6,
    ),

    "inferno_surge": Skill(
        id="inferno_surge",
        name="Inferno Surge",
        description="The dragon gathers fire deep within its chest.",
        intent_hint="Flames churn violently beneath its scales…",
        target="enemy",
        damage={
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.6,
            "can_crit": False,
        },
        apply_status={
            "id": "burn",
            "duration": 4,
            "magnitude": 0.12,
            "chance": 1.0,
        },
        locks_actor={
            "state": "overheating",
            "turns": 2,
            "forced_action": None,
        },
        cooldown_turns=5,
    ),

    "debug": Skill(
        id="debug",
        name="Debug",
        description="A testing attack/status skill",
        intent_hint="Testing Stun",
        target="enemy",
        damage=None,
        hit_chance=1,
        apply_status={
            "id": "stun",
            "duration": 1,
            "magnitude": None,
            "chance": 1.0,
        },
        forbid_if_target_has=["stun"],
        cooldown_turns=0
    ),


}
