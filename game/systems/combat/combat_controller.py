from game.systems.combat.combat_turn import _get_initiative_value
from game.core.Character_class import Character
from game.core.Enemy_class import Enemy
from game.world.Dungeon_room_code import Room
from game.core.Item_class import roll_loot
from typing import Optional, Any
from game.systems.combat.combat_actions import Action, resolve_action, _choose_consumable_from_inventory, _choose_enemy_target

class Combat_State():
    def __init__(self, player: Character, enemy_list: list[Enemy]):
        self.player: Character = player
        self.enemy_list: list[Enemy] = enemy_list
        self.round_number: int = 1
        self.log: list[dict[str, Any]] = []
        self.is_running: bool = True

    def alive_enemies(self) -> list[Enemy]:
        return [enemy for enemy in self.enemy_list if enemy.is_alive()]

def show_combat_status(combat: Combat_State):
    player = combat.player
    print("\n=== COMBAT STATUS ===")
    print(f"You: {player.hp}/{getattr(player, 'max_hp', player.hp)} HP")

    print("\nEnemies:")
    for i, enemy in enumerate(combat.alive_enemies(), start=1):
        max_hp = getattr(enemy, "max_hp", enemy.hp)
        print(f"{i}. {enemy.name} ({enemy.hp}/{max_hp} HP)")
    print("=====================\n")



def start_encounter(player: Character, room: Room) -> dict[str, Any]:
    enemy_list = list(room.contents.get("enemies", []))

    combat_state = Combat_State(player, enemy_list)
    combat_state.is_running = True
    combat_state.log.append({"event": "encounter_start", "player": player.name, "enemy_count": len(enemy_list)})

    if not enemy_list:
        return {"result": "no_enemies", "log": combat_state.log}

    while combat_state.is_running:
        participants = [player] + combat_state.alive_enemies()
        participants_sorted = sorted(participants, key=_get_initiative_value, reverse=True)

        for actor in participants_sorted:
            if not combat_state.is_running:
                break
            if not actor.is_alive():
                continue
            
            # process statuses placeholder (not implemented yet)
            # _process_statuses(actor, state)

            if actor is combat_state.player:
                action = ask_player_for_action(actor, combat_state)
                if action is None:
                    continue

            else:
                action = decide_enemy_action(actor, combat_state)

            outcome = resolve_action(action, combat_state)
            render_combat_outcome(outcome)
            input()
            
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
                
                print("\n=== VICTORY ===")

                if total_loot["gold"] > 0:
                    print(f"You gained {total_loot['gold']} gold.")
                else:
                    print("You gained no gold.")

                if xp_gain > 0:
                    print(f"You gained {xp_gain} experience.")

                if total_loot["items"]:
                    print("\nLoot obtained:")
                    item_counts = {}
                    for item in total_loot["items"]:
                        item_counts[item.name] = item_counts.get(item.name, 0) + 1

                    for name, count in item_counts.items():
                        print(f"- {name} x{count}")
                else:
                    print("\nNo items dropped.")

                print("================\n")
                
                combat_state.log.append({"event": "victory", "loot": total_loot})
                combat_state.is_running = False
                return {"result": "victory", "log": combat_state.log, "loot": total_loot}



 
            if not player.is_alive():
                combat_state.log.append({"event": "defeat", "by": [enemy.name for enemy in combat_state.enemy_list]})
                combat_state.is_running = False
                return {"result": "defeat", "log": combat_state.log}
        combat_state.round_number += 1

    # fallback
    return {"result": "stopped", "log": combat_state.log}



def ask_player_for_action(actor: Character, combat: Combat_State) -> Optional['Action']:
    while True:
        show_combat_status(combat)

        print("What do you want to do?")
        print("1. Attack")
        print("2. Use Item")
        print("3. Inspect Enemy")
        print("4. Flee")

        choice = input("> ").strip().lower()

        aliases = {
            "1": "attack", "attack": "attack", "a": "attack",
            "2": "item",   "item": "item",   "i": "item",
            "3": "inspect","inspect": "inspect", "x": "inspect",
            "4": "flee",   "flee": "flee",   "f": "flee",
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
            enemies = combat.alive_enemies()
            if not enemies:
                print("There is nothing to inspect.")
                input()
                continue
            
            print()
            for i, e in enumerate(enemies, start=1):
                print(f"{i}. {e.name}")
            print("c. Cancel")

            choice = input("> ").strip().lower()
            if choice in ("c", "back", "cancel"):
                continue
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(enemies):
                    e = enemies[idx]
                    print(f"\n{e.name}")
                    print(f"HP: {e.hp}")
                    etype = getattr(e, "type", None)
                    behavior = getattr(e, "behavior_tag", None)

                    print(f"Type: {etype.value if etype else 'Unknown'}")
                    print(f"Behavior: {behavior.value if behavior else 'Unknown'}")

                    input("\nPress Enter to continue...")
            except ValueError:
                pass
            continue

        if action == "flee":
            return Action(actor, "flee", None)

def render_combat_outcome(outcome: dict):
    actor = outcome["actor"]
    action = outcome["action"]
    target = outcome["target"]
    dmg = outcome["damage"]
    blocked = outcome["blocked"]
    critical = outcome["critical"]
    died = outcome["died"]
    extra = outcome.get("extra", {})

    if action == "attack":
        if blocked:
            print(f"{actor.title()}'s attack was blocked by {target.title()}!")
        else:
            crit = " CRITICAL HIT!" if critical else ""
            print(f"{actor.title()} hits {target.title()} for {dmg} damage.{crit}")
        if died:
            print(f"\n{target.title()} has been slain!")

    elif action == "item":
        print(f"{actor.title()} uses an item on {target.title()}.")

    elif action == "flee":
        if extra.get("escaped"):
            print(f"{actor.title()} successfully fled!")
        else:
            print(f"{actor.title()} failed to flee!")

    print()  # spacing after action


def decide_enemy_action(enemy: Enemy, combat_state: Combat_State) -> 'Action':
    # Example: if enemy has .max_hp, check low-health behavior (defensive)
    # special_move = getattr(enemy, "special_move", None)
    # if special_move and enemy.hp < getattr(enemy, "max_hp", enemy.hp) * 0.5:
    #     return Action(enemy, "skill", state.player, skill_id=special_move)
    
    return Action(enemy, "attack", combat_state.player)
   