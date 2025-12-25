
def combat_log_renderer(log: list[dict]) -> str:
    lines: list[str] = []
    lines.append("\n=== BATTLE REPORT ===\n")

    current_turn = None
    start_phase = []
    action_phase = []
    post_action_phase = []

    def flush_turn():
        for line in start_phase:
            lines.append(line)
        for line in action_phase:
            lines.append(line)
        for line in post_action_phase:
            lines.append(line)

    for entry in log:
        event = entry.get("event")
        action = entry.get("action")

        actor = entry.get("actor", "Unknown")
        target = entry.get("target", "Unknown")


        if event == "turn_start":
            if current_turn is not None:
                flush_turn()
                start_phase.clear()
                action_phase.clear()
                post_action_phase.clear()

            current_turn = entry["turn"]
            lines.append(f"\n--- Turn {current_turn} ---")
            continue


        if event == "encounter_start":
            count = entry.get("enemy_count", 0)
            enemy_word = "enemy" if count == 1 else "enemies"
            lines.append(f"You are ambushed by {count} {enemy_word}.\n")
            continue
        
        if event == "victory":
            flush_turn()
            start_phase.clear()
            action_phase.clear()
            post_action_phase.clear()
            
            lines.append("\n--- You are victorious! ---")
            loot = entry.get("loot", {})
            if loot.get("gold"):
                lines.append(f"Gold gained: {loot['gold']}")
            if loot.get("items"):
                lines.append("Items gained:")
                for item in loot["items"]:
                    lines.append(f" - {item.name}")

            lines.append("\n=====================\n")
            return "\n".join(lines)

        if event == "defeat":
            flush_turn()
            
            return "\n".join(lines + ["\nYou have been defeated."])

        if event == "status_tick":
            status = entry.get("status", "").replace("_", " ").title()
            before = entry.get("hp_before")
            after = entry.get("hp_after")

            if before is not None and after is not None:
                delta = before - after
                if delta > 0:
                    start_phase.append(
                        f"{entry['target']} takes {delta} damage from {status}."
                    )
                elif delta < 0:
                    start_phase.append(
                        f"{entry['target']} recovers {-delta} HP from {status}."
                    )
            continue

        if event == "status_expired":
            status = entry.get("status", "").replace("_", " ").title()
            start_phase.append(f"{status} on {entry['target']} wears off.")
            continue

        if event == "status_applied":
            status = entry.get("status", "").replace("_", " ").title()
            post_action_phase.append(f"{entry['target']} is afflicted with {status}.")
            continue
        
        if event == "interrupt":
            status = entry["status"].replace("_", " ").title()
            state = entry.get("interrupted_state", "action")

            post_action_phase.append(
                f"{entry['target']}'s {state} is interrupted by {status}!"
            )
            continue

        if event == "status_prevented_action":
            action_phase.append(f"{entry['target']} is unable to act!")
            continue

        if event == "status_interaction":
            status = entry["status"].replace("_", " ").title()
            source = entry["source"].replace("_", " ").title()
            mult = entry["multiplier"]

            if mult < 1:
                lines.append(
                    f"{status} is weakened by {source}."
                )
            else:
                lines.append(
                    f"{status} is amplified by {source}."
                )
            continue

        if event == "status_resisted":
            status = entry.get("status", "").replace("_", " ").title()
            skill = entry.get("skill")

            if skill:
                skill_name = skill.replace("_", " ").title()
                post_action_phase.append(
                    f"{entry['target']}'s {skill_name} is interrupted by {status}!"
                )
            else:
                post_action_phase.append(
                    f"{entry['target']}'s action is interrupted by {status}!"
                )
            continue

        if event == "interrupt_resisted":
            status = entry["status"].replace("_", " ").title()
            state = entry.get("state", "action")

            post_action_phase.append(
                f"{entry['target']} resists the interruption and continues {state}!"
            )
            continue

        if event == "wait":
            action_phase.append(f"{entry['actor']} is gathering power.")
            continue


        if event == "death":
            post_action_phase.append(f"{entry['target']} collapses.")
            continue


        if action == "attack":
            dmg = entry.get("damage", 0)
            blocked = entry.get("blocked", False)
            crit = entry.get("critical", False)
            died = entry.get("died", False)

            if blocked:
                action_phase.append(f"{actor} attacks {target}, but the blow is blocked.")
            else:
                text = f"{actor} strikes {target} for {dmg} damage"
                if crit:
                    text += " (CRITICAL HIT)"
                action_phase.append(text + ".")

                if died:
                    post_action_phase.append(f"{target} is slain.")
            continue

        if action == "skill":
            skill_id = entry.get("extra", {}).get("skill", "unknown_skill")
            skill_name = skill_id.replace("_", " ").title()
            dmg = entry.get("damage", 0)
            blocked = entry.get("blocked", False)
            died = entry.get("died", False)

            if blocked:
                action_phase.append(f"{target} blocks the attack with a defensive stance.")

                action_phase.append(
                    f"{actor} uses {skill_name} on {target}, but it is blocked."
                )
            else:
                text = f"{actor} uses {skill_name}"
                if target:
                    text += f" on {target}"
                if dmg > 0:
                    text += f" for {dmg} damage"
                text += "."
                action_phase.append(text)

                if died:
                    post_action_phase.append(f"{target} is slain.")

            continue

        if action == "defend":
            action_phase.append(f"{actor} takes a defensive stance.")


        if action == "item":
            action_phase.append(f"{actor} uses an item on {target}.")
            continue

        if action == "flee":
            escaped = entry.get("extra", {}).get("escaped", False)
            if escaped:
                action_phase.append(f"{actor} successfully flees the battle.")
            else:
                action_phase.append(f"{actor} tries to flee, but fails.")
            continue

    
    flush_turn()
    lines.append("\n=====================\n")
    return "\n".join(lines)
