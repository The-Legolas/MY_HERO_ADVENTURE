from game.systems.combat.status_registry import STATUS_REGISTRY

def format_status_icons(entity) -> str:
    if not entity.statuses:
        return ""

    icons = []
    for status in entity.statuses:
        data = STATUS_REGISTRY.get(status.id, {})
        icon = data.get("icon", "?")
        icons.append(f"{icon} {status.remaining_turns}")

    return " ".join(icons)
