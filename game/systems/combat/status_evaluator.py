from game.systems.combat.status_registry import STATUS_REGISTRY

def evaluate_status_magnitude(status, active_statuses) -> float:
    
    value = status.magnitude
    data = STATUS_REGISTRY.get(status.id, {})
    interactions = data.get("interactions", {})

    for other in active_statuses:
        rule = interactions.get(other.id)
        if not rule:
            continue

        multiplier = rule.get("damage_multiplier")
        if multiplier is not None:
            value *= multiplier

    return value
