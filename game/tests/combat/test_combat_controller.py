import unittest
from unittest.mock import patch

from game.core.character import Character
from game.core.Enemy_class import Enemy, Enemy_behavior_tag, Enemy_type, Enemy_sub_type
from game.core.Status import Enemy_Rarity
from game.systems.combat.combat_controller import Combat_State, start_encounter, get_available_enemy_skills, plan_enemy_intent, weighted_pick_enemy_skill, decide_enemy_action
from game.core.class_progression import SKILL_REGISTRY


def make_enemy(name="Goblin", hp=1):
    return Enemy(
        name=name,
        hp=hp,
        damage=1,
        defence=0,
        rarity=Enemy_Rarity.COMMON,
        type=Enemy_type.ENEMY_GOBLIN,
        sub_type=Enemy_sub_type.HUMANOID,
        xp_reward=10,
        gold_reward=1,
        loot_table=[],
    )

class TestCombatState(unittest.TestCase):
    def test_alive_enemies_filters_dead(self):
        player = Character("Hero", 10, 1, 1)
        e1 = make_enemy("Alive", hp=5)
        e2 = make_enemy("Dead", hp=0)

        combat = Combat_State(player, [e1, e2])

        alive = combat.alive_enemies()
        self.assertEqual(len(alive), 1)
        self.assertEqual(alive[0].name, "Alive")

class TestEncounterNoEnemies(unittest.TestCase):
    def test_start_encounter_no_enemies(self):
        player = Character("Hero", 10, 1, 1)

        class DummyRoom:
            contents = {"enemies": []}

        result = start_encounter(player, DummyRoom())

        self.assertEqual(result["result"], "no_enemies")

class TestEnemySkillAvailability(unittest.TestCase):
    def test_skill_filtered_by_cooldown(self):
        enemy = make_enemy()
        enemy.usable_skills = ["shield_bash"]
        enemy.skill_cooldowns = {"shield_bash": 2}

        combat = Combat_State(Character("Hero", 10, 1, 1), [enemy])

        skills = get_available_enemy_skills(enemy, combat)
        self.assertEqual(skills, [])

class TestEnemyIntentPlanning(unittest.TestCase):
    def test_enemy_without_skills_attacks(self):
        enemy = make_enemy()
        enemy.usable_skills = []

        combat = Combat_State(Character("Hero", 10, 1, 1), [enemy])

        plan_enemy_intent(enemy, combat)

        self.assertEqual(enemy.intent["type"], "attack")

class TestWeightedSkillPick(unittest.TestCase):
    @patch("random.choices")
    def test_weighted_pick_returns_skill(self, mock_choices):
        enemy = make_enemy()
        enemy.behavior_tag = Enemy_behavior_tag.NORMAL

        skill = SKILL_REGISTRY["shield_bash"]
        mock_choices.return_value = [skill]

        chosen = weighted_pick_enemy_skill(enemy, [skill])
        self.assertEqual(chosen, skill)

class TestDecideEnemyAction(unittest.TestCase):
    def test_locked_state_forces_wait(self):
        enemy = make_enemy()
        enemy.locked_state = {
            "skill_id": "shield_bash",
            "turns": 2,
            "forced_action": None,
        }

        combat = Combat_State(Character("Hero", 10, 1, 1), [enemy])
        action = decide_enemy_action(enemy, combat)

        self.assertEqual(action.type, "wait")

class TestCombatStateMutation(unittest.TestCase):
    def test_alive_enemies_updates_after_damage(self):
        player = Character("Hero", 10, 1, 1)
        enemy = make_enemy("Goblin", hp=5)

        combat = Combat_State(player, [enemy])

        enemy.take_damage(5)

        alive = combat.alive_enemies()
        self.assertEqual(alive, [])

