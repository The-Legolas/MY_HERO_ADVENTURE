from __future__ import annotations
from enum import Enum
import random
from game.core.Status import Enemy_Rarity
from typing import TYPE_CHECKING

from game.core.character import Character


class Enemy_sub_type(Enum):
    UNDEAD = "undead"
    HUMANOID = "humanoid"
    OOZE = "ooze"
    BEAST = "beast"
    DRAGON = "dragon"

class Enemy_type(Enum):
    ENEMY_GOBLIN = "goblin"
    ENEMY_SLIME = "slime"
    ENEMY_WOLF = "wolf"
    ENEMY_ORC = "orc"
    ENEMY_BOSS_DRAGON = "dragon boss"


class Enemy_behavior_tag(Enum):
    NORMAL = "normal" # default state
    AGGRESSIVE = "aggressive"
    COWARDLY = "cowardly"
    RANGED = "ranged"
    SLOW = "slow"
    HULKING = "hulking"



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

        


ENEMY_DEFINITIONS = {
    Enemy_type.ENEMY_GOBLIN: {
        "name": "Goblin",
        "hp": 20,
        "damage": 4,
        "defence": 1,
        "rarity": Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 50,
        "gold_reward": 3,
        "loot_table": [
            {"item": "goblin_ear", "chance": 0.60},
            {"item": "small_healing_potion", "chance": 0.10},
        ],
        "usable_skills": [
            "dirty_strike",
            "battle_shout",
            "shield_wall"
        ],
        "behavior_tag": Enemy_behavior_tag.NORMAL
    },
    Enemy_type.ENEMY_SLIME: {
        "name": "Slime",
        "hp": 14,
        "damage": 2,
        "defence": 5,
        "rarity": Enemy_Rarity.COMMON, #Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.OOZE,
        "xp_reward": 50,
        "gold_reward": 2,
        "loot_table": [
            {"item": "slime_goop", "chance": 0.70},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "explosive_potion", "chance": 0.05},
        ],
        "usable_skills": [
            "engulf",
            "acid_splash",
            "corrosive_buildup",
        ],
        "status_affinities": {
            "poison": "immune",
            "bleed": "immune",
            "acid": "vulnerable",
        },
        "behavior_tag": Enemy_behavior_tag.COWARDLY
    },
    Enemy_type.ENEMY_WOLF:  {
        "name": "Wolf",
        "hp": 23,
        "damage": 5,
        "defence": 3,
        "rarity": Enemy_Rarity.MINI_BOSS, #Enemy_Rarity.UNCOMMON,
        "sub_type": Enemy_sub_type.BEAST,
        "xp_reward": 60,
        "gold_reward": 3,
        "loot_table": [
            {"item": "wolf_tooth", "chance": 0.65},
            {"item": "small_healing_potion", "chance": 0.13},
            {"item": "medium_healing_potion", "chance": 0.07},
        ],
        "usable_skills": [
            "rending_bite",
            "poison_bite",
            "pounce",
            "savage_howl",
        ],
        "behavior_tag": Enemy_behavior_tag.AGGRESSIVE
    },
    Enemy_type.ENEMY_ORC: {
        "name": "Orc",
        "hp": 50,
        "damage": 7,
        "defence": 5,
        "rarity": Enemy_Rarity.MINI_BOSS, #Rare
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 100,
        "gold_reward": 20,
        "loot_table": [
            {"item": "goblin_ear", "chance": 0.25},
            {"item": "basic_armor", "chance": 0.10},
            {"item": "medium_healing_potion", "chance": 0.20},
        ],
        "usable_skills": [
            "dirty_strike",
            "battle_shout",
        ],
        "behavior_tag": Enemy_behavior_tag.SLOW
    },
    Enemy_type.ENEMY_BOSS_DRAGON : {
        "name": "Dragon",
        "hp": 150,
        "damage": 20,
        "defence": 15,
        "rarity": Enemy_Rarity.BOSS,
        "sub_type": Enemy_sub_type.DRAGON,
        "xp_reward": 1800,
        "gold_reward": 450,
        "loot_table": [
            {"item": "improved_sword", "chance": 1.0},
            {"item": "grand_healing_potion", "chance": 0.5},
            {"item": "slime_goop", "chance": 0.001}
        ],
        "usable_skills": [
            "flame_breath",
            "terrifying_roar",
            "skyward_ascension",
        ],
        "behavior_tag": Enemy_behavior_tag.HULKING
    }
}

def spawn_enemy(enemy_type):
    template = ENEMY_DEFINITIONS[enemy_type].copy()

    enemy_obj = Enemy(
            name        = template["name"],
            hp          = template["hp"],
            damage      = template["damage"],
            defence     = template["defence"],
            rarity      = template["rarity"],
            type        = enemy_type,
            sub_type    = template["sub_type"],
            xp_reward   = template["xp_reward"],
            gold_reward = template["gold_reward"],
            loot_table  = template["loot_table"],
            behavior_tag= template["behavior_tag"]
        )
    enemy_obj.usable_skills = template.get("usable_skills", []).copy()
    enemy_obj.status_affinities = template.get("status_affinities", {}).copy()

    return enemy_obj


class Enemy_Spawner:

    @staticmethod
    def build_weight_table(forbid_rarities: set[Enemy_Rarity] | None = None):
        weight_table = []

        for enemy_type, data in ENEMY_DEFINITIONS.items():
            rarity = data["rarity"]

            if forbid_rarities and rarity in forbid_rarities:
                continue

            weight = rarity.value

            if weight <= 0:
                continue

            weight_table.append((enemy_type, weight))
        
        return weight_table

    @staticmethod
    def get_random_template_weighted(forbid_rarities: set[Enemy_Rarity] | None = None):
        weight_table = Enemy_Spawner.build_weight_table(forbid_rarities)

        total_weight = sum(weight for _, weight in weight_table)
        rnd_roll = random.uniform(0, total_weight)

        running_sum = 0
        for enemy_type, weight in weight_table:
            running_sum += weight
            if rnd_roll <= running_sum:
                return enemy_type
        
        return weight_table[-1][0]
    
    @staticmethod
    def get_random_miniboss_template():
        minibosses = [
            enemy_type
            for enemy_type, data in ENEMY_DEFINITIONS.items()
            if data["rarity"] == Enemy_Rarity.MINI_BOSS
        ]
        return random.choice(minibosses)


