
STATUS_REGISTRY = {
    "poison": {
        "priority": 10,
        "icon": "☠",
        "stacking": "refresh",
        "max_stacks": 1,
        "prevents_action": False,
        "description": "Deals damage at the start of each turn.",
        "on_tick": lambda target, status: target.take_damage(status.magnitude),
        "is_debuff": True,
        "interactions": {
            "regen": {
                "description": "Poison damage is reduced while Regen is active.",
                "damage_multiplier": 0.5,
            },
            "bleed": {
                "description": "Poison damage is increased if also Bleeding.",
                "damage_multiplier": 1.4,
            },
        },
    },

    "regen": {
        "priority": 20,
        "icon": "✚",
        "stacking": "refresh",
        "max_stacks": 1,
        "prevents_action": False,
        "description": "Restores health at the start of each turn.",
        "is_debuff": False,
        "on_tick": lambda target, status: setattr(
            target,
            "hp",
            min(target.max_hp, target.hp + status.magnitude),
        ),
    },

    "weakened": {
        "priority": 30,
        "icon": "⚔⬇",
        "stacking": "stack",
        "max_stacks": 5,
        "description": "Reduces outgoing damage.",
        "modifiers": {"damage_mult": 0.75},
        "is_debuff": True,
    },

    "strength_up": {
        "priority": 40,
        "icon": "⚔⬆",
        "stacking": "stack",
        "max_stacks": 5,
        "description": "Increases outgoing damage.",
        "modifiers": {"damage_mult": 1.25},
        "is_debuff": False,
    },

    "stun": {
        "priority": 100,
        "icon": "💫",
        "stacking": "replace",
        "prevents_action": True,
        "description": "Prevents the target from acting.",
        "interrupts": bool,
        "expires_end_of_turn": True,
    },

    "defending": {
        "priority": 90,
        "icon": "🛡",
        "stacking": "replace",
        "max_stacks": 1,
        "prevents_action": False,
        "description": "Raises defense and blocks weak attacks for one turn.",
        "modifiers": {"defence_mult": 2.0},
        "expires_end_of_turn": True,
    },
    "burn": {
        "priority": 15,
        "icon": "🔥",
        "stacking": "refresh",
        "max_stacks": 1,
        "prevents_action": False,
        "description": "Deals percentage-based damage each turn.",
        "on_tick": lambda target, status: target.take_damage(
            max(1, int(target.max_hp * (status.magnitude / 100)))
        ),
        "is_debuff": True,
    },

    "bleed": {
        "priority": 12,
        "icon": "🩸",
        "stacking": "stack",
        "max_stacks": 10,
        "prevents_action": False,
        "description": "Deals minor damage over time. Can stack heavily.",
        "on_tick": lambda target, status: target.take_damage(
            max(1, int(status.magnitude * 0.5))
        ),
        "is_debuff": True,
    },

    "armor_down": {
        "priority": 35,
        "icon": "🛡⬇",
        "stacking": "stack",
        "max_stacks": 5,
        "prevents_action": False,
        "description": "Reduces defense, making the target more vulnerable.",
        "modifiers": {
            "defence_mult": 0.8,
        },
        "is_debuff": True,
    },

}
 
