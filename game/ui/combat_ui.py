from game.systems.combat.status_registry import STATUS_REGISTRY
from collections import defaultdict

def format_status_icons(entity) -> str:
    if not entity.statuses:
        return ""

    counts = defaultdict(int)

    for status in entity.statuses:
        counts[status.id] += status.magnitude if isinstance(status.magnitude, int) else 1

    ordered = sorted(
        counts.items(),
        key=lambda item: STATUS_REGISTRY.get(item[0], {}).get("priority", 50)
    )

    icons = []
    for status_id, total in ordered:
        icon = STATUS_REGISTRY.get(status_id, {}).get("icon", "?")
        icons.append(f"{icon} {total}")

    return " ".join(icons)
