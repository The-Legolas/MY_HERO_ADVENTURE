
from enum import Enum

class Status():
    def __init__(self, id: str, remaining_turns: int, magnitude: int | dict | None, source: str | None = None, expires_end_of_turn: bool = False):
        self.id = id
        self.remaining_turns = remaining_turns
        self.source = source
        self.magnitude = magnitude
        self.just_applied = True
        self.expires_end_of_turn = expires_end_of_turn

class Enemy_Rarity(Enum):
    COMMON = 50000 #100
    UNCOMMON = 40 #40
    RARE = 20 # 15
    ELITE = 5
    MINI_BOSS = 2
    BOSS = 0

INTERRUPT_RESISTANCE_BY_RARITY = {
    Enemy_Rarity.COMMON: 0.0,   # no resistance
    Enemy_Rarity.ELITE: 0.5,    # 50% chance to resist interrupt
    Enemy_Rarity.BOSS: 1.0,     # full immunity
}