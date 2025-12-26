from game.systems.combat.status_registry import STATUS_REGISTRY
from game.core.Status import Status

def render_status_tooltip(status, entity) -> list[str]:
    data = STATUS_REGISTRY.get(status.id, {})
    lines = []

    name = status.id.replace("_", " ").title()
    lines.append(name)

    if "description" in data:
        lines.append(data["description"])

    if status.magnitude is not None:
        mag = status.magnitude

        if isinstance(mag, dict):
            if "damage_mult" in mag:
                lines.append(f"Effect strength: x{mag['damage_mult']} damage")
            else:
                # Fallback for future structured magnitudes
                for k, v in mag.items():
                    lines.append(f"Effect strength: {k} = {v}")

        else:
            # Scalar magnitude (poison, regen, etc.)
            lines.append(f"Effect strength: {mag}")

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

def format_status_icons(entity) -> str:
    if not entity.statuses:
        return ""

    by_id = {}

    for status in entity.statuses:
        existing = by_id.get(status.id)

        if not existing:
            by_id[status.id] = status
        else:
            if status.remaining_turns > existing.remaining_turns:
                by_id[status.id] = status

    ordered = sorted(
        by_id.values(),
        key=lambda s: STATUS_REGISTRY.get(s.id, {}).get("priority", 50)
    )

    icons = []
    for status in ordered:
        data = STATUS_REGISTRY.get(status.id, {})
        icon = data.get("icon", "?")

        if status.remaining_turns >= 0:
            icons.append(f"{icon} {status.remaining_turns}")
        else:
            icons.append(f"{icon}")

    return " ".join(icons)

def describe_status(status: Status) -> str:
    name = status.id.replace("_", " ").title()
    turns = status.remaining_turns

    data = STATUS_REGISTRY.get(status.id, {})
    desc = data.get("description")

    if desc:
        return f"{name}: {desc} ({turns} turns)"
    return f"{name} ({turns} turns)"
