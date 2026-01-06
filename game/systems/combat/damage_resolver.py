import random
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from game.core.character import Character

def resolve_damage(actor: 'Character', target: 'Character', damage_def: dict) -> dict:
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
    effective_defence = target.get_effective_defence()

    if raw <= effective_defence:
        # Proportional blocked damage (max 50%, min 0%)
        ratio = max(0.0, min(1.0, (raw * 2 - effective_defence) / raw))
        damage = int(raw * 0.25 * ratio)

        if damage > 0:
            target.take_damage(damage)

        return {
            "damage": damage,
            "blocked": True,
            "critical": critical,
            "died": not target.is_alive(),
        }

    damage = raw - effective_defence
    target.take_damage(damage)

    return {
        "damage": damage,
        "blocked": False,
        "critical": critical,
        "died": not target.is_alive(),
    }
