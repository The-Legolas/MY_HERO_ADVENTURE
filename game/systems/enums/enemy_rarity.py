from enum import Enum

class Enemy_Rarity(Enum):
    COMMON = 90 #100
    UNCOMMON = 40 #40
    RARE = 20 # 15
    ELITE = 5
    MINI_BOSS = 2 # 2
    BOSS = 0
    DEBUG = 0

INTERRUPT_RESISTANCE_BY_RARITY = {
    Enemy_Rarity.COMMON: 0.0,   # no resistance
    Enemy_Rarity.ELITE: 0.5,    # 50% chance to resist interrupt
    Enemy_Rarity.BOSS: 1.0,     # full immunity
}
