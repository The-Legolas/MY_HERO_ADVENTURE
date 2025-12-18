
def combat_log_renderer(log: list[dict]) -> str:
    lines: list[str] = []
    lines.append("\n=== BATTLE REPORT ===\n")

    for entry in log:
        event = entry.get("event")
        if not event:
            continue
        
        action = entry.get("action")
        actor = entry.get("actor", "Unknown").title()
        target = entry.get("target", "Unknown").title()

        if event == "encounter_start":
            count = entry.get('enemy_count', 0)
            enemy_word = "enemy" if count == 1 else "enemies"
            lines.append(f"You are ambushed by {count} {enemy_word}.\n")             
            continue

        elif event == "victory":
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

        elif event == "defeat":
            lines.append("\nYou have been defeated.\n")
            continue

        
        elif event == "status_applied":
            target = entry.get("target", "Unknown").title()
            status = entry.get("status", "unknown")
            lines.append(f"{target} is afflicted with {status}!")

        elif event == "status_tick":
            status = entry.get("status", "Unknown").title()
            target = entry.get("target", "Unknown").title()
            if "damage" in entry:
                lines.append(f"{status} deals {entry['damage']} damage to {target}.")
            elif "heal" in entry:
                lines.append(f"{status} heals {target} for {entry['heal']} HP.")

        elif event == "status_expire":
            status = entry.get("status", "Unknown").title()
            target = entry.get("target", "Unknown").title()
            lines.append(f"{status} on {target} wears off.")

        elif event == "status_prevented_action":
            target = entry.get("target", "Unknown").title()
            lines.append(f"{target} is stunned and cannot act!")
    
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

        elif action == "item":
            lines.append(f"{actor} uses an item on {target}.")
            continue

        elif action == "flee":
            escaped = entry.get("extra", {}).get("escaped", False)
            if escaped:
                lines.append(f"{actor} successfully flees the battle.")
            else:
                lines.append(f"{actor} tries to flee, but fails.")
            continue

    lines.append("\n=====================\n")
    return "\n".join(lines)