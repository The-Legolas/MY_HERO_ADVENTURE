from game.core.Character_class import Character
from game.core.Enemy_class import Enemy
from game.world.Dungeon_room_code import Room
from game.core.Item_class import roll_loot
from typing import Optional, Any

from combat.Combat_manager import Action
from combat.Combat_manager import _get_initiative_value, resolve_action, _choose_consumable_from_inventory, _choose_enemy_target



class Combat_State():
    def __init__(self, player: Character, enemy_list: list[Enemy]):
        self.player: Character = player
        self.enemy_list: list[Enemy] = enemy_list
        self.round_number: int = 1
        self.log: list[dict[str, Any]] = []
        self.is_running: bool = True

    def alive_enemies(self) -> list[Enemy]:
        return [enemy for enemy in self.enemy_list if enemy.is_alive()]



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

            resolve_action(action, combat_state)

            if not combat_state.alive_enemies():
                killed = [enemy for enemy in enemy_list if not enemy.is_alive()]
                total_loot = {"gold": 0, "items": []}
                for dead in killed:
                    loot = roll_loot(dead)
                    total_loot["gold"] += loot.get("gold", 0)
                    for item in loot.get("items", []):
                        total_loot["items"].append(item)
                        player.add_item(item)
                    
                    player.xp = getattr(player, "xp", 0) + getattr(dead, "xp_reward", 0)
                
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



def ask_player_for_action(actor: Character, combat: Combat_State) -> Optional[Action]:
    while True:
        choice = input("What do you wish to do? (attack / item / flee) : ").strip().lower()
        if choice in ("attack", "item", "flee"):
            break
        print("Invalid action.")
    
    match choice:
        case "attack":
                enemies = combat.alive_enemies()
                target = _choose_enemy_target(enemies)
                if target is None:
                    return None
                return Action(combat.player, "attack", target)

        case "item":        
            inventory_choice = _choose_consumable_from_inventory(combat.player)
            if inventory_choice is None:
                return None
            print("Who to use the item on?")
            print("1. Self")
            
            enemies = combat.alive_enemies()
            for i, e in enumerate(enemies, start=2):
                print(f"{i}. {e.name} (HP:{e.hp})")
            
            while True:
                target = input("Target # : ").strip().lower()
                if target == "c":
                    return None
                try:
                    idx = int(target)
                    if idx == 1:
                        return Action(combat.player, "item", combat.player, item_id=inventory_choice["key"])
                    else:
                        enemy_idx = idx - 2
                        if 0 <= enemy_idx < len(enemies):
                            return Action(combat.player, "item", enemies[enemy_idx], item_id=inventory_choice["key"])
                except ValueError:
                    pass
                print("Invalid selection.")



        case "flee":
            return Action(actor, "flee", None)
        
        case _:
            return None


def decide_enemy_action(enemy: Enemy, combat_state: Combat_State) -> Action:
    # Example: if enemy has .max_hp, check low-health behavior (defensive)
    # special_move = getattr(enemy, "special_move", None)
    # if special_move and enemy.hp < getattr(enemy, "max_hp", enemy.hp) * 0.5:
    #     return Action(enemy, "skill", state.player, skill_id=special_move)
    
    return Action(enemy, "attack", combat_state.player)
   