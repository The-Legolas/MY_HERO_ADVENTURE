import unittest
from unittest.mock import patch

from game.systems.combat.damage_resolver import resolve_damage
from game.systems.combat.status_evaluator import evaluate_status_magnitude
from game.systems.combat.status_registry import STATUS_REGISTRY
from game.core.Status import Status
from game.systems.combat.combat_turn import _get_initiative_value
from game.core.character import Character
from game.core.Enemy_class import Enemy
from game.core.Status import Enemy_Rarity
from game.core.Enemy_class import Enemy_type, Enemy_sub_type


class DummyCharacter:
    def __init__(self, hp=100, damage=10, defence=0):
        self.hp = hp
        self.damage = damage
        self.defence = defence

    def get_damage_multiplier(self):
        return 1.0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def is_alive(self):
        return self.hp > 0

class TestDamageResolverGuards(unittest.TestCase):
    def test_no_target_returns_no_damage(self):
        result = resolve_damage(None, None, None)

        self.assertEqual(result["damage"], 0)
        self.assertFalse(result["blocked"])
        self.assertFalse(result["critical"])
        self.assertFalse(result["died"])

class TestFlatDamage(unittest.TestCase):
    def test_flat_damage_applies(self):
        actor = DummyCharacter(damage=10)
        target = DummyCharacter(hp=50, defence=0)

        damage_def = {
            "type": "flat",
            "amount": 15,
            "can_crit": False,
        }

        result = resolve_damage(actor, target, damage_def)

        self.assertEqual(result["damage"], 15)
        self.assertEqual(target.hp, 35)
        self.assertFalse(result["blocked"])

class TestMultiplierDamage(unittest.TestCase):
    def test_multiplier_damage_uses_actor_stat(self):
        actor = DummyCharacter(damage=20)
        target = DummyCharacter(hp=50, defence=0)

        damage_def = {
            "type": "multiplier",
            "stat": "damage",
            "mult": 0.5,
            "can_crit": False,
        }

        result = resolve_damage(actor, target, damage_def)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(target.hp, 40)

class TestHybridDamage(unittest.TestCase):
    def test_hybrid_damage(self):
        actor = DummyCharacter(damage=10)
        target = DummyCharacter(hp=50, defence=0)

        damage_def = {
            "type": "hybrid",
            "base": 5,
            "stat": "damage",
            "mult": 0.5,
            "can_crit": False,
        }

        result = resolve_damage(actor, target, damage_def)

        self.assertEqual(result["damage"], 10)

class TestDefenseBlock(unittest.TestCase):
    def test_damage_fully_blocked(self):
        actor = DummyCharacter(damage=5)
        target = DummyCharacter(hp=50, defence=10)

        damage_def = {
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
        }

        result = resolve_damage(actor, target, damage_def)

        self.assertTrue(result["blocked"])
        self.assertEqual(result["damage"], 0)
        self.assertEqual(target.hp, 50)

class TestCriticalHit(unittest.TestCase):
    @patch("random.random", return_value=0.99)
    def test_critical_doubles_damage(self, _):
        actor = DummyCharacter(damage=10)
        target = DummyCharacter(hp=50, defence=0)

        damage_def = {
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
            "can_crit": True,
        }

        result = resolve_damage(actor, target, damage_def)

        self.assertTrue(result["critical"])
        self.assertEqual(result["damage"], 20)

class TestDeathDetection(unittest.TestCase):
    def test_target_death_flag(self):
        actor = DummyCharacter(damage=50)
        target = DummyCharacter(hp=10, defence=0)

        damage_def = {
            "type": "multiplier",
            "stat": "damage",
            "mult": 1.0,
        }

        result = resolve_damage(actor, target, damage_def)

        self.assertTrue(result["died"])
        self.assertFalse(target.is_alive())



class TestStatusEvaluatorBase(unittest.TestCase):
    def test_no_interactions_returns_base_value(self):
        status = Status(
            id="burn",
            remaining_turns=3,
            magnitude=10,
            source="test"
        )

        with patch.dict(
            "game.systems.combat.status_registry.STATUS_REGISTRY",
            {},
            clear=True
        ):
            value = evaluate_status_magnitude(status, [])

        self.assertEqual(value, 10)

class TestStatusEvaluatorInteractions(unittest.TestCase):
    def test_single_interaction_multiplier(self):
        status = Status("poison", 3, 10, "test")
        other = Status("vulnerable", 2, None, "test")

        registry = {
            "poison": {
                "interactions": {
                    "vulnerable": {
                        "damage_multiplier": 1.5
                    }
                }
            }
        }

        with patch.dict(
            "game.systems.combat.status_registry.STATUS_REGISTRY",
            registry,
            clear=True
        ):
            value = evaluate_status_magnitude(status, [other])

        self.assertEqual(value, 15)

    def test_multiple_interactions_multiply(self):
        status = Status("bleed", 3, 10, "test")
        other_a = Status("vulnerable", 2, None, "test")
        other_b = Status("exposed", 1, None, "test")

        registry = {
            "bleed": {
                "interactions": {
                    "vulnerable": {"damage_multiplier": 1.5},
                    "exposed": {"damage_multiplier": 2.0},
                }
            }
        }

        with patch.dict(
            "game.systems.combat.status_registry.STATUS_REGISTRY",
            registry,
            clear=True
        ):
            value = evaluate_status_magnitude(status, [other_a, other_b])

        self.assertEqual(value, 30)

    def test_non_matching_status_ignored(self):
        status = Status("burn", 3, 10, "test")
        other = Status("shielded", 2, None, "test")

        registry = {
            "burn": {
                "interactions": {
                    "vulnerable": {"damage_multiplier": 2.0}
                }
            }
        }

        with patch.dict(
            "game.systems.combat.status_registry.STATUS_REGISTRY",
            registry,
            clear=True
        ):
            value = evaluate_status_magnitude(status, [other])

        self.assertEqual(value, 10)
    
    def test_interaction_without_multiplier_is_ignored(self):
        status = Status("burn", 3, 10, "test")
        other = Status("vulnerable", 2, None, "test")

        registry = {
            "burn": {
                "interactions": {
                    "vulnerable": {}
                }
            }
        }

        with patch.dict(
            "game.systems.combat.status_registry.STATUS_REGISTRY",
            registry,
            clear=True
        ):
            value = evaluate_status_magnitude(status, [other])

        self.assertEqual(value, 10)


