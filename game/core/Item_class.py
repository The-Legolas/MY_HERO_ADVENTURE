from game.core.Status import Status

from game.systems.enums.item_type import Item_Type
from game.systems.util_funcs.item_class_utils import EFFECT_ACTIONS, apply_remove_status



def item_make_outcome(actor_name, action, target_name=None, damage=0, blocked=False, critical=False, died=False, extra=None):
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


class Items():
    def __init__(self, name: str, category: Item_Type, stackable: bool, unique: bool,
                 stats: dict[str, any] | None = None, effect: dict[str, any] | None = None, 
                 passive_modifiers: dict[str, float] | None = None,
                 on_hit_status: dict | None = None, value: int = 0):
        self.id = None
        self.name = name
        self.category = category
        self.stackable = stackable
        self.unique = unique
        self.value = value

        self.effect = effect
        self.stats = stats or {}
        self.passive_modifiers = passive_modifiers or {}
        self.on_hit_status = on_hit_status
    
    def get_tooltip(self) -> str:
        lines = []

        if self.stats:
            for k, v in self.stats.items():
                name = k.replace("_", " ").title()

                if isinstance(v, float):
                    lines.append(f"\t{name}: +{int(v * 100)}%")
                else:
                    sign = "+" if v > 0 else ""
                    lines.append(f"\t{name}: {sign}{v}")

        if self.passive_modifiers:
            for k, v in self.passive_modifiers.items():
                name = k.replace("_", " ").replace("resist", "Resist").title()
                lines.append(f"\t{name}: +{int(v * 100)}%")

        if not self.effect:
            return "\n".join(lines)

        # CONSUMABLE EFFECTS (dict)
        if isinstance(self.effect, dict):
            summary_parts = []
            detail_lines = []

            if "apply_status" in self.effect:
                status_data = self.effect["apply_status"]
                status_name = status_data["id"].replace("_", " ").title()
                duration = status_data.get("duration")

                summary_parts.append(f"applies {status_name.lower()}")
                if duration:
                    detail_lines.append(f"\t• {status_name} for {duration} turns")
                else:
                    detail_lines.append(f"\t• {status_name}")

            if "heal" in self.effect:
                amount = self.effect["heal"]
                summary_parts.append("restores health")
                detail_lines.append(f"\t• Heals {amount} HP")

            if "damage" in self.effect:
                amount = self.effect["damage"]
                summary_parts.append("deals damage")
                detail_lines.append(f"\t• Deals {amount} damage")

            if "remove_status" in self.effect:
                status = self.effect["remove_status"].replace("_", " ").title()
                summary_parts.append(f"cures {status.lower()}")
                detail_lines.append(f"\t• Removes {status}")

            if "restore_resource" in self.effect:
                amount = self.effect["restore_resource"]
                summary_parts.append("restores stamina")
                detail_lines.append(f"\t• Restores {amount} stamina")

            if summary_parts:
                lines.append(f"\tUse: {' and '.join(summary_parts).capitalize()}")
                for d in detail_lines:
                    lines.append(f"  {d}")

            return "\n".join(lines)

        # TRIGGERED / PASSIVE EFFECTS (list)
        if isinstance(self.effect, list):
            for entry in self.effect:
                trigger = entry.get("trigger", "unknown")
                chance = entry.get("chance", 1.0)
                status = entry.get("status")

                if not status:
                    continue

                status_name = status["id"].replace("_", " ").title()
                duration = status.get("duration")

                trigger_text = {
                    "on_hit": "On hit",
                    "on_equip": "On equip",
                    "on_turn": "Each turn",
                }.get(trigger, trigger.replace("_", " ").title())

                line = f"\t{trigger_text}: {status_name}"
                
                if duration is not None:
                    if duration < 0:
                        line += " (while equipped)"
                    else:
                        line += f" ({duration} turns)"

                if chance < 1.0:
                    line += f" — {int(chance * 100)}% chance"

                lines.append(line)

            return "\n".join(lines)

        return "\n".join(lines)



    def use(self, player, target):
        if not self.effect:
            return item_make_outcome(player.name, "use_item_fail", getattr(target, "name", None),
                                extra={"reason": "not_consumable", "item": self.name})
        
        if self.category != Item_Type.CONSUMABLE:
            return item_make_outcome(player.name, "use_item_fail", getattr(target, "name", None),
                                extra={"reason": "no_effect", "item": self.name})
        
        did_something = False        

        total_damage = 0
        total_heal = 0
        details = []

        if isinstance(self.effect, dict):
            for effect_type, amount in self.effect.items():
                if effect_type in ("heal", "damage"):
                    action = EFFECT_ACTIONS.get(effect_type)
                    if not action:
                        continue

                    action(target, amount)

                    if effect_type == "heal":
                        total_heal += amount
                    elif effect_type == "damage":
                        total_damage += amount
                        
                    details.append({
                        "effect": effect_type,
                        "amount": amount
                    })

                    did_something = True
                    continue

                if effect_type == "apply_status":
                    status = Status(
                        id=amount["id"],
                        remaining_turns=amount["duration"],
                        magnitude=amount.get("magnitude"),
                        source=self.name
                    )

                    result = target.apply_status(status)

                    details.append({
                        "effect": "apply_status",
                        "status": status.id,
                        "applied": result
                    })

                    if result:
                        did_something = True
                    continue

                if effect_type == "remove_status":
                    success = apply_remove_status(target, amount)

                    details.append({
                        "effect": "remove_status",
                        "status": amount,
                        "success": success
                    })

                    if success:
                        did_something = True
                    continue

                if effect_type == "restore_resource":
                    before = target.resource_current
                    target.resource_current = min(
                        target.resource_max,
                        target.resource_current + amount
                    )

                    details.append({
                        "effect": "restore_resource",
                        "amount": amount,
                        "before": before,
                        "after": target.resource_current,
                    })

                    did_something = True
                    continue

            if not did_something:
                return item_make_outcome(
                    player.name,
                    "use_item_fail",
                    getattr(target, "name", None),
                    extra={"reason": "no_effect", "item": self.name}
                )

            return item_make_outcome(
                player.name,
                "use_item",
                getattr(target, "name", None),
                damage=total_damage,
                blocked=False,
                critical=False,
                died=hasattr(target, "is_alive") and not target.is_alive(),
                extra={
                    "item": self.name,
                    "details": details
                }
            )

        # CASE 2 — status effects
        elif isinstance(self.effect, list):
            for entry in self.effect:
                if entry.get("type") != "status":
                    continue

                status_data = entry.get("status")
                if not status_data:
                    continue

                status = Status(
                    id=status_data["id"],
                    remaining_turns=status_data["duration"],
                    magnitude=status_data.get("magnitude"),
                    source=self.name
                )

                result = target.apply_status(status)
                if result:
                    did_something = True

                details.append({
                    "effect": "status",
                    "status": status.id,
                    "applied": result
                })

        if did_something:
            return item_make_outcome(
                player.name,
                "use_item",
                getattr(target, "name", None),
                damage=total_damage,
                blocked=False,
                critical=False,
                died=hasattr(target, "is_alive") and not target.is_alive(),
                extra={
                    "item": self.name,
                    "details": details
                }
            )

        return item_make_outcome(
            player.name,
            "use_item_fail",
            getattr(target, "name", None),
            extra={
                "reason": "no_effect",
                "item": self.name
            }
        )
        
