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
    ENEMY_FORGOTTEN_CHAMPION = "forgotten champion"
    ENEMY_CORRUPTED_GUARDIAN = "corrupted guardian"
    ENEMY_ASH_DRAKE = "ash drake"
    ENEMY_LICHBOUND_KNIGHT = "lichbound knight"
    ENEMY_DARK_TEMPLAR_INQUISITOR = "dark templar inquisitor"
    ENEMY_WIGHT_CHAMPION = "wight champion"
    ENEMY_DARK_TEMPLAR = "dark templar"
    ENEMY_GELATINOUS_SENTINEL = "gelatinous sentinel"
    ENEMY_DIRE_WOLF = "dire wolf"
    ENEMY_DEAD_WARDEN = "dead warden"
    ENEMY_DIRE_BOAR = "dire boar"
    ENEMY_SHAMBLING_CORPSE = "shambling corpse"


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
        "defence": 3,
        "rarity": Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 50,
        "gold_reward": 20,
        "loot_table": [
            {"item": "goblin_ear", "chance": 0.60},
            {"item": "boar_tusk", "chance": 0.40},
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
        "rarity": Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.OOZE,
        "xp_reward": 50,
        "gold_reward": 10,
        "loot_table": [
            {"item": "slime_goop", "chance": 0.70},
            {"item": "hardened_slime_core", "chance": 0.20},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "explosive_potion", "chance": 0.05},
        ],
        "usable_skills": [
            "engulf",
            "acid_splash",
            "corrosive_buildup",
            "dissolve_armor"
        ],
        "status_affinities": {
            "poison": "immune",
            "bleed": "immune",
            "acid": "vulnerable",
        },
        "behavior_tag": Enemy_behavior_tag.COWARDLY
    },

    Enemy_type.ENEMY_SHAMBLING_CORPSE: {
        "name": "Shambling Corpse",
        "hp": 28,
        "damage": 4,
        "defence": 2,
        "rarity": Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.UNDEAD,
        "xp_reward": 45,
        "gold_reward": 5,
        "loot_table": [
            {"item": "rotted_bone", "chance": 0.60},
            {"item": "broken_helm", "chance": 0.45},
            {"item": "small_healing_potion", "chance": 0.10},
        ],
        "usable_skills": [
            "rotting_claw",
            "grave_resilience",
        ],
        "status_affinities": {
            "poison": "immune",
            "bleed": "immune",
            "burn": "normal",
        },
        "behavior_tag": Enemy_behavior_tag.SLOW
    },

    Enemy_type.ENEMY_DIRE_BOAR: {
        "name": "Dire Boar",
        "hp": 40,
        "damage": 6,
        "defence": 4,
        "rarity": Enemy_Rarity.COMMON,
        "sub_type": Enemy_sub_type.BEAST,
        "xp_reward": 60,
        "gold_reward": 6,
        "loot_table": [
            {"item": "matted_hide", "chance": 0.60},
            {"item": "boar_tusk", "chance": 0.60},
            {"item": "small_healing_potion", "chance": 0.10},
        ],
        "usable_skills": [
            "rending_bite",
            "pounce",
        ],
        "status_affinities": {
            "stun": "resistant",
            "weakened": "vulnerable",
            "burn": "vulnerable",
        },
        "behavior_tag": Enemy_behavior_tag.AGGRESSIVE
    },


    Enemy_type.ENEMY_DEAD_WARDEN: {
        "name": "Dead Warden",
        "hp": 55,
        "damage": 6,
        "defence": 9,
        "rarity": Enemy_Rarity.UNCOMMON,
        "sub_type": Enemy_sub_type.UNDEAD,
        "xp_reward": 90,
        "gold_reward": 10,
        "loot_table": [
            {"item": "broken_helm", "chance": 0.60},
            {"item": "rotted_bone", "chance": 0.60},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "medium_healing_potion", "chance": 0.05},
        ],
        "usable_skills": [
            "rotting_claw",
            "grave_resilience",
            "grave_chill",
            "death_coil",
        ],
        "status_affinities": {
            "poison": "immune",
            "armor_down": "resistant",
        },
        "behavior_tag": Enemy_behavior_tag.SLOW
    },

    Enemy_type.ENEMY_DIRE_WOLF: {
        "name": "Dire Wolf",
        "hp": 32,
        "damage": 7,
        "defence": 3,
        "rarity": Enemy_Rarity.UNCOMMON,
        "sub_type": Enemy_sub_type.BEAST,
        "xp_reward": 75,
        "gold_reward": 6,
        "loot_table": [
            {"item": "matted_hide", "chance": 0.60},
            {"item": "wolf_tooth", "chance": 0.60},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "medium_healing_potion", "chance": 0.05},
        ],
        "usable_skills": [
            "rending_bite",
            "poison_bite",
            "pounce",
            "savage_howl",
            "tear_flesh",
        ],
        "status_affinities": {
            "bleed": "vulnerable",
            "stun": "normal",
        },
        "behavior_tag": Enemy_behavior_tag.AGGRESSIVE
    },

    Enemy_type.ENEMY_GELATINOUS_SENTINEL: {
        "name": "Gelatinous Sentinel",
        "hp": 60,
        "damage": 5,
        "defence": 12,
        "rarity": Enemy_Rarity.UNCOMMON,
        "sub_type": Enemy_sub_type.OOZE,
        "xp_reward": 110,
        "gold_reward": 8,
        "loot_table": [
            {"item": "slime_goop", "chance": 0.70},
            {"item": "hardened_slime_core", "chance": 0.60},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "medium_healing_potion", "chance": 0.05},
        ],
        "usable_skills": [
            "engulf",
            "acid_splash",
            "corrosive_buildup",
            "dissolve_armor",
            "gelatinous_recovery"
        ],
        "status_affinities": {
            "poison": "immune",
            "bleed": "immune",
            "burn": "vulnerable",
        },
        "behavior_tag": Enemy_behavior_tag.SLOW
    },


    Enemy_type.ENEMY_WOLF:  {
        "name": "Wolf",
        "hp": 23,
        "damage": 5,
        "defence": 3,
        "rarity": Enemy_Rarity.UNCOMMON, #Enemy_Rarity.UNCOMMON,
        "sub_type": Enemy_sub_type.BEAST,
        "xp_reward": 60,
        "gold_reward": 3,
        "loot_table": [
            {"item": "matted_hide", "chance": 0.60},
            {"item": "wolf_tooth", "chance": 0.65},
            {"item": "small_healing_potion", "chance": 0.10},
            {"item": "medium_healing_potion", "chance": 0.05},
        ],
        "usable_skills": [
            "rending_bite",
            "poison_bite",
            "pounce",
            "savage_howl",
            "tear_flesh",
        ],
        "behavior_tag": Enemy_behavior_tag.AGGRESSIVE
    },

    Enemy_type.ENEMY_DARK_TEMPLAR: {
        "name": "Dark Templar",
        "hp": 45,
        "damage": 8,
        "defence": 6,
        "rarity": Enemy_Rarity.RARE,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 120,
        "gold_reward": 18,
        "loot_table": [
            {"item": "tarnished_insignia", "chance": 0.80},
            {"item": "broken_helm", "chance": 0.30},
            {"item": "medium_healing_potion", "chance": 0.15},
            {"item": "grand_healing_potion", "chance": 0.02},
            {"item": "explosive_potion", "chance": 0.00005},
            {"item": "lesser_fortitude_draught", "chance": 0.00005},
            {"item": "elixir_of_battle_focus", "chance": 0.00005},
            {"item": "antivenom_vial", "chance": 0.00005},
            {"item": "volatile_concoction", "chance": 0.00005},
            {"item": "sluggish_brew", "chance": 0.00005},
            {"item": "poison_flask", "chance": 0.00005},
            {"item": "strength_elixir", "chance": 0.00005},
            {"item": "regeneration_draught", "chance": 0.00005},
        ],
        "usable_skills": [
            "bloodletting_slash",
            "shield_wall",
            "battle_shout",
        ],
        "status_affinities": {
            "stun": "resistant",
            "weakened": "resistant",
            "poison": "normal",
            "bleed": "normal",
        },
        "behavior_tag": Enemy_behavior_tag.NORMAL
    },

    Enemy_type.ENEMY_WIGHT_CHAMPION: {
        "name": "Wight Champion",
        "hp": 70,
        "damage": 10,
        "defence": 7,
        "rarity": Enemy_Rarity.RARE,
        "sub_type": Enemy_sub_type.UNDEAD,
        "xp_reward": 160,
        "gold_reward": 30,
        "loot_table": [
            {"item": "broken_helm", "chance": 0.60},
            {"item": "medium_healing_potion", "chance": 0.15},
            {"item": "grand_healing_potion", "chance": 0.02},
            {"item": "explosive_potion", "chance": 0.00005},
            {"item": "lesser_fortitude_draught", "chance": 0.00005},
            {"item": "elixir_of_battle_focus", "chance": 0.00005},
            {"item": "antivenom_vial", "chance": 0.00005},
            {"item": "volatile_concoction", "chance": 0.00005},
            {"item": "sluggish_brew", "chance": 0.00005},
            {"item": "poison_flask", "chance": 0.00005},
            {"item": "strength_elixir", "chance": 0.00005},
            {"item": "regeneration_draught", "chance": 0.00005},
        ],
        "usable_skills": [
            "grave_resilience",
            "grave_chill",
            "death_coil",
            "withering_touch",
            "shield_wall"
        ],
        "status_affinities": {
            "poison": "immune",
            "weakened": "resistant",
            "burn": "normal",
        },
        "behavior_tag": Enemy_behavior_tag.HULKING
    },

    Enemy_type.ENEMY_DARK_TEMPLAR_INQUISITOR: {
        "name": "Dark Templar Inquisitor",
        "hp": 65,
        "damage": 9,
        "defence": 8,
        "rarity": Enemy_Rarity.ELITE,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 180,
        "gold_reward": 35,
        "loot_table": [
            {"item": "bloodletter_axe", "chance": 0.05},
            {"item": "ashen_drake_claw", "chance": 0.40},
            {"item": "tarnished_insignia", "chance": 0.80},
            {"item": "tarnished_insignia", "chance": 0.10},
            {"item": "broken_helm", "chance": 0.60},
            {"item": "medium_healing_potion", "chance": 0.24},
            {"item": "grand_healing_potion", "chance": 0.13},
            {"item": "explosive_potion", "chance": 0.0005},
            {"item": "lesser_fortitude_draught", "chance": 0.0005},
            {"item": "elixir_of_battle_focus", "chance": 0.0005},
            {"item": "antivenom_vial", "chance": 0.0005},
            {"item": "volatile_concoction", "chance": 0.0005},
            {"item": "sluggish_brew", "chance": 0.0005},
            {"item": "poison_flask", "chance": 0.0005},
            {"item": "strength_elixir", "chance": 0.0005},
            {"item": "regeneration_draught", "chance": 0.0005},
        ],
        "usable_skills": [
            "bloodletting_slash",
            "shield_wall",
            "battle_shout",
            "cracking_blow"
        ],
        "status_affinities": {
            "stun": "resistant",
            "poison": "resistant",
            "weakened": "normal",
        },
        "behavior_tag": Enemy_behavior_tag.SLOW
    },

    Enemy_type.ENEMY_LICHBOUND_KNIGHT: {
        "name": "Lichbound Knight",
        "hp": 85,
        "damage": 11,
        "defence": 10,
        "rarity": Enemy_Rarity.ELITE,
        "sub_type": Enemy_sub_type.UNDEAD,
        "xp_reward": 220,
        "gold_reward": 45,
        "loot_table": [
            {"item": "frostbrand_sword", "chance": 0.05},
            {"item": "medium_healing_potion", "chance": 0.24},
            {"item": "grand_healing_potion", "chance": 0.13},
            {"item": "explosive_potion", "chance": 0.0005},
            {"item": "lesser_fortitude_draught", "chance": 0.0005},
            {"item": "elixir_of_battle_focus", "chance": 0.0005},
            {"item": "antivenom_vial", "chance": 0.0005},
            {"item": "volatile_concoction", "chance": 0.0005},
            {"item": "sluggish_brew", "chance": 0.0005},
            {"item": "poison_flask", "chance": 0.0005},
            {"item": "strength_elixir", "chance": 0.0005},
            {"item": "regeneration_draught", "chance": 0.0005},
        ],
        "usable_skills": [
            "grave_resilience",
            "grave_chill",
            "death_coil",
            "withering_touch",
            "shield_wall"
            "tear_flesh",
        ],
        "status_affinities": {
            "stun": "resistant",
            "poison": "immune",
        },
        "behavior_tag": Enemy_behavior_tag.HULKING
    },

    Enemy_type.ENEMY_ORC: {
        "name": "Orc",
        "hp": 50,
        "damage": 7,
        "defence": 5,
        "rarity": Enemy_Rarity.ELITE,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 100,
        "gold_reward": 20,
        "loot_table": [
            {"item": "ring_of_corruption", "chance": 0.05},
            {"item": "goblin_ear", "chance": 0.25},
            {"item": "medium_healing_potion", "chance": 0.35},
            {"item": "grand_healing_potion", "chance": 0.20},
            {"item": "explosive_potion", "chance": 0.0005},
            {"item": "lesser_fortitude_draught", "chance": 0.0005},
            {"item": "elixir_of_battle_focus", "chance": 0.0005},
            {"item": "antivenom_vial", "chance": 0.0005},
            {"item": "volatile_concoction", "chance": 0.0005},
            {"item": "sluggish_brew", "chance": 0.0005},
            {"item": "poison_flask", "chance": 0.0005},
            {"item": "strength_elixir", "chance": 0.0005},
            {"item": "regeneration_draught", "chance": 0.0005},
        ],
        "usable_skills": [
            "dirty_strike",
            "battle_shout",
            "cracking_blow",
            "shield_wall",
        ],
        "behavior_tag": Enemy_behavior_tag.SLOW
    },

    Enemy_type.ENEMY_ASH_DRAKE: {
        "name": "Ash Drake",
        "hp": 110,
        "damage": 14,
        "defence": 10,
        "rarity": Enemy_Rarity.MINI_BOSS,
        "sub_type": Enemy_sub_type.DRAGON,
        "xp_reward": 350,
        "gold_reward": 90,
        "loot_table": [
            {"item": "ring_of_vital_flow", "chance": 0.05},
            {"item": "ashen_drake_claw", "chance": 0.50},
            {"item": "charred_scale", "chance": 0.59},
            {"item": "medium_healing_potion", "chance": 0.35},
            {"item": "grand_healing_potion", "chance": 0.20},
            {"item": "explosive_potion", "chance": 0.0005},
            {"item": "lesser_fortitude_draught", "chance": 0.0005},
            {"item": "elixir_of_battle_focus", "chance": 0.0005},
            {"item": "antivenom_vial", "chance": 0.0005},
            {"item": "volatile_concoction", "chance": 0.0005},
            {"item": "sluggish_brew", "chance": 0.0005},
            {"item": "poison_flask", "chance": 0.0005},
            {"item": "strength_elixir", "chance": 0.0005},
            {"item": "regeneration_draught", "chance": 0.0005},
        ],
        "usable_skills": [
            "flame_breath",
            "terrifying_roar",
            "skyward_ascension",
            "molten_scales",
            "searing_presence",
        ],
        "status_affinities": {
            "burn": "immune",
            "poison": "resistant",
        },
        "behavior_tag": Enemy_behavior_tag.HULKING
    },

    Enemy_type.ENEMY_CORRUPTED_GUARDIAN: {
        "name": "Corrupted Guardian",
        "hp": 130,
        "damage": 12,
        "defence": 14,
        "rarity": Enemy_Rarity.MINI_BOSS,
        "sub_type": Enemy_sub_type.HUMANOID,
        "xp_reward": 380,
        "gold_reward": 110,
        "loot_table": [
            {"item": "cracked_warhammer", "chance": 0.05},
            {"item": "medium_healing_potion", "chance": 0.35},
            {"item": "grand_healing_potion", "chance": 0.20},
            {"item": "explosive_potion", "chance": 0.0005},
            {"item": "lesser_fortitude_draught", "chance": 0.0005},
            {"item": "elixir_of_battle_focus", "chance": 0.0005},
            {"item": "antivenom_vial", "chance": 0.0005},
            {"item": "volatile_concoction", "chance": 0.0005},
            {"item": "sluggish_brew", "chance": 0.0005},
            {"item": "poison_flask", "chance": 0.0005},
            {"item": "strength_elixir", "chance": 0.0005},
            {"item": "regeneration_draught", "chance": 0.0005},
        ],
        "usable_skills": [
            "dirty_strike",
            "battle_shout",
            "cracking_blow",
            "shield_wall",
            "bloodletting_slash",
        ],
        "status_affinities": {
            "stun": "resistant",
            "armor_down": "resistant",
        },
        "behavior_tag": Enemy_behavior_tag.SLOW
    },

    Enemy_type.ENEMY_FORGOTTEN_CHAMPION: {
        "name": "Forgotten Champion",
        "hp": 140,
        "damage": 13,
        "defence": 11,
        "rarity": Enemy_Rarity.MINI_BOSS,
        "sub_type": Enemy_sub_type.UNDEAD,
        "xp_reward": 400,
        "gold_reward": 130,
        "loot_table": [
            {"item": "ring_of_iron_will", "chance": 0.05},
            {"item": "medium_healing_potion", "chance": 0.35},
            {"item": "grand_healing_potion", "chance": 0.20},
            {"item": "explosive_potion", "chance": 0.0005},
            {"item": "lesser_fortitude_draught", "chance": 0.0005},
            {"item": "elixir_of_battle_focus", "chance": 0.0005},
            {"item": "antivenom_vial", "chance": 0.0005},
            {"item": "volatile_concoction", "chance": 0.0005},
            {"item": "sluggish_brew", "chance": 0.0005},
            {"item": "poison_flask", "chance": 0.0005},
            {"item": "strength_elixir", "chance": 0.0005},
            {"item": "regeneration_draught", "chance": 0.0005},
        ],
        "usable_skills": [
            "grave_resilience",
            "grave_chill",
            "death_coil",
            "withering_touch",
            "shield_wall"
            "tear_flesh",
            "battle_shout",
            "bloodletting_slash",
        ],
        "status_affinities": {
            "poison": "immune",
            "bleed": "resistant",
            "burn": "vulnerable",
        },
        "behavior_tag": Enemy_behavior_tag.HULKING
    },

    Enemy_type.ENEMY_BOSS_DRAGON : {
        "name": "Dragon",
        "hp": 240,
        "damage": 23,
        "defence": 19,
        "rarity": Enemy_Rarity.BOSS,
        "sub_type": Enemy_sub_type.DRAGON,
        "xp_reward": 1800,
        "gold_reward": 450,
        "loot_table": [
            {"item": "slime_goop", "chance": 0.001}
        ],
        "usable_skills": [
            "flame_breath",
            "terrifying_roar",
            "cataclysmic_slam",
            "molten_scales",
            "searing_presence",
            "crushing_bite",
            "raking_talons",
            "ancient_fury",
            "smoldering_regeneration",
            "inferno_surge",
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


