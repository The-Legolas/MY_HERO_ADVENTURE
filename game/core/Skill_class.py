from typing import Literal

SkillTarget = Literal[
    "self",
    "enemy",
    "all_enemies",
    "random_enemy"
]


class Skill:
    def __init__(self, id: str, name: str, description: str, target: SkillTarget, damage: dict | None = None,
                 hit_chance: float = 1.0, apply_status=None, effects=None,
                 trigger: Literal["immediate", "on_turn_start"] = "immediate", cost: dict | None = None,
                 forbid_if_target_has: list[str] = None, cooldown_turns: int = None, locks_actor: dict[str, str|int] = None,
                 allowed_while_locked: bool = None, requires_target_alive: bool = None, intent_hint: str = None, ):
        
        self.id = id
        self.name = name
        self.description = description
        self.target = target

        self.damage = damage
        self.hit_chance = hit_chance

        self.apply_status = apply_status
        self.effects = effects or []
        self.trigger = trigger
        self.cost = cost

        self.forbid_if_target_has = forbid_if_target_has or []
        self.cooldown_turns = cooldown_turns
        self.locks_actor = locks_actor
        self.allowed_while_locked = allowed_while_locked if allowed_while_locked is not None else False
        self.requires_target_alive = requires_target_alive if requires_target_alive is not None else True
        self.intent_hint = intent_hint if intent_hint is not None else None
