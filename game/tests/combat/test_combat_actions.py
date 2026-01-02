import unittest
from unittest.mock import patch

from game.systems.combat.combat_actions import Action, resolve_action, _compute_escape_chance
from game.core.Enemy_class import Enemy_behavior_tag


class DummyCombatState:
    def __init__(self, actor, enemies):
        self.player = actor
        self.enemy_list = enemies
        self.log = []
        self.is_running = True

class DummyActor:
    def __init__(self, name="Hero", hp=100, damage=10):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.defence = 0
        self.resource_name = "mana"
        self.resource_current = 100
        self.usable_skills = []
        self.skill_cooldowns = {}
        self.behavior_tag = None

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def get_damage_multiplier(self):
        return 1.0

    def get_on_hit_effects(self):
        return []

    def apply_status(self, status, log=None):
        return {"applied": True, "status": status.id}

class TestAttackAction(unittest.TestCase):
    @patch("game.systems.combat.combat_actions.resolve_damage")
    def test_attack_action_logs_outcome(self, mock_resolve):
        actor = DummyActor()
        target = DummyActor(name="Enemy")

        mock_resolve.return_value = {
            "damage": 10,
            "blocked": False,
            "critical": False,
            "died": False,
        }

        combat = DummyCombatState(actor, [target])
        action = Action(actor, "attack", target)

        outcome = resolve_action(action, combat)

        self.assertEqual(outcome["action"], "attack")
        self.assertEqual(outcome["damage"], 10)
        self.assertEqual(len(combat.log), 1)

class TestDeadActor(unittest.TestCase):
    def test_dead_actor_noop(self):
        actor = DummyActor(hp=0)
        combat = DummyCombatState(actor, [])

        action = Action(actor, "attack", None)
        outcome = resolve_action(action, combat)

        self.assertEqual(outcome["action"], "noop")

class TestSkillResourceCheck(unittest.TestCase):
    def test_skill_fails_without_resource(self):
        actor = DummyActor()
        actor.resource_current = 0

        combat = DummyCombatState(actor, [])
        action = Action(actor, "skill", None, skill_id="shield_bash")

        outcome = resolve_action(action, combat)

        self.assertEqual(outcome["action"], "skill_fail")

class TestDefendAction(unittest.TestCase):
    def test_defend_applies_status(self):
        actor = DummyActor()
        combat = DummyCombatState(actor, [])

        action = Action(actor, "defend", None)
        outcome = resolve_action(action, combat)

        self.assertEqual(outcome["action"], "defend")
        self.assertEqual(len(combat.log), 1)

class TestFleeAction(unittest.TestCase):
    @patch("random.random", return_value=0.0)
    @patch("random.uniform", return_value=0.0)
    def test_flee_success_stops_combat(self, *_):
        actor = DummyActor()
        enemy = DummyActor(name="Enemy")
        enemy.behavior_tag = Enemy_behavior_tag.NORMAL

        combat = DummyCombatState(actor, [enemy])
        action = Action(actor, "flee", None)

        outcome = resolve_action(action, combat)

        self.assertTrue(outcome["extra"]["escaped"])
        self.assertFalse(combat.is_running)

class TestEscapeChance(unittest.TestCase):
    @patch("random.uniform", return_value=0.0)
    @patch("random.random", return_value=0.0)
    def test_escape_chance_returns_bool(self, *_):
        enemy = DummyActor()
        enemy.behavior_tag = Enemy_behavior_tag.AGGRESSIVE

        combat = DummyCombatState(None, [enemy])
        result = _compute_escape_chance(combat)

        self.assertIsInstance(result, bool)

