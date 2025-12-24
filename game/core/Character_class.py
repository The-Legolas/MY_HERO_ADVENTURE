import random
from game.core.Item_class import Item_Type, Items, make_outcome
from game.systems.combat.status_evaluator import evaluate_status_magnitude
from game.systems.combat.status_registry import STATUS_REGISTRY
from game.systems.combat.damage_resolver import resolve_damage
from game.core.Enemy_class import INTERRUPT_RESISTANCE_BY_RARITY

from game.core.Status import Status

class Character():
    def __init__(self, name: str, hp: int, damage: int, defence: int):
        self.name = name
        self.hp = hp
        self.max_hp = self.hp
        self.damage = damage
        self.defence = defence
        self.xp = 0

        self.statuses: list['Status'] = []
        self.known_skills: set[str] = set()
        self.usable_skills: list[str] = []

        self.equipment = {
            "weapon": None,
            "armor": None,
            "ring1": None,
            "ring2": None
        }

        self.inventory = {
            "items": {},
            "gold": 0
        }
    
    def add_item(self, item: Items, amount:int = 1) -> None:
        if item.name not in self.inventory["items"]:
            self.inventory["items"][item.name] = {
                "item": item, 
                "count": amount
                }
            return
        
        if item.stackable:
            self.inventory["items"][item.name]["count"] += amount
    

    def remove_item(self, item_id: str, amount: int = 1) -> None:
        items = self.inventory["items"]

        if item_id not in items:
            return

        entry = items[item_id]
        item_obj = entry["item"]

        # stackable items
        if item_obj.stackable:
            entry["count"] -= amount
            if entry["count"] <= 0:
                del items[item_id]

        else:
            del items[item_id]

    def use_item(self, item: Items, target: 'Character') -> None:
        if isinstance(item, str):
            entry = self.inventory["items"].get(item)
            if not entry:
                return make_outcome(self.name, "use_item_fail", getattr(target, "name", None),
                                    extra={"reason": "item_key_missing", "item_key": item})
            item_obj = entry["item"]
        else:
            item_obj = item

        outcome = item_obj.use(self, target)

        inventory = self.inventory["items"]
        if item_obj.name in inventory:
            entry = inventory[item_obj.name]
            if item_obj.stackable:
                entry["count"] -= 1
                if entry["count"] <= 0:
                    del inventory[item_obj.name]
            else:
                del inventory[item_obj.name]

        return outcome
        

    def equip_item(self, item: Items) -> None:
        if item.category not in (Item_Type.WEAPON, Item_Type.ARMOR, Item_Type.RING):
            print(f"Cannot equip {item.category.value}")
            return 


        if item.category == Item_Type.WEAPON:
            slot = "weapon"
        elif item.category == Item_Type.ARMOR:
            slot = "armor"
        elif item.category == Item_Type.RING:
                if self.equipment["ring1"] is None:
                    slot = "ring1"
                elif self.equipment["ring2"] is None:
                    slot = "ring2"
                else:
                    print("Both ring slots are full.\n")
                    return

    
        if self.equipment[slot] is not None:
            self.unequip_item(self.equipment[slot])

        self.equipment[slot] = item
        
        self.remove_item(item.name, 1)

        if item.category in (Item_Type.WEAPON, Item_Type.ARMOR):
            for stat, value in item.stats.items():
                if stat == "damage":
                    self.damage += value
                elif stat == "defence":
                    self.defence += value
                elif stat == "hp":
                    self.hp += value

        print(f"You equipped {item.name} in {slot} slot.")
        

    def unequip_item(self, item: Items) -> None:
        slot_found = False

        if item.category == Item_Type.WEAPON:
            if self.equipment["weapon"] == item:
                self.equipment["weapon"] = None
                slot_found = True

        elif item.category == Item_Type.ARMOR:
            if self.equipment["armor"] == item:
                self.equipment["armor"] = None
                slot_found = True

        elif item.category == Item_Type.RING:
            if self.equipment["ring1"] == item:
                self.equipment["ring1"] = None
                slot_found = True
            elif self.equipment["ring2"] == item:
                self.equipment["ring2"] = None
                slot_found = True

        if not slot_found:
            print("Item is not equipped.")
            return

        for stat, value in item.stats.items():
            if stat == "damage":
                self.damage -= value
            elif stat == "defence":
                self.defence -= value
            elif stat == "hp":
                self.hp -= value
            elif stat == "crit_chance":
                pass #not implemented yet

        self.add_item(item, 1)
        print(f"You unequipped {item.name}.")



    def take_damage(self, damage: int) -> None:
        self.hp = max(0, self.hp - int(damage))
    
    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + int(amount))


    def is_alive(self) -> bool:
        return True if self.hp > 0 else False  

    def attack(self, other: 'Character') -> dict:
        damage_def = {
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
            "can_crit": True,
        }
        return resolve_damage(self, other, damage_def)
    
    def get_damage_multiplier(self) -> float:
        mult = 1.0
        for status in self.statuses:
            modifiers = STATUS_REGISTRY.get(status.id, {}).get("modifiers", {})
            mult *= modifiers.get("damage_mult", 1.0)
        return mult
    
    def get_effective_defence(self) -> int:
        defence = self.defence

        for status in self.statuses:
            modifiers = STATUS_REGISTRY.get(status.id, {}).get("modifiers", {})
            defence = int(defence * modifiers.get("defence_mult", 1.0))

        return defence


    def can_act(self) -> bool:
        statuses_sorted = sorted(
            self.statuses,
            key=lambda s: STATUS_REGISTRY.get(s.id, {}).get("priority", 50),
            reverse=True
        )

        for status in statuses_sorted:
            if STATUS_REGISTRY.get(status.id, {}).get("prevents_action"):
                return False
        return True


    

    def level_up(self) -> None:
        pass


    def remove_status(self, status_id: str) -> None:
        self.statuses = [status for status in self.statuses if status.id != status_id]

    def has_status(self, status_id: str) -> bool:
        return any(status.id == status_id for status in self.statuses)

    def add_status(self, new_status: 'Status'):
        registry = STATUS_REGISTRY.get(new_status.id)
        if not registry:
            return

        for status in self.statuses:
            if status.id == new_status.id:
                rule = registry.get("stacking", "refresh")

                if rule == "refresh":
                    status.remaining_turns = max(
                        status.remaining_turns,
                        new_status.remaining_turns
                    )
                    return

                if rule == "stack":
                    status.magnitude += new_status.magnitude
                    return

        self.statuses.append(new_status)
    
    def process_statuses(self) -> list[dict]:
        expired = []
        logs = []

        statuses_sorted = sorted(
            self.statuses,
            key=lambda s: STATUS_REGISTRY.get(s.id, {}).get("priority", 50)
        )

        for status in statuses_sorted:
            data = STATUS_REGISTRY.get(status.id, {})

            if status.just_applied:
                status.just_applied = False
                continue

            if "on_tick" in data:
                before_hp = self.hp

                base_magnitude = status.magnitude
                effective_magnitude = evaluate_status_magnitude(
                    status=status,
                    active_statuses=self.statuses
                )

                if effective_magnitude != base_magnitude:
                    interactions = data.get("interactions", {})
                    strongest_rule = None
                    strongest_multiplier = None

                    for other in self.statuses:
                        rule = interactions.get(other.id)
                        if not rule:
                            continue

                        mult = rule.get("damage_multiplier")
                        if mult is None:
                            continue

                        if (
                            strongest_multiplier is None
                            or abs(mult - 1.0) > abs(strongest_multiplier - 1.0)
                        ):
                            strongest_multiplier = mult
                            strongest_rule = other.id

                    if strongest_rule is not None:
                        logs.append({
                            "event": "status_interaction",
                            "status": status.id,
                            "target": self.name,
                            "source": strongest_rule,
                            "multiplier": strongest_multiplier
                        })

                temp_status = Status(
                    id=status.id,
                    remaining_turns=status.remaining_turns,
                    magnitude=effective_magnitude,
                    source=status.source
                )

                data["on_tick"](self, temp_status)

                logs.append({
                    "event": "status_tick",
                    "status": status.id,
                    "target": self.name,
                    "hp_before": before_hp,
                    "hp_after": self.hp
                })

            status.remaining_turns -= 1
            if status.remaining_turns <= 0:
                expired.append(status)

        for status in expired:
            self.statuses.remove(status)
            logs.append({
                "event": "status_expired",
                "status": status.id,
                "target": self.name
            })

        return logs


    def apply_status(self, new_status: 'Status', combat_log: list[dict] | None = None) -> bool:
        resist = self.get_status_resistance(new_status.id)
        if resist > 0 and random.random() < resist:
            if combat_log is not None:
                combat_log.append({
                    "event": "status_resisted",
                    "status": new_status.id,
                    "target": self.name
                })
            return False

        data = STATUS_REGISTRY.get(new_status.id, {})
        stacking = data.get("stacking", "replace")
        max_stacks = data.get("max_stacks", 1)

        existing = [s for s in self.statuses if s.id == new_status.id]
        
        applied = False

        if not existing:
            new_status.just_applied = True
            self.statuses.append(new_status)
            applied = True
        else:
            current = existing[0]

            if stacking == "refresh":
                current.remaining_turns = max(
                    current.remaining_turns,
                    new_status.remaining_turns
                )
                applied = True

            elif stacking == "replace":
                new_status.just_applied = True
                self.statuses.remove(current)
                self.statuses.append(new_status)
                applied = True

            elif stacking == "stack":
                if len(existing) < max_stacks:
                    new_status.just_applied = True
                    self.statuses.append(new_status)
                    applied = True
                else:
                    current.remaining_turns = max(
                        current.remaining_turns,
                        new_status.remaining_turns
                    )
                    applied = True
        
        if applied and combat_log is not None:
            combat_log.append({
                "event": "status_applied",
                "status": new_status.id,
                "target": self.name,
                "source": new_status.source
            })
        
        data = STATUS_REGISTRY.get(new_status.id, {})

        if (applied and data.get("interrupts")
            and hasattr(self, "locked_state")
            and self.locked_state
        ):
            # Determine resistance
            rarity = getattr(self, "rarity", None)
            resist_chance = 0.0

            if rarity is not None:
                resist_chance = INTERRUPT_RESISTANCE_BY_RARITY.get(rarity, 0.0)

            if random.random() < resist_chance:
                # Interrupt resisted
                if combat_log is not None:
                    combat_log.append({
                        "event": "interrupt_resisted",
                        "target": self.name,
                        "status": new_status.id,
                        "state": self.locked_state["state"],
                    })
            else:
                # Interrupt succeeds
                interrupted_state = self.locked_state["state"]
                self.locked_state = None

                if combat_log is not None:
                    combat_log.append({
                        "event": "interrupt",
                        "target": self.name,
                        "status": new_status.id,
                        "interrupted_state": interrupted_state,
                    })

        return applied
        
    def get_status_resistance(self, status_id: str) -> float:
        resist = 0.0
        key = f"{status_id}_resist"

        for item in self.equipment.values():
            if not item:
                continue
            resist += item.passive_modifiers.get(key, 0.0)

        # Cap to avoid total immunity
        return min(resist, 0.95)
    
    def get_effects_by_trigger(self, trigger: str) -> list[dict]:
        effects = []

        for item in self.equipment.values():
            if not item or not item.effect:
                continue

            for effect in item.effect:
                if effect.get("trigger") == trigger:
                    effects.append(effect)

        return effects

    def get_on_hit_effects(self):
        return self.get_effects_by_trigger("on_hit")

    def get_on_equip_effects(self):
        return self.get_effects_by_trigger("on_equip")

    def get_on_turn_effects(self):
        return self.get_effects_by_trigger("on_turn")



    def __str__(self):
        return f"name:{self.name}, hp:{self.hp}, damage:{self.damage}, level:{self.level}, defence: {self.defence}, equipment: {self.equipment}"
    