from game.systems.combat.combat_turn import _get_initiative_value
from game.core.Character_class import Character
from game.core.Enemy_class import Enemy, Enemy_behavior_tag
from game.world.Dungeon_room_code import Room
from game.core.Item_class import roll_loot
from game.systems.combat.combat_actions import Action, resolve_action, _choose_consumable_from_inventory, _choose_enemy_target
from game.ui.status_ui import format_status_icons
import random
from typing import Optional
from game.core.Status import Status
from game.ui.status_ui import describe_status_compact, sort_statuses_by_priority, inspect_entity_statuses
from game.systems.combat.status_registry import STATUS_REGISTRY
from game.core.Skill_class import Skill
from game.core.class_progression import SKILL_REGISTRY
from game.ui.combat_text_helpers import describe_attack, describe_skill, describe_wait

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
        if e.intent:
            if e.intent["type"] == "charging":
                turns = e.intent["turns"]

                if turns > 1:
                    print(
                        f"\tIntent: {e.intent['text']} "
                        f"({turns - 1} turns)"
                    )
                elif turns == 1:
                    print(
                        f"\tIntent: {e.intent['text']} "
                        f"(imminent)"
                    )
            else:
                print(f"\tIntent: {e.intent['text']} ")
            
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

        for enemy in combat_state.alive_enemies():
            if isinstance(enemy, Enemy) and enemy.locked_state:
                enemy.locked_state["turns"] -= 1
            plan_enemy_intent(enemy, combat_state)

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
                total_xp = 0
                for dead in killed:
                    loot = roll_loot(dead)
                    total_loot["gold"] += loot.get("gold", 0)
                    total_xp += getattr(dead, "xp_reward", 0)

                    for item in loot.get("items", []):
                        total_loot["items"].append(item)
                        player.add_item(item)

                if total_xp > 0:
                    level_ups = player.gain_xp(total_xp)

                for level_data in level_ups:
                    player.render_level_up_screen(level_data)

                if total_loot["gold"] > 0:
                    player.inventory["gold"] += total_loot["gold"]
                
                combat_state.log.append({"event": "victory", "loot": total_loot, "xp": total_xp})
                combat_state.is_running = False
                return {"result": "victory", "log": combat_state.log, "loot": total_loot, "xp": total_xp}


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

            if isinstance(actor, Enemy):
                actor.tick_skill_cooldowns()
            
            actor.statuses = [
                s for s in actor.statuses
                if not getattr(s, "expires_end_of_turn", False)
            ]

            if action.type == "flee" and not combat_state.is_running:
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
        print("3. Defend")
        print("4. Use Item")
        print("5. Inspect")
        print("6. Flee")

        choice = input("> ").strip().lower()

        aliases = {
            "1": "attack", "attack": "attack", "a": "attack",
            "2": "skill",  "skills": "skill", "s": "skill",
            "3": "defend", "defend": "defend", "d": "defend",
            "4": "item",   "item": "item",   "i": "item",
            "5": "inspect","inspect": "inspect", "x": "inspect",
            "6": "flee",   "flee": "flee",   "f": "flee",
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
        
        
        if action == "skill":
            skills = actor.usable_skills
            
            print() #spaceing

            if not skills:
                print("You have no skills.")
                input()
                continue

            for i, skill_id in enumerate(skills, start=1):
                skill = SKILL_REGISTRY.get(skill_id)

                if not skill:
                    print(f"{i}. [INVALID SKILL: {skill_id}]")
                    continue

                print(f"{i}. {skill.name} — {skill.description}")
            print("c. Cancel")

            choice = input("> ").strip().lower()

            if not choice.isdigit():
                continue

            idx = int(choice) - 1
            if idx < 0 or idx >= len(skills):
                print("Invalid selection.")
                continue


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
            
            else:
                print("This skill cannot be used right now.")
                continue


        if action == "defend":
            return Action(actor, "defend", actor)

        
        if action == "item":
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
                    input("\nPress Enter to continue...")
                    continue
                while True:       
                    print()
                    for i, enemy in enumerate(enemies, start=1):
                        print(f"{i}. {enemy.name}")
                    print("c. Cancel")

                    choice = input("> ").strip().lower()
                    if choice in ("c", "back", "cancel"):
                        break

                    if not choice.isdigit():
                        break
                
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
                    for status in sort_statuses_by_priority(enemy.statuses):
                        print(f" - {describe_status_compact(status)}")

                    print("\nInspect enemy statuses?")
                    print("1. Yes")
                    print("2. Back")

                    sub_choice = input("> ").strip().lower()
                    if sub_choice != "1":
                        continue

                    inspect_entity_statuses(enemy)


            if sub in ("2", "statuses", "status"):

                if not actor.statuses:
                    print("\nYou have no active statuses.")
                    input()
                    continue

                print()
                inspect_entity_statuses(actor)
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
        print(f"{actor} {describe_wait(extra)}.")

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


def decide_enemy_action(enemy: Enemy, combat_state: Combat_State) -> 'Action':
    player = combat_state.player

    if enemy.locked_state:
        enemy.locked_state["turns"] -= 1

        forced = enemy.locked_state.get("forced_action")
        if forced == "attack":
            return Action(enemy, "attack", player)
        if forced == "defend":
            return Action(enemy, "defend", enemy)
        
        if enemy.locked_state["turns"] > 0:
            return Action(enemy, "wait", None)
        
        skill_id = enemy.locked_state.get("skill_id")
        enemy.locked_state = None

        skill = SKILL_REGISTRY.get(skill_id)
        if not skill:
            return Action(enemy, "attack", player)

        target = enemy if skill.target == "self" else player
        return Action(enemy, "skill", target, skill_id=skill_id)

    intent = enemy.intent
    enemy.intent = None

    if not intent:
        return Action(enemy, "attack", player)

    if intent["type"] == "attack":
        return Action(enemy, "attack", player)

    if intent["type"] == "skill":
        skill = SKILL_REGISTRY.get(intent["skill_id"])
        if not skill:
            return Action(enemy, "attack", player)

        target = enemy if skill.target == "self" else player
        return Action(enemy, "skill", target, skill_id=skill.id)

    if intent["type"] == "charging":
        enemy.locked_state = {
            "skill_id": intent["skill_id"],
            "turns": intent["turns"],
            "forced_action": intent.get("forced_action"),
            "intent_hint": intent["text"],
        }
        return Action(enemy, "wait", None)
    
    return Action(enemy, "attack", player)


def get_available_enemy_skills(enemy, combat_state) -> list[Skill]:

    available = []

    for skill_id in enemy.usable_skills:
        skill = SKILL_REGISTRY.get(skill_id)
        if not skill:
            continue

        if skill_id in enemy.skill_cooldowns:
            continue

        if enemy.locked_state and not skill.allowed_while_locked:
            continue

        target = enemy if skill.target == "self" else combat_state.player

        if skill.requires_target_alive and not target.is_alive():
            continue

        if skill.forbid_if_target_has:
            if any(target.has_status(s) for s in skill.forbid_if_target_has):
                continue

        available.append(skill)

    return available

def plan_enemy_intent(enemy: Enemy, combat_state: Combat_State) -> None:
#fix
    if enemy.locked_state:
        enemy.intent = {
            "type": "charging",
            "skill_id": enemy.locked_state["skill_id"],
            "turns": enemy.locked_state["turns"],
            "forced_action": enemy.locked_state.get("forced_action"),
            "text": enemy.locked_state.get("intent_hint", "Gathering power lin 561"),
        }
        return

    skills = get_available_enemy_skills(enemy, combat_state)
    
    if not skills:
        enemy.intent = {
            "type": "attack",
            "skill_id": None,
            "turns": None,
            "forced_action": None,
            "text": "Preparing a basic attack",
        }
        return
    
    chosen_skill = weighted_pick_enemy_skill(enemy, skills)

    if chosen_skill.locks_actor:
        enemy.intent = {
            "type": "charging",
            "skill_id": chosen_skill.id,
            "turns": chosen_skill.locks_actor["turns"],
            "forced_action": chosen_skill.locks_actor.get("forced_action"),
            "text": chosen_skill.intent_hint,
        }
        return

    enemy.intent = {
        "type": "skill",
        "skill_id": chosen_skill.id,
        "turns": None,
        "forced_action": None,
        "text": chosen_skill.intent_hint,
    }

def weighted_pick_enemy_skill(enemy: Enemy, skills: list[Skill]) -> Skill:
    behavior = enemy.behavior_tag or Enemy_behavior_tag.NORMAL
    behavior_weights = BEHAVIOR_WEIGHTS[behavior]

    choices = []
    weights = []

    for skill in skills:
        w = 1.0

        if skill.damage:
            w *= behavior_weights.get("damage", 1.0)

        if skill.apply_status:
            if skill.apply_status["id"] in ("stun", "poison", "weakened"):
                w *= behavior_weights.get("debuff", 1.0)
            else:
                w *= behavior_weights.get("buff", 1.0)

        if skill.locks_actor:
            w *= behavior_weights.get("lock", 1.0)

        choices.append(skill)
        weights.append(w)

    chosen_skill = random.choices(choices, weights=weights, k=1)[0]
    return chosen_skill


BEHAVIOR_WEIGHTS = {
    Enemy_behavior_tag.AGGRESSIVE: {
        "damage": 3.0,
        "debuff": 1.5,
        "buff": 0.5,
    },
    Enemy_behavior_tag.COWARDLY: {
        "damage": 0.5,
        "debuff": 2.0,
        "buff": 2.5,
    },
    Enemy_behavior_tag.SLOW: {
        "damage": 1.5,
        "debuff": 1.0,
        "buff": 0.5,
        "lock": 2.5,
    },
    Enemy_behavior_tag.RANGED: {
        "damage": 2.0,
        "debuff": 1.5,
        "buff": 0.5,
    },
    Enemy_behavior_tag.HULKING: {
        "damage": 3.0,
        "lock": 2.0,
        "debuff": 0.5,
    },
    Enemy_behavior_tag.NORMAL: {
        "damage": 1.0,
        "debuff": 1.0,
        "buff": 1.0,
    },
}
