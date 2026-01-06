import random

from game.ui.dialog.dungeon_flavor_text import FLAVOR_TEXT


def pick_flavor(dungeon: str, category: str, tier: str) -> str:
    return random.choice(FLAVOR_TEXT[dungeon][category][tier])


def depth_tier(depth: int) -> str:
    if depth < 2:
        return "shallow"
    elif depth < 6:
        return "mid"
    else:
        return "deep"


def boss_tier(distance: int) -> str:
    if distance < 3:
        return "close"
    elif distance < 8:
        return "mid"
    else:
        return "far"
