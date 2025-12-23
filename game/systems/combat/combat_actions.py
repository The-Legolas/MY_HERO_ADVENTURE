import random
from game.core.Character_class import Character
from game.core.Enemy_class import Enemy, Enemy_behavior_tag
from game.core.Status import Status
from game.systems.combat.skill_registry import SKILL_REGISTRY
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.systems.combat.combat_controller import Combat_State




class Action():
    def __init__(self, actor: Character, action_type: str, target: None, skill_id: str | None = None, item_id: str | None = None):
        self.actor = actor
        self.type = action_type
        self.target = target
        self.skill_id = skill_id
        self.item_id = item_id


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
        
        if not blocked and damage > 0 and action.target:
            effects = actor.get_on_hit_effects()

            for effect in effects:
                if random.random() > effect.get("chance", 1.0):
                    continue

                status_data = effect.get("status")
                if not status_data:
                    continue

                target_entity = actor if status_data.get("target") == "self" else action.target
                if not target_entity:
                    continue

                status = Status(
                    id=status_data["id"],
                    remaining_turns=status_data["duration"],
                    magnitude=status_data.get("magnitude", 1),
                    source=actor.name,
                )

                target_entity.apply_status(status, combat_state.log)



        outcome = _make_outcome(attacker_name, "attack", target_name, damage, blocked, critical, died)
        combat_state.log.append(outcome)
        return outcome
    
    if action.type == "skill":
        skill = SKILL_REGISTRY.get(action.skill_id)
        actor = action.actor
        target = action.target

        if not skill:
            outcome = _make_outcome(actor.name, "skill_fail", None)
            combat_state.log.append(outcome)
            return outcome
        
        # --- Hit chance ---
        if random.random() > skill.hit_chance:
            outcome = _make_outcome(
                actor.name,
                "skill",
                getattr(target, "name", None),
                damage=0,
                blocked=False,
                extra={"skill": skill.id, "missed": True}
            )
            combat_state.log.append(outcome)
            return outcome

        # --- Damage via normal attack pipeline ---
        result = resolve_skill_damage(actor, target, skill)

        # --- Apply status (if any) ---
        if skill.apply_status and target and not result["blocked"]:
            if random.random() <= skill.apply_status.get("chance", 1.0):
                status = Status(
                    id=skill.apply_status["id"],
                    remaining_turns=skill.apply_status["duration"],
                    magnitude=skill.apply_status.get("magnitude"),
                    source=skill.name,
                )
                target.apply_status(status, combat_state.log)

        outcome = _make_outcome(
            actor.name,
            "skill",
            getattr(target, "name", None),
            damage=result["damage"],
            blocked=result["blocked"],
            critical=result["critical"],
            died=result["died"],
            extra={"skill": skill.id}
        )

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

def resolve_skill_damage(actor, target, skill) -> dict:

    dmg_def = skill.damage

    if dmg_def is None or target is None:
        return {
            "damage": 0,
            "blocked": False,
            "critical": False,
            "died": False,
        }

    raw = 0

    # --- Base damage ---
    if dmg_def["type"] == "flat":
        raw = dmg_def["amount"]

    elif dmg_def["type"] == "multiplier":
        stat_val = getattr(actor, dmg_def["stat"], 0)
        raw = int(stat_val * dmg_def["mult"])

    elif dmg_def["type"] == "hybrid":
        stat_val = getattr(actor, dmg_def["stat"], 0)
        raw = int(dmg_def["base"] + stat_val * dmg_def["mult"])

    # --- Status modifiers ---
    raw = int(raw * actor.get_damage_multiplier())

    # --- Critical ---
    critical = False
    if dmg_def.get("can_crit", True):
        if random.random() >= 0.95:
            raw *= 2
            critical = True

    # --- Defense ---
    if raw <= target.defence:
        return {
            "damage": 0,
            "blocked": True,
            "critical": critical,
            "died": False,
        }

    damage = raw - target.defence
    target.take_damage(damage)

    return {
        "damage": damage,
        "blocked": False,
        "critical": critical,
        "died": not target.is_alive(),
    }
