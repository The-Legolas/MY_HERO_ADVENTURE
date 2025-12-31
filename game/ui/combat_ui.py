
def render_victory_summary(entry: dict) -> list[str]:
    lines = []
    lines.append("\n--- You are victorious! ---")

    xp = entry.get("xp", 0)
    if xp:
        lines.append(f"XP gained: {xp}")

    loot = entry.get("loot", {})
    gold = loot.get("gold", 0)
    if gold:
        lines.append(f"Gold gained: {gold}")

    items = loot.get("items", [])
    if items:
        lines.append("Items gained:")
        for item in items:
            lines.append(f" - {item.name}")

    return lines
