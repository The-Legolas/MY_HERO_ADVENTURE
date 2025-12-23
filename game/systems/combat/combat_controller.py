from game.systems.combat.combat_turn import _get_initiative_value
from game.core.Character_class import Character
from game.core.Enemy_class import Enemy
from game.world.Dungeon_room_code import Room
from game.core.Item_class import roll_loot
from game.systems.combat.combat_actions import Action, resolve_action, _choose_consumable_from_inventory, _choose_enemy_target
from game.ui.combat_ui import format_status_icons
import random
from typing import Optional
from game.core.Status import Status
from game.ui.status_ui import render_status_tooltip
from game.systems.combat.status_registry import STATUS_REGISTRY
from game.systems.combat.skill_registry import SKILL_REGISTRY

class Combat_State():
    def __init__(self, player: Character, enemy_list: list[Enemy]):
        self.player: Character = player
        self.enemy_list: list[Enemy] = enemy_list
        self.round_number: int = 1
        self.log: list[dict[str, any]] = []
        self.is_running: bool = True

    def alive_enemies(self) -> list[Enemy]:
        return [enemy for enemy in self.enemy_list if enemy.is_alive()]

def show_combat_status(combat: Combat_State):
    player = combat.player
    icons = format_status_icons(player)

    print("\n=== COMBAT STATUS ===")
    print(f"You: {player.hp}/{player.max_hp} HP {icons}")
    for i, e in enumerate(combat.alive_enemies(), start=1):
        icons = format_status_icons(e)
        print(f"{i}. {e.name} ({e.hp}/{e.max_hp} HP) {icons}")
            
    print("=====================\n")



def start_encounter(player: Character, room: Room) -> dict[str, any]:
    enemy_list = list(room.contents.get("enemies", []))

    combat_state = Combat_State(player, enemy_list)
    combat_state.is_running = True
    combat_state.log.append({"event": "encounter_start", "player": player.name, "enemy_count": len(enemy_list)})

    if not enemy_list:
        return {"result": "no_enemies", "log": combat_state.log}

    while combat_state.is_running:
        participants = [player] + combat_state.alive_enemies()
        participants_sorted = sorted(participants, key=_get_initiative_value, reverse=True)

        combat_state.log.append({
            "event": "turn_start",
            "turn": combat_state.round_number
        })


        for actor in participants_sorted:
            if not combat_state.is_running:
                break

            if not actor.is_alive():
                continue

            turn_effects = actor.get_on_turn_effects()

            for effect in turn_effects:
                if random.random() > effect.get("chance", 1.0):
                    continue

                status_data = effect.get("status")
                if not status_data:
                    continue

                status = Status(
                    id=status_data["id"],
                    remaining_turns=status_data["duration"],
                    magnitude=status_data.get("magnitude", 1),
                    source=actor.name,
                )

                actor.apply_status(status, combat_state.log)


            status_logs = actor.process_statuses()
            combat_state.log.extend(status_logs)

            if not combat_state.alive_enemies():
                killed = [enemy for enemy in enemy_list if not enemy.is_alive()]
                total_loot = {"gold": 0, "items": []}
                for dead in killed:
                    loot = roll_loot(dead)
                    total_loot["gold"] += loot.get("gold", 0)

                    xp_gain = 0
                    for item in loot.get("items", []):
                        total_loot["items"].append(item)
                        player.add_item(item)
                        xp_gain += getattr(dead, "xp_reward", 0)

                    player.xp = getattr(player, "xp", 0) + xp_gain
                
                combat_state.log.append({"event": "victory", "loot": total_loot})
                combat_state.is_running = False
                return {"result": "victory", "log": combat_state.log, "loot": total_loot}


            if not actor.is_alive():
                combat_state.log.append({
                    "event": "death",
                    "target": actor.name,
                    "cause": "status"
                })
                continue

            if not actor.can_act():
                combat_state.log.append({
                    "event": "status_prevented_action",
                    "target": actor.name
                })
                continue

            if actor is combat_state.player:
                action = ask_player_for_action(actor, combat_state)
                if action is None:
                    continue

            else:
                action = decide_enemy_action(actor, combat_state)

            outcome = resolve_action(action, combat_state)
            render_combat_outcome(outcome)
            input()

            if action.type == "flee":
                return {
                    "result": "fled",
                    "log": combat_state.log
                }



 
            if not player.is_alive():
                combat_state.log.append({"event": "defeat", "by": [enemy.name for enemy in combat_state.enemy_list]})
                combat_state.is_running = False
                return {"result": "defeat", "log": combat_state.log}
            
        combat_state.round_number += 1

    # fallback
    #return {"result": "stopped", "log": combat_state.log}



