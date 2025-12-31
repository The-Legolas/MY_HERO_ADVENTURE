import random
from game.core.Item_class import Item_Type, Items, make_outcome, ITEM_DEFINITIONS
from game.systems.combat.status_evaluator import evaluate_status_magnitude
from game.systems.combat.status_registry import STATUS_REGISTRY
from game.systems.combat.damage_resolver import resolve_damage
from game.core.Status import INTERRUPT_RESISTANCE_BY_RARITY
from game.core.class_progression import CLASS_PROGRESSION, SKILL_REGISTRY

from game.core.Status import Status

STAT_VALUE_GETTERS = {
    "hp": lambda c: c.max_hp,
    "damage": lambda c: c.damage,
    "defence": lambda c: c.defence,
}


class Character():
    def __init__(self, name: str, hp: int, damage: int, defence: int, starting_items: dict[str, int] | None = None, gold: int = 0):
        self.name = name
        self.base_hp = hp
        self.hp = hp

        self.base_damage = damage
        self.base_defence = defence

        self.level = 1
        self.xp = 0
        self.STAT_VALUE_GETTERS = 0
        self.class_id:str | None = None
        self.level_bonuses: dict[str, int] = {
            "hp": 0,
            "damage": 0,
            "defence": 0,
        }


        self.skills: dict[str, dict] = {}

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
            "gold": gold
        }

        if starting_items:
            for item_id, count in starting_items.items():
                data = ITEM_DEFINITIONS.get(item_id)
                if not data:
                    raise ValueError(f"Unknown item ID: {item_id}")
                
                item = Items(
                name=data["name"],
                category=data["category"],
                stackable=data.get("stackable", False),
                unique=data.get("unique", False),
                stats=data.get("stats"),
                effect=data.get("effect"),
                passive_modifiers=data.get("passive_modifiers"),
                on_hit_status=data.get("on_hit_status"),
                value=data.get("value", 0),
            )

                self.inventory["items"][item_id] = {
                    "item": item,
                    "count": count
                }
    @property
    def max_hp(self) -> int:
        return self.base_hp + self.level_bonuses.get("hp", 0)


    @property
    def damage(self) -> int:
        return self.base_damage + self.level_bonuses.get("damage", 0)


    @property
    def defence(self) -> int:
        return self.base_defence + self.level_bonuses.get("defence", 0)


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

    def use_item(self, item_id: str, target: 'Character') -> None:
        entry = self.inventory["items"].get(item_id)
        if not entry:
            return make_outcome(
                self.name,
                "use_item_fail",
                getattr(target, "name", None),
                extra={"reason": "missing_item", "item": item_id}
            )

        item = entry["item"]
        outcome = item.use(self, target)

        # Consume item only on success
        if outcome and outcome.get("action") == "use_item":
            self.remove_item(item_id, amount=1)

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
        self.hp = min(self.max_hp, self.hp + amount)


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

    def gain_xp(self, amount: int) -> list[dict]:
        if self.class_id is None:
            return []
    
        progression = CLASS_PROGRESSION[self.class_id]
        xp_table = progression["xp_per_level"]
        level_cap = progression["level_cap"]

        self.xp += amount
        level_ups: list[dict] = []
        
        while self.level < level_cap:
            next_level = self.level + 1

            if next_level >= len(xp_table):
                break

            if self.xp < xp_table[self.level]:
                break

            self.level = next_level
            reward_data = self.apply_level_rewards(self.level)

            if reward_data:
                level_ups.append(reward_data)

        return level_ups
    
        
    def apply_level_rewards(self, level: int) -> dict | None:
        progression = CLASS_PROGRESSION[self.class_id]
        rewards = progression["level_rewards"].get(level)

        if not rewards:
            return
        
        result = {
            "level": level,
            "stats": {},
            "skills": [],
        }
        
        for stat, value in rewards.get("stats", {}).items():
            if stat not in self.level_bonuses:
                raise ValueError(f"Unknown stat bonus: {stat}")
            
            getter = STAT_VALUE_GETTERS[stat]

            old_value = getter(self)
            self.level_bonuses[stat] += value
            new_value = getter(self)

            if stat == "hp":
                self.hp = new_value


            result["stats"][stat] = {
                "old": old_value,
                "new": new_value,
            }

        for skill_id in rewards.get("skills", []):
            self.unlock_skill(skill_id)
            result["skills"].append(skill_id)

        return result
    
    def unlock_skill(self, skill_id: str) -> None:
        if skill_id in self.known_skills:
            return

        self.known_skills.add(skill_id)
        self.usable_skills.append(skill_id)


    def reset_progression(self) -> None:
        self.level = 1
        self.xp = 0

        self.level_bonuses = {
            "hp": 0,
            "damage": 0,
            "defence": 0,
        }

        self.known_skills.clear()
        self.usable_skills.clear()

        self.apply_level_rewards(1)

        self.hp = min(self.hp, self.max_hp)

    def set_level(self, target_level: int) -> None:
        progression = CLASS_PROGRESSION[self.class_id]
        level_cap = progression["level_cap"]

        target_level = max(1, min(target_level, level_cap))

        self.reset_progression()

        for lvl in range(2, target_level + 1):
            self.level = lvl
            self.apply_level_rewards(lvl)

        self.xp = progression["xp_per_level"][self.level]

        self.hp = min(self.hp, self.max_hp)

    def render_level_up_screen(self, level_data: dict) -> None:
        print("\n" + "=" * 30)
        print(f"LEVEL UP!  →  Level {level_data['level']}")
        print("=" * 30)

        if level_data["stats"]:
            print("\nStats increased:")
            for stat, values in level_data["stats"].items():
                name = stat.replace("_", " ").title()
                print(f" - {name}: {values['old']} → {values['new']}")

        if level_data["skills"]:
            print("\nNew skills unlocked:")
            for skill_id in level_data["skills"]:
                skill = SKILL_REGISTRY.get(skill_id)
                name = skill.name if skill else skill_id
                print(f" - {name}")

        input("\nPress Enter to continue...")


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
        data = STATUS_REGISTRY.get(new_status.id, {})
        stacking = data.get("stacking", "replace")
        max_stacks = data.get("max_stacks", 1)

        affinity = getattr(self, "status_affinities", {}).get(new_status.id, "normal")

        # IMMUNITY
        if affinity == "immune":
            if combat_log is not None:
                combat_log.append({
                    "event": "status_immune",
                    "status": new_status.id,
                    "target": self.name,
                })
            return {
                "applied": False,
                "reason": "immune",
                "status": new_status.id,
            }
        
        # AFFINITY MODIFIERS
        chance = data.get("chance", 1.0)
        duration = new_status.remaining_turns

        if affinity == "resistant":
            chance *= 0.5
            duration = max(1, duration - 1)
            if combat_log is not None:
                combat_log.append({
                    "event": "status_weakened",
                    "status": new_status.id,
                    "target": self.name,
                })


        elif affinity == "vulnerable":
            chance = min(1.0, chance * 1.5)
            duration += 1
            if combat_log is not None:
                combat_log.append({
                    "event": "status_exploited",
                    "status": new_status.id,
                    "target": self.name,
                })


        new_status.remaining_turns = duration

        # RESISTANCE ROLL
        resist = self.get_status_resistance(new_status.id)
        if resist > 0 and random.random() < resist:
            if combat_log is not None:
                combat_log.append({
                    "event": "status_resisted",
                    "status": new_status.id,
                    "target": self.name
                })
            return False
        if random.random() > chance:
            return {
                "applied": False,
                "reason": "resisted",
                "status": new_status.id,
            }

        # FIND EXISTING STATUS
        current = next((s for s in self.statuses if s.id == new_status.id), None)
        
        applied = False

        # STACKING LOGIC
        if not current:
            new_status.just_applied = True
            self.statuses.append(new_status)
            applied = True

        elif stacking == "replace":
            self.statuses.remove(current)
            new_status.just_applied = True
            self.statuses.append(new_status)
            applied = True

        elif stacking == "refresh":
            new_mag = new_status.magnitude or 0
            cur_mag = current.magnitude or 0

            if new_mag > cur_mag:
                self.statuses.remove(current)
                new_status.just_applied = True
                self.statuses.append(new_status)
                applied = True

            elif new_mag == cur_mag:
                current.remaining_turns = max(
                    current.remaining_turns,
                    new_status.remaining_turns
                )
                applied = True

        elif stacking == "stack":
            added_stacks = new_status.remaining_turns
            current.remaining_turns = min(
                current.remaining_turns + added_stacks,
                max_stacks
            )
            applied = True
        
        # LOG APPLICATION
        if applied and combat_log is not None:
            combat_log.append({
                "event": "status_applied",
                "status": new_status.id,
                "target": self.name,
                "source": new_status.source
            })
        

        # INTERRUPTS
        if applied and data.get("interrupts") and hasattr(self, "locked_state") and self.locked_state:
            rarity = getattr(self, "rarity", None)
            resist_chance = INTERRUPT_RESISTANCE_BY_RARITY.get(rarity, 0.0) if rarity else 0.0
            interrupted_skill = self.locked_state.get("skill_id")

            if random.random() < resist_chance:
                if combat_log is not None:
                    combat_log.append({
                        "event": "interrupt_resisted",
                        "target": self.name,
                        "status": new_status.id,
                        "skill": interrupted_skill,
                    })
            else:
                self.locked_state = None
                if combat_log is not None:
                    combat_log.append({
                        "event": "interrupt",
                        "target": self.name,
                        "status": new_status.id,
                        "skill": interrupted_skill,
                    })

        return {
            "applied": True,
            "status": new_status.id,
            "affinity": affinity,
        }
        
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
    