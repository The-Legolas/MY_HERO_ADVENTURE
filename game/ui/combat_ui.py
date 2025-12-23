from game.systems.combat.status_registry import STATUS_REGISTRY


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
