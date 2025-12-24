import random
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from game.core.Character_class import Character

def resolve_damage(actor: 'Character', target: 'Character', damage_def: dict) -> dict:
    """
    Final authoritative damage resolver.
    All combat damage MUST go through here.
    """

    if not target or not damage_def:
        return {
            "damage": 0,
            "blocked": False,
            "critical": False,
            "died": False,
        }

    # --- Step 1: Compute raw damage ---
    raw = 0

    dmg_type = damage_def["type"]

    if dmg_type == "flat":
        raw = damage_def["amount"]

    elif dmg_type == "multiplier":
        stat_val = getattr(actor, damage_def["stat"], 0)
        raw = int(stat_val * damage_def["mult"])

    elif dmg_type == "hybrid":
        stat_val = getattr(actor, damage_def["stat"], 0)
        raw = int(damage_def["base"] + stat_val * damage_def["mult"])

    # --- Step 2: Status modifiers ---
    raw = int(raw * actor.get_damage_multiplier())

    # --- Step 3: Critical ---
    critical = False
    if damage_def.get("can_crit", True):
        if random.random() >= 0.95:
            raw *= 2
            critical = True

    # --- Step 4: Defense ---
    if raw <= target.defence:
        return {
            "damage": 0,
            "blocked": True,
            "critical": critical,
            "died": False,
        }

    damage = raw - target.defence
    target.take_damage(damage)

    return {
        "damage": damage,
        "blocked": False,
        "critical": critical,
        "died": not target.is_alive(),
    }
