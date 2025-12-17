
def combat_log_renderer(log: list[dict]) -> str:
    lines: list[str] = []
    lines.append("\n=== BATTLE REPORT ===\n")

    for entry in log:
        event = entry.get("event")

        if event == "encounter_start":
            count = entry.get('enemy_count', 0)
            if count == 1:
                lines.append(f"You are ambushed by {count} enemy.\n")
            else:
                lines.append(f"You are ambushed by {count} enemies.\n")
                             
            continue

        if event == "victory":
            loot = entry.get("loot", {})
            gold = loot.get("gold", 0)
            items = loot.get("items", [])
            lines.append("\nYou are victorious!\n")
            lines.append(f"Gold gained: {gold}")
            if items:
                lines.append("Items gained:")
                for item in items:
                    lines.append(f" - {item.name}")
            lines.append("")
            continue

        if event == "defeat":
            lines.append("\nYou have been defeated.\n")
            continue

        actor = entry.get("actor").title()
        action = entry.get("action")
        target = entry.get("target").title()

        if action == "attack":
            dmg = entry.get("damage", 0)
            crit = entry.get("critical", False)
            blocked = entry.get("blocked", False)
            died = entry.get("died", False)

            text = f"{actor} attacks {target}"
            if blocked:
                text += ", but the blow is blocked."
            else:
                text += f" for {dmg} damage"
                if crit:
                    text += " CRITICAL HIT"
                if died:
                    text += f". {target} is slain."
                else:
                    text += "."
            lines.append(text)
            continue

        if action == "item":
            lines.append(f"{actor} uses an item on {target}.")
            continue

        if action == "flee":
            escaped = entry.get("extra", {}).get("escaped", False)
            if escaped:
                lines.append(f"{actor} successfully flees the battle.")
            else:
                lines.append(f"{actor} tries to flee, but fails.")
            continue

    lines.append("\n=====================\n")
    return "\n".join(lines)