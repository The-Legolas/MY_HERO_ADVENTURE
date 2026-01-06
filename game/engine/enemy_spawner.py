import random

from game.core.Enemy_class import Enemy

from game.systems.enums.enemy_rarity import Enemy_Rarity

from game.definitions.enemy_definitions import ENEMY_DEFINITIONS


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



