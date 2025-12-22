
STATUS_REGISTRY = {
    "poison": {
        "priority": 10,
        "icon": "☠",
        "stacking": "refresh",
        "max_stacks": 1,
        "prevents_action": False,
        "description": "Deals damage at the start of each turn.",
        "on_tick": lambda target, status: target.take_damage(status.magnitude),
        "interactions": {
            "regen": {
                "description": "Poison damage is reduced while Regen is active.",
                "damage_multiplier": 0.5,
            },
            "bloodletting": {
                "description": "Poison damage is increased if also using Bloodletting.",
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
        "on_tick": lambda target, status: setattr(
            target,
            "hp",
            min(target.max_hp, target.hp + status.magnitude),
        ),
    },

    "weakened": {
        "priority": 30,
        "icon": "⬇",
        "stacking": "stack",
        "max_stacks": 5,
        "description": "Reduces outgoing damage.",
        "modifiers": {"damage_mult": 0.75},
    },

    "strength_up": {
        "priority": 40,
        "icon": "⚔",
        "stacking": "stack",
        "max_stacks": 5,
        "description": "Increases outgoing damage.",
        "modifiers": {"damage_mult": 1.25},
    },

    "stun": {
        "priority": 100,
        "icon": "💫",
        "stacking": "replace",
        "prevents_action": True,
        "description": "Prevents the target from acting.",
    },
}

