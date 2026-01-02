from game.core.character import Character
from game.core.Enemy_class import Enemy


def _get_initiative_value(entity: 'Character') -> int:
    speed = getattr(entity, "speed", None)
    if speed is not None:
        return int(speed)
    if isinstance(entity, Character) and not isinstance(entity, Enemy):
        return 999
    return 0
