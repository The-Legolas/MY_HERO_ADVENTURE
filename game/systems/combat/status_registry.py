
STATUS_REGISTRY: dict[str, dict[str, any]] = {


    "weakened": {
        "icon": "⬇",
        "modifiers": {
            "damage_mult": 0.75
        },
        "stacking": "refresh",
        "description": "Reduces damage dealt."
    },

    "stunned": {
        "icon": "💫",
        "prevents_action": True,
        "stacking": "refresh",
        "description": "Cannot act."
    }
}

STATUS_REGISTRY = {
    "poison": {
        "on_tick": lambda target, status: target.take_damage(status.magnitude),
        "stacking": "refresh",   # refresh duration, keep magnitude
        "max_stacks": 1,
        "icon": "☠",
        "prevents_action": False,
    },

    "regen": {
        "on_tick": lambda target, status: setattr(
            target,
            "hp",
            min(target.max_hp, target.hp + status.magnitude)
        ),
        "stacking": "refresh",
        "max_stacks": 1,
        "icon": "✚",
        "prevents_action": False,
    },

    "strength_up": {
        "stacking": "stack",
        "modifiers": {
            "damage_mult": 1.25
        },
        "max_stacks": 3,
        "icon": "⚔",
    },

    "weakened": {
        "stacking": "stack",
        "max_stacks": 2,
        "modifiers": {
            "damage_mult": 0.75
        },
        "icon": "⬇",
    },

    "stun": {
        "stacking": "replace",
        "icon": "💫",
        "prevents_action": True,
    }
}
