from enum import Enum

class Enemy_behavior_tag(Enum):
    NORMAL = "normal" # default state
    AGGRESSIVE = "aggressive"
    COWARDLY = "cowardly"
    RANGED = "ranged"
    SLOW = "slow"
    HULKING = "hulking"

