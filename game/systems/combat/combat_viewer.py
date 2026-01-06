from game.ui.combat_text_helpers import describe_attack, describe_skill, describe_wait
from game.ui.combat_ui import render_victory_summary

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
            
            lines.extend(render_victory_summary(entry))
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

        if action == "wait":
            action_phase.append(
                f"{entry['actor']} {describe_wait(entry.get('extra', {}))}."
            )
            continue
        
        if event == "status_immune":
            status = entry["status"].replace("_", " ").title()
            post_action_phase.append(
                f"{entry['target']} is immune to {status}."
            )
            continue
            
        if event == "status_exploited":
            status = entry["status"].replace("_", " ").title()
            post_action_phase.append(
                f"{status} hits especially hard!"
            )
            continue

        if event == "status_weakened":
            status = entry["status"].replace("_", " ").title()
            post_action_phase.append(
                f"{status} has reduced effect."
            )
            continue

        if event == "death":
            post_action_phase.append(f"{entry['target']} collapses.")
            continue

        if event == "item":
            outcome = entry["outcome"]
            item = outcome["extra"]["item"]
            actor = entry["actor"]
            target = entry["target"]

            lines.append(f"{actor} uses {item} on {target}.")

            for d in outcome["extra"]["details"]:
                if d["effect"] == "heal":
                    lines.append(f"{target} recovers {d['amount']} HP.")
                elif d["effect"] == "damage":
                    lines.append(f"{target} takes {d['amount']} damage.")
                elif d["effect"] == "apply_status":
                    status = d["status"].replace("_", " ").title()
                    if d["applied"]:
                        lines.append(f"{target} is afflicted with {status}.")
                    else:
                        lines.append(f"{status} has no effect on {target}.")



        if action == "attack":
            dmg = entry.get("damage", 0)
            blocked = entry.get("blocked", False)
            crit = entry.get("critical", False)
            died = entry.get("died", False)

            action_phase.append(
                describe_attack(actor, target, dmg, blocked, crit)
            )

            if died:
                post_action_phase.append(f"{target} is slain.")
            continue

        if action == "skill":
            dmg = entry.get("damage", 0)
            blocked = entry.get("blocked", False)
            died = entry.get("died", False)

            action_phase.append(
                describe_skill(actor, target, entry.get("extra", {}), dmg, blocked)
            )

            if died:
                post_action_phase.append(f"{target} is slain.")
            continue

        if action == "defend":
            action_phase.append(f"{actor} takes a defensive stance.")
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

def render_combat_outcome(outcome: dict):
    if not outcome:
        return
    
    action = outcome.get("action")
    actor = outcome.get("actor")
    target = outcome.get("target")

    damage = outcome.get("damage", 0)
    blocked = outcome.get("blocked", False)
    critical = outcome.get("critical", False)
    died = outcome.get("died", False)
    extra = outcome.get("extra", {})

    if action == "attack":
        print(describe_attack(actor, target, damage, blocked, critical))
        if died:
            print(f"{target} has been slain!")

    elif action == "skill":
        print(describe_skill(actor, target, extra, damage, blocked))
        if died:
            print(f"{target} has been slain!")

    elif action == "defend":
        print(f"{actor} braces for impact, raising their defenses.")

    elif action == "use_item":
        item = extra.get("item", "item")
        details = extra.get("details", [])

        print(f"{actor} uses {item}.")

        for d in details:
            effect = d.get("effect")

            if effect == "heal":
                print(f"{target} recovers {d['amount']} HP.")
            elif effect == "damage":
                print(f"{target} takes {d['amount']} damage.")
            elif effect == "apply_status":
                status = d["status"].replace("_", " ").title()
                if d.get("applied"):
                    print(f"{target} is affected by {status}.")
                else:
                    print(f"{target} is not affected by {status}.")
            elif effect == "remove_status":
                status = d["status"].replace("_", " ").title()
                if d.get("success"):
                    print(f"{status} is removed.")
                else:
                    print(f"{target} had no {status}.")


    elif action == "wait":
        reason = extra.get("reason")

        if reason == "stunned":
            print(f"{actor} is stunned and cannot act.")

            intent = extra.get("enemy_intent")
            if intent:
                print(f"The enemy is preparing to act: {intent}")

        elif reason == "overheating":
            print(f"{actor} is overheated and must recover.")
            print("Flames subside as it gathers itself.")

        else:
            print(f"{actor} waits.")

    elif action == "flee":
        if extra.get("escaped"):
            print(f"{actor} successfully fled!")
        else:
            print(f"{actor} failed to flee!")
    
    feedback = outcome.get("status_feedback")
    if feedback:
        status = feedback["status"].replace("_", " ").title()
        result = feedback["result"]

        if result == "immune":
            print(f"{target} is immune to {status}.")
        elif result == "resisted":
            print(f"{target} resists the effects of {status}.")
        elif result == "vulnerable":
            print(f"{status} takes hold more strongly!")
        elif result == "resistant":
            print(f"{status} has reduced effect on {target}.")

    print()  # spacing only
