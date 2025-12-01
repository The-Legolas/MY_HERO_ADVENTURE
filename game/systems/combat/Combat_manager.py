from game.core.Character_class import Character
from game.core.Enemy_class import Enemy, Enemy_behavior_tag
from game.world.Dungeon_room_code import Room
from game.core.Item_class import roll_loot
import random
from typing import Optional, Any, Callable

class Combat_State():
    def __init__(self, player: Character, enemy_list: list[Enemy]):
        self.player: Character = player
        self.enemy_list: list[Enemy] = enemy_list
        self.round_number: int = 1
        self.log: list[dict[str, Any]] = []
        self.is_running: bool = True

    def alive_enemies(self) -> list[Enemy]:
        return [enemy for enemy in self.enemy_list if enemy.is_alive()]

class Action():
    def __init__(self, actor: Character, action_type: str, target: Optional[Character], skill_id: Optional[str] = None, item_id:Optional[str] = None):
        self.actor = actor
        self.type = action_type
        self.target = target
        self.skill_id = skill_id
        self.item_id = item_id


class Status():
    def __init__(self, id: str, remaining_turns: int, magnitude: int | dict | None, source: Optional[str] = None):
        self.id = id
        self.remaining_turns = remaining_turns
        self.source = source
        self.magnitude = magnitude


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



def _make_outcome(actor_name: str, action: str, target_name: Optional[str], damage: int = 0,
                  blocked: bool = False, critical: bool = False, died: bool = False, extra: Optional[dict] = None) -> dict:
    return {
        "actor": actor_name,
        "action": action,
        "target": target_name,
        "damage": int(damage),
        "blocked": bool(blocked),
        "critical": bool(critical),
        "died": bool(died),
        "extra": extra or {}
    }

def _get_initiative_value(entity: Character) -> int:
    speed = getattr(entity, "speed", None)
    if speed is not None:
        return int(speed)
    if isinstance(entity, Character) and not isinstance(entity, Enemy):
        return 999
    return 0


def _choose_enemy_target(enemies: list[Enemy]) -> Optional[Enemy]:
    if not enemies:
        print("There are no enemies to target.")
        return None

    for i, e in enumerate(enemies, start=1):
        print(f"{i}. {e.name} (HP: {e.hp})")
    while True:
        choice = input("Choose target number (or 'c' to cancel): ").strip().lower()
        if choice == "c":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(enemies):
                return enemies[idx]
        except ValueError:
            pass
        print("Invalid selection. Try again.")


def _choose_consumable_from_inventory(actor: Character) -> Optional[dict[str, Any]]:
    inventory = getattr(actor, "inventory", {}).get("items", {})
    consumables = [entry for entry in inventory.items() if entry[1]["item"].category.name == "CONSUMABLE"]
    if not consumables:
        print("You have no consumable items.")
        return None

    for i, (key, data) in enumerate(consumables, start=1):
        print(f"{i}. {data['item'].name} x{data['count']}")
    while True:
        choice = input("Choose item number (or 'c' to cancel): ").strip().lower()
        if choice == "c":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(consumables):
                key, data = consumables[idx]
                return {"key": key, "item": data["item"], "count": data["count"]}
        except ValueError:
            pass
        print("Invalid selection.")



def decide_enemy_action(enemy: Enemy, combat_state: Combat_State) -> Action:
    # Example: if enemy has .max_hp, check low-health behavior (defensive)
    # special_move = getattr(enemy, "special_move", None)
    # if special_move and enemy.hp < getattr(enemy, "max_hp", enemy.hp) * 0.5:
    #     return Action(enemy, "skill", state.player, skill_id=special_move)
    
    return Action(enemy, "attack", combat_state.player)
    

def resolve_action(action: Action, combat_state: Combat_State) -> dict:
    actor = action.actor
    if not actor.is_alive():
        outcome = _make_outcome(getattr(actor, "name", "Unknown"), "noop", None)
        combat_state.log.append(outcome)
        return outcome
    
    if action.type == "attack":
        raw = actor.attack(action.target)

        attacker_name = raw.get("attacker", getattr(actor, "name", "Unknown"))
        target_name = raw.get("target", getattr(action.target, "name", None)) if action.target else None
        damage = raw.get("damage", 0)
        blocked = raw.get("blocked", False)
        critical = raw.get("critical_hit", raw.get("critical", False))
        died = raw.get("died", False)

        outcome = _make_outcome(attacker_name, "attack", target_name, damage, blocked, critical, died)
        combat_state.log.append(outcome)
        return outcome

    if action.type == "item":
        outcome = actor.use_item(action.item_id, action.target)
        combat_state.log.append(outcome)
        return outcome

    if action.type == "flee":
        success = _compute_escape_chance(combat_state)
        if success:
            outcome = _make_outcome(actor.name, "flee", None, 0, False, False, False, extra={"escaped": True})
            combat_state.is_running = False
        else:
            outcome = _make_outcome(actor.name, "flee", None, 0, False, False, False, extra={"escaped": False})
        combat_state.log.append(outcome)
        return outcome


    outcome = _make_outcome(actor.name, "noop", None)
    combat_state.log.append(outcome)
    return outcome

    
def _compute_escape_chance(combat_state: Combat_State) -> bool:
    base = 0.70
    behavior_penalty = 0.0
    for enemy in combat_state.enemy_list:
        tag = getattr(enemy, "behavior_tag", None)
        if tag == Enemy_behavior_tag.AGGRESSIVE:
            behavior_penalty += 0.10
        if tag == Enemy_behavior_tag.COWARDLY:
            behavior_penalty -= 0.10

    size_penalty = 0.1 * max(0, len(combat_state.enemy_list) - 1)
    noise = random.uniform(-0.12, 0.12)
    chance = max(0.01, min(0.95, base - behavior_penalty - size_penalty + noise))
    return random.random() < chance