class TestStatusRegistryStructure(unittest.TestCase):
    def test_registry_is_non_empty(self):
        self.assertTrue(STATUS_REGISTRY)

    def test_registry_keys_are_strings(self):
        for key in STATUS_REGISTRY:
            self.assertIsInstance(key, str)

    def test_registry_values_are_dicts(self):
        for value in STATUS_REGISTRY.values():
            self.assertIsInstance(value, dict)

class TestStatusRegistryKeys(unittest.TestCase):
    def test_known_fields_have_correct_types(self):
        for status_id, data in STATUS_REGISTRY.items():
            if "priority" in data:
                self.assertIsInstance(data["priority"], int)

            if "stacking" in data:
                self.assertIn(data["stacking"], {"replace", "refresh", "stack"})

            if "max_stacks" in data:
                self.assertIsInstance(data["max_stacks"], int)

            if "prevents_action" in data:
                self.assertIsInstance(data["prevents_action"], bool)

            if "is_debuff" in data:
                self.assertIsInstance(data["is_debuff"], bool)

class TestStatusRegistryOnTick(unittest.TestCase):
    def test_on_tick_is_callable_if_present(self):
        for status_id, data in STATUS_REGISTRY.items():
            if "on_tick" in data:
                self.assertTrue(callable(data["on_tick"]), status_id)

class TestStatusModifiers(unittest.TestCase):
    def test_modifiers_are_numeric(self):
        for status_id, data in STATUS_REGISTRY.items():
            modifiers = data.get("modifiers")
            if not modifiers:
                continue

            self.assertIsInstance(modifiers, dict)
            for key, value in modifiers.items():
                self.assertIsInstance(value, (int, float))

class TestStatusInteractions(unittest.TestCase):
    def test_interactions_schema(self):
        for status_id, data in STATUS_REGISTRY.items():
            interactions = data.get("interactions")
            if not interactions:
                continue

            self.assertIsInstance(interactions, dict)

            for other_status, rule in interactions.items():
                self.assertIsInstance(other_status, str)
                self.assertIsInstance(rule, dict)

                if "damage_multiplier" in rule:
                    self.assertIsInstance(rule["damage_multiplier"], (int, float))

class TestStatusConsistency(unittest.TestCase):
    def test_stack_status_has_max_stacks(self):
        for status_id, data in STATUS_REGISTRY.items():
            if data.get("stacking") == "stack":
                self.assertIn("max_stacks", data, status_id)

    def test_interrupting_status_prevents_action(self):
        for status_id, data in STATUS_REGISTRY.items():
            if data.get("interrupts"):
                self.assertTrue(data.get("prevents_action", False), status_id)

class TestInitiativeExplicitSpeed(unittest.TestCase):
    def test_entity_with_speed_uses_speed(self):
        char = Character("Hero", hp=10, damage=1, defence=1)
        char.speed = 42

        self.assertEqual(_get_initiative_value(char), 42)

class TestInitiativePlayerDefault(unittest.TestCase):
    def test_player_without_speed_gets_high_priority(self):
        char = Character("Hero", hp=10, damage=1, defence=1)

        self.assertEqual(_get_initiative_value(char), 999)

class TestInitiativeEnemyDefault(unittest.TestCase):
    def test_enemy_without_speed_gets_zero(self):
        enemy = Enemy(
            name="Goblin",
            hp=10,
            damage=1,
            defence=1,
            rarity=Enemy_Rarity.COMMON,
            type=Enemy_type.ENEMY_GOBLIN,
            sub_type=Enemy_sub_type.HUMANOID,
            xp_reward=10,
            gold_reward=1,
            loot_table=[],
        )

        self.assertEqual(_get_initiative_value(enemy), 0)

class TestInitiativeEnemyWithSpeed(unittest.TestCase):
    def test_enemy_speed_overrides_zero(self):
        enemy = Enemy(
            name="Fast Goblin",
            hp=10,
            damage=1,
            defence=1,
            rarity=Enemy_Rarity.COMMON,
            type=Enemy_type.ENEMY_GOBLIN,
            sub_type=Enemy_sub_type.HUMANOID,
            xp_reward=10,
            gold_reward=1,
            loot_table=[],
        )
        enemy.speed = 7

        self.assertEqual(_get_initiative_value(enemy), 7)
