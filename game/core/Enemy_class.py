from enum import Enum
import random
from game.core.Character_class import Character

class Enemy_Rarity(Enum):
    COMMON = 100
    UNCOMMON = 40
    RARE = 15
    ELITE = 5
    MINI_BOSS = 2
    BOSS = 0

class Enemy_sub_type(Enum): #only 1 for don't know how many I'll add
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
        self.base_hp = hp
        self.type = type
        self.sub_type = sub_type
        self.rarity = rarity
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward

        self.level_scaling_factor = None # TBA

        self.loot_table = loot_table

        self.behavior_tag = behavior_tag if behavior_tag else Enemy_behavior_tag.NORMAL

        self.is_scaled = False

    
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

        self.hp = max(1, int(self.hp * day_counter_scaling))
        self.defence = max(0, int(self.defence * day_counter_scaling))
        self.damage = max(1, int(self.damage * depth_scaling))
        
        after_stats = {
        "hp": self.hp,
        "defence": self.defence,
        "damage": self.damage,
        }

        # Debug output
        self.debug_scaling(before_stats, after_stats, day_counter, depth)

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
        "behavior_tag": Enemy_behavior_tag.NORMAL
    },
    Enemy_type.ENEMY_SLIME: {
        "name": "Slime",
        "hp": 14,
        "damage": 2,
        "defence": 5,
        "rarity": Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.OOZE,
        "xp_reward": 50,
        "gold_reward": 2,
        "loot_table": [
            {"item": "slime_goop", "chance": 0.70},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "explosive_potion", "chance": 0.05},
        ],
        "behavior_tag": Enemy_behavior_tag.COWARDLY
    },
    Enemy_type.ENEMY_WOLF:  {
        "name": "Wolf",
        "hp": 23,
        "damage": 5,
        "defence": 3,
        "rarity": Enemy_Rarity.UNCOMMON,
        "sub_type": Enemy_sub_type.BEAST,
        "xp_reward": 60,
        "gold_reward": 3,
        "loot_table": [
            {"item": "wolf_tooth", "chance": 0.65},
            {"item": "small_healing_potion", "chance": 0.13},
            {"item": "medium_healing_potion", "chance": 0.07},
        ],
        "behavior_tag": Enemy_behavior_tag.AGGRESSIVE
    },
    Enemy_type.ENEMY_ORC: {
        "name": "Orc",
        "hp": 50,
        "damage": 7,
        "defence": 5,
        "rarity": Enemy_Rarity.RARE,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 100,
        "gold_reward": 20,
        "loot_table": [
            {"item": "goblin_ear", "chance": 0.25},
            {"item": "basic_armor", "chance": 0.10},
            {"item": "medium_healing_potion", "chance": 0.20},
        ],
        "behavior_tag": Enemy_behavior_tag.SLOW
    },
    Enemy_type.ENEMY_BOSS_DRAGON : {
        "name": "Dragon",
        "hp": 150,
        "damage": 40,
        "defence": 28,
        "rarity": Enemy_Rarity.BOSS,
        "sub_type": Enemy_sub_type.DRAGON,
        "xp_reward": 1800,
        "gold_reward": 450,
        "loot_table": [
            {"item": "improved_sword", "chance": 1.0},
            {"item": "grand_healing_potion", "chance": 0.5},
            {"item": "slime_goop", "chance": 0.001}
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
            type        = enemy_type ,
            sub_type    = template["sub_type"],
            xp_reward   = template["xp_reward"],
            gold_reward = template["gold_reward"],
            loot_table  = template["loot_table"],
            behavior_tag= template["behavior_tag"]
        )

    return enemy_obj



class Enemy_Spawner:
    
    def build_weight_table():
        weight_table = []

        for (enemy_type, data) in ENEMY_DEFINITIONS.items():
            rarity = data["rarity"]
            weight = rarity.value

            if weight == 0:
                continue

            weight_table.append((enemy_type, weight))
        
        return weight_table

    @staticmethod
    def get_random_template_weighted():
        weight_table = Enemy_Spawner.build_weight_table()

        total_weight = sum(weight for _, weight in weight_table)

        rnd_roll = random.uniform(0, total_weight)
        running_sum = 0

        for enemy_type, weight in weight_table:
            running_sum += weight

            if rnd_roll <= running_sum:
                return enemy_type
        
        return weight_table[-1][0]

