from game.definitions.status_registry import STATUS_REGISTRY
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
                for k, v in mag.items():
                    lines.append(f"Effect strength: {k} = {v}")

        else:
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

        if status.remaining_turns > 0:
            icons.append(f"{icon} {status.remaining_turns}")
        elif status.remaining_turns == 0:
            pass
        else:
            icons.append(f"{icon}")

    return " ".join(icons)

def describe_status_compact(status: Status) -> str:
    data = STATUS_REGISTRY.get(status.id, {})
    icon = data.get("icon", "")
    name = status.id.replace("_", " ").title()
    turns = status.remaining_turns

    if turns is not None:
        return f"{icon} {name}: {turns} turns"
    return f"{icon} {name}"

def sort_statuses_by_priority(statuses: list[Status]) -> list[Status]:
    return sorted(
        statuses,
        key=lambda s: STATUS_REGISTRY.get(s.id, {}).get("priority", 0),
        reverse=True
    )

def inspect_entity_statuses(entity):
    statuses = sort_statuses_by_priority(entity.statuses)
    if not statuses:
        print("\nNo active statuses.")
        input("\nPress Enter to continue...")
        return
    while True:
        print()
        for i, s in enumerate(statuses, start=1):
            print(f"{i}. {s.id.replace('_', ' ').title()}")
        print("c. Cancel")

        choice = input("> ").strip().lower()

        if not choice.isdigit():
            return

        idx = int(choice) - 1
        if not (0 <= idx < len(statuses)):
            continue

        status = statuses[idx]

        print()
        for line in render_status_tooltip(status, entity):
            print(line)

        print("-" * 30)
        input("\nPress Enter to continue...")
