def combat_log_renderer(log: list[dict]) -> str:
    lines: list[str] = []
    lines.append("\n=== BATTLE REPORT ===\n")

    for entry in log:
        event = entry.get("event")
        action = entry.get("action")

        actor = entry.get("actor", "Unknown")
        target = entry.get("target", "Unknown")

        match event:
            case "encounter_start":
                count = entry.get("enemy_count", 0)
                enemy_word = "enemy" if count == 1 else "enemies"
                lines.append(f"You are ambushed by {count} {enemy_word}.\n")
                continue

            case "victory":
                loot = entry.get("loot", {})
                gold = loot.get("gold", 0)
                items = loot.get("items", [])

                lines.append("\nYou are victorious!\n")
                lines.append(f"Gold gained: {gold}")

                if items:
                    lines.append("Items gained:")
                    for item in items:
                        lines.append(f" - {item.name}")
                continue

            case "defeat":
                lines.append("\nYou have been defeated.\n")
                continue

            case "status_applied":
                lines.append(
                    f"{entry['target']} is afflicted with {entry['status']}!"
                )
                continue

            case "status_resisted":
                lines.append(
                    f"{entry['target']} resisted {entry['status']}."
                )
                continue

            case "status_tick":
                if "damage" in entry:
                    lines.append(
                        f"{entry['target']} takes {entry['damage']} damage from {entry['status']}."
                    )
                elif "heal" in entry:
                    lines.append(
                        f"{entry['target']} recovers {entry['heal']} HP from {entry['status']}."
                    )
                continue

            case "status_expire":
                lines.append(
                    f"{entry['status']} on {entry['target']} wears off."
                )
                continue

            case "status_prevented_action":
                lines.append(
                    f"{entry['target']} is stunned and cannot act!"
                )
                continue

            case _:
                pass  


        match action:
            case "attack":
                dmg = entry.get("damage", 0)
                blocked = entry.get("blocked", False)
                crit = entry.get("critical", False)
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

            case "item":
                lines.append(f"{actor} uses an item on {target}.")
                continue

            case "flee":
                escaped = entry.get("extra", {}).get("escaped", False)
                if escaped:
                    lines.append(f"{actor} successfully flees the battle.")
                else:
                    lines.append(f"{actor} tries to flee, but fails.")
                continue

            case _:
                pass

    lines.append("\n=====================\n")
    return "\n".join(lines)
