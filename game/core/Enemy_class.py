#from __future__ import annotations
from game.core.character import Character

from game.systems.enums.enemy_type import Enemy_type
from game.systems.enums.enemy_sub_type import Enemy_sub_type
from game.systems.enums.enemy_behavior_tag import Enemy_behavior_tag
from game.systems.enums.enemy_rarity import Enemy_Rarity


class Enemy(Character):
    def __init__(self, name: str, hp: int, damage: int, 
                 defence: int, rarity: Enemy_Rarity, 
                 type: Enemy_type, sub_type: Enemy_sub_type, xp_reward: int, gold_reward: int, loot_table: list[dict[str, any]],
                 behavior_tag: Enemy_behavior_tag | None = None):
        super().__init__(name, hp, damage, defence)
        self.type = type
        self.sub_type = sub_type
        self.rarity = rarity
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward

        self.level_scaling_factor = None # TBA

        self.loot_table = loot_table

        self.behavior_tag = behavior_tag if behavior_tag else Enemy_behavior_tag.NORMAL

        self.is_scaled = False

        self.skill_cooldowns: dict[str, int] = {}
        self.locked_state: dict | None = None

        self.intent: dict | None = None
        self.status_affinities: dict[str, str] = {}



    def tick_skill_cooldowns(self) -> None:
        expired = []

        for skill_id, turns in self.skill_cooldowns.items():
            self.skill_cooldowns[skill_id] -= 1
            if self.skill_cooldowns[skill_id] <= 0:
                expired.append(skill_id)

        for skill_id in expired:
            del self.skill_cooldowns[skill_id]


    def scale_stats(self, day_counter: int, depth: int) -> None:
        if self.is_scaled == True:
            return
        
        before_stats = {
            "hp": self.hp,
            "defence": self.defence,
            "damage": self.damage,
        }   

        day_counter = max(1, day_counter)
        depth = max(0, abs(depth))

        day_counter_scaling = 1 + (day_counter / 100)
        depth_scaling = 1 + (depth / 50)

        scaled_hp = max(1, int(self.base_hp * day_counter_scaling))
        self.hp = scaled_hp
        self.base_hp = scaled_hp

        self.base_defence = max(0, int(self.defence * day_counter_scaling))
        self.base_damage = max(1, int(self.damage * depth_scaling))
        
        after_stats = {
        "hp": self.hp,
        "defence": self.defence,
        "damage": self.damage,
        }

        # Debug output
        #self.debug_scaling(before_stats, after_stats, day_counter, depth)

        self.is_scaled = True

    def debug_scaling(self, before, after, day_counter, depth):
        print("=== Enemy Scaling Debug ===")
        print(f"Name: {self.name}")
        print(f"Day Counter: {day_counter}")
        print(f"Depth: {depth}")
        print("--- BEFORE ---")
        print(f"HP: {before['hp']}, DEF: {before['defence']}, DMG: {before['damage']}")
        print("--- AFTER ---")
        print(f"HP: {after['hp']}, DEF: {after['defence']}, DMG: {after['damage']}")
        print("===========================\n")

        