def ask_player_for_action(actor: Character, combat: Combat_State) -> Optional['Action']:
    while True:
        show_combat_status(combat)

        print("What do you want to do?")
        print("1. Attack")
        print("2. Skills")
        print("3. Use Item")
        print("4. Inspect")
        print("5. Flee")

        choice = input("> ").strip().lower()

        aliases = {
            "1": "attack", "attack": "attack", "a": "attack",
            "2": "skill",  "skills": "skill", "s": "skill",
            "3": "item",   "item": "item",   "i": "item",
            "4": "inspect","inspect": "inspect", "x": "inspect",
            "5": "flee",   "flee": "flee",   "f": "flee",
        }

        action = aliases.get(choice)
        if not action:
            print("Invalid choice.")
            continue

        if action == "attack":
            enemies = combat.alive_enemies()
            target = _choose_enemy_target(enemies)
            if target is None:
                continue
            return Action(actor, "attack", target)
        
        elif action == "skill":
            skills = actor.usable_skills
            
            print() #spaceing

            if not skills:
                print("You have no skills.")
                input()
                continue

            for i, skill_id in enumerate(skills, start=1):
                skill = SKILL_REGISTRY.get(skill_id)
                print(f"{i}. {skill.name} — {skill.description}")
            print("c. Cancel")

            choice = input("> ").strip().lower()
            if choice in ("c", "back", "cancel"):
                continue

            idx = int(choice) - 1
            skill_id = skills[idx]
            skill = SKILL_REGISTRY.get(skill_id)

            if skill.target == "enemy":
                enemies = combat.alive_enemies()
                target = _choose_enemy_target(enemies)
                if target is None:
                    continue
                return Action(actor, "skill", target, skill_id=skill_id)

            elif skill.target == "self":
                return Action(actor, "skill", actor, skill_id=skill_id)

        
        elif action == "item":
            inventory_choice = _choose_consumable_from_inventory(actor)
            if inventory_choice is None:
                continue

            print("\nWho do you want to use it on?")
            print("1. Yourself")
            enemies = combat.alive_enemies()
            for i, e in enumerate(enemies, start=2):
                print(f"{i}. {e.name} ({e.hp} HP)")

            while True:
                target_input = input("> ").strip().lower()
                if target_input in ("c", "back", "cancel"):
                    break
                try:
                    print()
                    idx = int(target_input)
                    if idx == 1:
                        return Action(actor, "item", actor, item_id=inventory_choice["key"])
                    enemy_idx = idx - 2
                    if 0 <= enemy_idx < len(enemies):
                        return Action(actor, "item", enemies[enemy_idx], item_id=inventory_choice["key"])
                except ValueError:
                    pass
                print("Invalid target.")

            continue

        if action == "skill":
            skills = actor.usable_skills

            if not skills:
                print("You have no usable skills.")
                input()
                continue

            print("\nChoose a skill:")
            for i, skill_id in enumerate(skills, start=1):
                skill = SKILL_REGISTRY.get(skill_id)
                if not skill:
                    continue
                print(f"{i}. {skill.name} — {skill.description}")

            print("c. Cancel")

            choice = input("> ").strip().lower()
            if choice in ("c", "back", "cancel"):
                continue

            if not choice.isdigit():
                print("Invalid choice.")
                continue

            idx = int(choice) - 1
            if idx < 0 or idx >= len(skills):
                print("Invalid selection.")
                continue

            selected_skill_id = skills[idx]

            return Action(
                actor=actor,
                action_type="skill",
                target=None,
                skill_id=selected_skill_id,
            )


        if action == "inspect":
            print("\nInspect:")
            print("1. Enemies")
            print(f"2. {actor.name}'s statuses")
            print("c. Cancel")

            sub = input("> ").strip().lower()

            if sub in ("c", "back", "cancel"):
                continue

            if sub in ("1", "enemies", "enemy"):
                enemies = combat.alive_enemies()
                if not enemies:
                    print("There is nothing to inspect.")
                    input()
                    continue
                
                print()
                for i, enemy in enumerate(enemies, start=1):
                    print(f"{i}. {enemy.name}")
                print("c. Cancel")

                choice = input("> ").strip().lower()
                if choice in ("c", "back", "cancel"):
                    continue
                try:
                    idx = int(choice) - 1
                    if not (0 <= idx < len(enemies)):
                        continue

                    enemy = enemies[idx]

                    print(f"\n{enemy.name}")
                    print(f"HP: {enemy.hp}")

                    etype = getattr(enemy, "type", None)
                    behavior = getattr(enemy, "behavior_tag", None)

                    print(f"Type: {etype.value if etype else 'Unknown'}")
                    print(f"Behavior: {behavior.value if behavior else 'Unknown'}")

                    if not enemy.statuses:
                        print("Statuses: None")
                        input("\nPress Enter to continue...")
                        continue

                    print("Statuses:")
                    for s in enemy.statuses:
                        icon = STATUS_REGISTRY.get(s.id, {}).get("icon", "?")
                        print(f" - {icon} {s.id.replace('_', ' ').title()} ({s.remaining_turns})")

                    print("\nInspect enemy statuses?")
                    print("1. Yes")
                    print("2. Back")

                    sub_choice = input("> ").strip().lower()
                    if sub_choice != "1":
                        continue

                    print()
                    tooltip_lines = render_status_tooltip(s, enemy)

                    for line in tooltip_lines:
                        print(line)
                        
                    print("-" * 30)

                    input("\nPress Enter to continue...")

                except ValueError:
                    pass
                continue

            if sub in ("2", "statuses", "status"):

                if not actor.statuses:
                    print("\nYou have no active statuses.")
                    input()
                    continue

                print()
                for i, s in enumerate(actor.statuses, start=1):
                    print(f"{i}. {s.id.replace('_', ' ').title()}")
                print("c. Cancel")

                choice = input("> ").strip().lower()
                if choice in ("c", "back", "cancel"):
                    continue

                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(actor.statuses):
                        status = actor.statuses[idx]
                        print()
                        tooltip_lines = render_status_tooltip(status, actor)

                        for line in tooltip_lines:
                            print(line)
                            
                        print("-" * 30)

                        input("\nPress Enter to continue...")
                except ValueError:
                    pass

                continue

        if action == "flee":
            return Action(actor, "flee", None)

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
        if blocked:
            print(f"{actor}'s attack was blocked by {target}!")
        else:
            crit = " CRITICAL HIT!" if critical else ""
            print(f"{actor} hits {target} for {damage} damage.{crit}")
        if died:
            print(f"\n{target} has been slain!")
    
    elif action == "skill":
        skill_name = outcome.get("extra", {}).get("skill", "Skill")
        skill_name = skill_name.replace("_", " ").title()

        missed = outcome.get("extra", {}).get("missed", False)

        if missed:
            print(f"{actor} uses {skill_name}, but misses!")
            return

        if blocked:
            print(f"{actor}'s {skill_name} was blocked by {target}!")
            return

        text = f"{actor} uses {skill_name}"
        if target:
            text += f" on {target}"

        if damage > 0:
            text += f" for {damage} damage"

        print(text + ".")
        
        if died:
            print(f"{target} has been slain!")

    elif action == "item":
        print(f"{actor} uses an item on {target}.")

    elif action == "flee":
        if extra.get("escaped"):
            print(f"{actor} successfully fled!")
        else:
            print(f"{actor} failed to flee!")

    print()  # spacing


def decide_enemy_action(enemy: Enemy, combat_state: Combat_State) -> 'Action':
    # Example: if enemy has .max_hp, check low-health behavior (defensive)
    # special_move = getattr(enemy, "special_move", None)
    # if special_move and enemy.hp < getattr(enemy, "max_hp", enemy.hp) * 0.5:
    #     return Action(enemy, "skill", state.player, skill_id=special_move)
    
    return Action(enemy, "attack", combat_state.player)
   