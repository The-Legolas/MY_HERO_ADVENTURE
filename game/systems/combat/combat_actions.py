import random
from typing import TYPE_CHECKING

from game.core.character import Character
from game.core.Enemy_class import Enemy
from game.core.Status import Status

from game.definitions.skill_registry import SKILL_REGISTRY
from game.definitions.status_registry import STATUS_REGISTRY

from game.systems.combat.damage_resolver import resolve_damage

from game.systems.enums.enemy_behavior_tag import Enemy_behavior_tag

if TYPE_CHECKING:
    from game.systems.combat.combat_controller import Combat_State




class Action():
    def __init__(self, actor: Character, action_type: str, target: Character | None = None, skill_id: str | None = None, item_id: str | None = None, state: str | None = None,):
        self.actor = actor
        self.type = action_type
        self.target = target
        self.skill_id = skill_id
        self.item_id = item_id
        self.state = state


def _make_outcome(actor_name: str, action: str, target_name: str | None = None, damage: int = 0,
                  blocked: bool = False, critical: bool = False, died: bool = False, extra: dict | None = None) -> dict:
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


def _choose_enemy_target(enemies: list[Enemy]) -> Enemy | None:
    if not enemies:
        print("\nThere are no enemies to target.")
        return None
    print()
    for i, e in enumerate(enemies, start=1):
        print(f"{i}. {e.name} (HP: {e.hp})")
    while True:
        choice = input("Choose target number (or 'c' to cancel): ").strip().lower()
        print()
        if choice == "c":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(enemies):
                return enemies[idx]
        except ValueError:
            pass
        print("Invalid selection. Try again.")


def _choose_consumable_from_inventory(actor: Character) -> dict[str, any] | None:
    inventory = getattr(actor, "inventory", {}).get("items", {})
    consumables = [entry for entry in inventory.items() if entry[1]["item"].category.name == "CONSUMABLE"]
    if not consumables:
        print("\nYou have no consumable items.")
        input()
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

 

def resolve_action(action: Action, combat_state: 'Combat_State') -> dict:
    actor = action.actor
    status_feedback = None
    if not actor.is_alive():
        outcome = _make_outcome(getattr(actor, "name", "Unknown"), "noop", None)
        combat_state.log.append(outcome)
        return outcome
    
    if action.type == "attack":
        target = action.target

        damage_def = {
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
            "can_crit": True,
        }

        result = resolve_damage(actor, target, damage_def)

        
        if not result["blocked"] and result["damage"] > 0:
            for effect in actor.get_on_hit_effects():
                if random.random() > effect.get("chance", 1.0):
                    continue

                status_data = effect.get("status")
                if not status_data:
                    continue

                target_entity = actor if status_data.get("target") == "self" else target
                if not target_entity:
                    continue

                status = Status(
                    id=status_data["id"],
                    remaining_turns=status_data["duration"],
                    magnitude=status_data.get("magnitude", 1),
                    source=actor.name,
                )

                target_entity.apply_status(status, combat_state.log)



        outcome = _make_outcome(actor.name, "attack", target.name if target else None, result["damage"], result["blocked"], result["critical"], result["died"])
        combat_state.log.append(outcome)
        return outcome
    
    if action.type == "skill":
        skill = SKILL_REGISTRY.get(action.skill_id)
        target = action.target

        if not skill:
            outcome = _make_outcome(actor.name, "skill_fail", None)
            combat_state.log.append(outcome)
            return outcome
        
        cost = skill.cost
        if cost:
            amount = cost.get("amount", 0)
            if actor.resource_current < amount:
                outcome = _make_outcome(
                    actor.name,
                    "skill_fail",
                    target.name if target else None,
                    extra={
                        "reason": "not_enough_resource",
                        "resource": actor.resource_name,
                    }
                )
                combat_state.log.append(outcome)
                return outcome
        
        if cost:
            actor.resource_current -= cost["amount"]
        
        if skill.effects:
            for effect in skill.effects:

                if effect["type"] == "cleanse":
                    actor.statuses = [
                        s for s in actor.statuses
                        if not STATUS_REGISTRY.get(s.id, {}).get("is_debuff", False)
                        or s.id in effect.get("except", [])
                    ]

                elif effect["type"] == "apply_status":
                    stacks = effect.get("stacks")
                    status_id = effect["id"]

                    if stacks == "max":
                        max_stacks = STATUS_REGISTRY.get(status_id, {}).get("max_stacks", 1)
                        magnitude = max_stacks
                    else:
                        magnitude = effect.get("magnitude")

                    status = Status(
                        id=status_id,
                        remaining_turns=effect["duration"],
                        magnitude=magnitude,
                        source=skill.name,
                    )
                    actor.apply_status(status, combat_state.log)


        if random.random() > skill.hit_chance:
            outcome = _make_outcome(
                actor.name,
                "skill",
                target.name if target else None,
                damage=0,
                blocked=False,
                critical=False,
                died=False,
                extra={"skill": skill.id, "missed": True}
            )
            combat_state.log.append(outcome)
            return outcome

        if skill.damage:
            result = resolve_damage(actor, target, skill.damage)
        else:
            result = {
                "damage": 0,
                "blocked": False,
                "critical": False,
                "died": False,
            }

        if skill.apply_status and target and not result["blocked"]:
            if random.random() <= skill.apply_status.get("chance", 1.0):
                status = Status(
                    id=skill.apply_status["id"],
                    remaining_turns=skill.apply_status["duration"],
                    magnitude=skill.apply_status.get("magnitude"),
                    source=skill.name,
                )
                status_feedback = None
                status_result = target.apply_status(status, combat_state.log)
                
                if isinstance(status_result, dict):
                    if not status_result.get("applied"):
                        status_feedback = {
                            "status": status_result["status"],
                            "result": status_result["reason"],
                        }

                    else:
                        affinity = status_result.get("affinity")
                        if affinity in ("resistant", "vulnerable"):
                            status_feedback = {
                                "status": status_result["status"],
                                "result": affinity,
                            }

        outcome = _make_outcome(actor.name, "skill", target.name if target else None, result["damage"], result["blocked"], result["critical"], result["died"], extra={"skill": skill.id})
        if status_feedback:
            outcome["status_feedback"] = status_feedback

        combat_state.log.append(outcome)

        if isinstance(actor, Enemy):
            if skill.cooldown_turns:
                actor.skill_cooldowns[skill.id] = skill.cooldown_turns

        return outcome
    
    if action.type == "defend":
        outcome = _make_outcome(actor.name, "defend", actor.name)
        combat_state.log.append(outcome)
        return outcome


    if action.type == "item":
        outcome = actor.use_item(action.item_id, action.target)
        combat_state.log.append({
            "event": "item",
            "actor": actor.name,
            "target": getattr(action.target, "name", None),
            "outcome": outcome,
        })
        return outcome

    if action.type == "flee":
        success = _compute_escape_chance(combat_state)

        outcome = _make_outcome(actor.name, "flee", None, extra={"escaped": success})

        if success == True:
            combat_state.is_running = False

        combat_state.log.append(outcome)
        return outcome
    
    if action.type == "wait":
        if isinstance(action.state, dict):
            reason = action.state.get("state")
        else:
            reason = action.state

        outcome = {
            "action": "wait",
            "actor": action.actor.name,
            "target": None,
            "damage": 0,
            "blocked": False,
            "critical": False,
            "died": False,
            "extra": {
                "reason": reason
            }
        }

        combat_state.log.append(outcome)
        return outcome
    
    return outcome


def _compute_escape_chance(combat_state: 'Combat_State') -> bool:
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

