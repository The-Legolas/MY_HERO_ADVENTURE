from game.systems.combat.status_registry import STATUS_REGISTRY

def render_status_tooltip(status, entity) -> list[str]:
    data = STATUS_REGISTRY.get(status.id, {})
    lines = []

    name = status.id.replace("_", " ").title()
    lines.append(name)

    if "description" in data:
        lines.append(data["description"])

    if status.magnitude is not None:
        lines.append(f"Effect strength: {status.magnitude}")

    if status.remaining_turns >= 0:
        lines.append(f"Turns remaining: {status.remaining_turns}")
    else:
        lines.append("Duration: While equipped")

    interactions = data.get("interactions", {})
    if interactions:
        lines.append("Interactions:")
        for other_status, rule in interactions.items():
            lines.append(f" - {rule['description']}")

    return lines
