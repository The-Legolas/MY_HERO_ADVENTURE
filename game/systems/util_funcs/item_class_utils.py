from game.core.Status import Status

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


EFFECT_ACTIONS = {
    "heal": apply_heal,
    "damage": apply_damage,
    "apply_status": apply_status_effect,
    "remove_status": apply_remove_status,
}

