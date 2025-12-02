from game.core.Character_class import Character
from game.core.Enemy_class import Enemy
from typing import Optional


class Status():
    def __init__(self, id: str, remaining_turns: int, magnitude: int | dict | None, source: Optional[str] = None):
        self.id = id
        self.remaining_turns = remaining_turns
        self.source = source
        self.magnitude = magnitude


def _get_initiative_value(entity: Character) -> int:
    speed = getattr(entity, "speed", None)
    if speed is not None:
        return int(speed)
    if isinstance(entity, Character) and not isinstance(entity, Enemy):
        return 999
    return 0
