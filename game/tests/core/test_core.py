import unittest
from unittest.mock import patch
from enum import Enum

from game.core.character import Character
from game.core.Heroes import Warrior
from game.core.Skill_class import Skill
from game.core.Item_class import item_make_outcome, Items
from game.core.Status import Status

from game.definitions.class_progression import CLASS_PROGRESSION
from game.definitions.enemy_definitions import ENEMY_DEFINITIONS
from game.definitions.skill_registry import SKILL_REGISTRY

from game.systems.enums.enemy_rarity import Enemy_Rarity, INTERRUPT_RESISTANCE_BY_RARITY
from game.systems.enums.enemy_type import Enemy_type
from game.systems.enums.enemy_sub_type import Enemy_sub_type
from game.systems.enums.enemy_behavior_tag import Enemy_behavior_tag
from game.systems.enums.item_type import Item_Type

from game.systems.util_funcs.roll_random import roll_loot

from game.engine.item_spawner import spawn_item
from game.engine.enemy_spawner import Enemy_Spawner, spawn_enemy


class TestCharacterCoreStats(unittest.TestCase):
    def setUp(self):
        self.char = Character(
            name="Hero",
            hp=100,
            damage=10,
            defence=5
        )

    def test_initial_stats(self):
        self.assertEqual(self.char.hp, 100)
        self.assertEqual(self.char.max_hp, 100)
        self.assertEqual(self.char.damage, 10)
        self.assertEqual(self.char.defence, 5)

    def test_take_damage_never_negative(self):
        self.char.take_damage(999)
        self.assertEqual(self.char.hp, 0)

    def test_heal_never_exceeds_max_hp(self):
        self.char.take_damage(50)
        self.char.heal(999)
        self.assertEqual(self.char.hp, self.char.max_hp)

    def test_is_alive(self):
        self.assertTrue(self.char.is_alive())
        self.char.take_damage(100)
        self.assertFalse(self.char.is_alive())


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.char = Character("Hero", 100, 10, 5)

        self.potion = Items(
            name="Potion",
            category=Item_Type.CONSUMABLE,
            stackable=True,
            unique=False,
            stats=None,
            effect=None,
            passive_modifiers={},
            on_hit_status=None,
            value=10
        )
        self.potion.id = "potion"

    def test_add_stackable_item(self):
        self.char.add_item(self.potion, 2)
        self.assertEqual(self.char.inventory["items"]["potion"]["count"], 2)

    def test_remove_stackable_item(self):
        self.char.add_item(self.potion, 2)
        self.char.remove_item("potion", 1)
        self.assertEqual(self.char.inventory["items"]["potion"]["count"], 1)

    def test_remove_item_to_zero_deletes_entry(self):
        self.char.add_item(self.potion, 1)
        self.char.remove_item("potion", 1)
        self.assertNotIn("potion", self.char.inventory["items"])


class TestEquipmentStats(unittest.TestCase):
    def setUp(self):
        self.char = Character("Hero", 100, 10, 5)

        self.sword = Items(
            name="Sword",
            category=Item_Type.WEAPON,
            stackable=False,
            unique=False,
            stats={"damage": 5},
            effect=None,
            passive_modifiers={},
            on_hit_status=None,
            value=100
        )
        self.sword.id = "sword"

        self.char.add_item(self.sword)

    @patch("builtins.input", lambda *_: None)
    def test_equip_weapon_increases_damage(self):
        self.char.equip_item(self.sword)
        self.assertEqual(self.char.damage, 15)

    @patch("builtins.input", lambda *_: None)
    def test_unequip_weapon_restores_damage(self):
        self.char.equip_item(self.sword)
        self.char.unequip_item(self.sword)
        self.assertEqual(self.char.damage, 10)


class TestProgression(unittest.TestCase):
    def setUp(self):
        self.char = Character("Hero", 100, 10, 5)
        self.char.class_id = "warrior"

    def test_gain_xp_levels_up(self):
        xp_table = CLASS_PROGRESSION["warrior"]["xp_per_level"]
        self.char.gain_xp(xp_table[1])
        self.assertGreaterEqual(self.char.level, 2)

    def test_set_level_bounds(self):
        self.char.set_level(999)
        cap = CLASS_PROGRESSION["warrior"]["level_cap"]
        self.assertEqual(self.char.level, cap)


class TestStatusApplication(unittest.TestCase):
    def setUp(self):
        self.char = Character("Hero", 100, 10, 5)

    @patch("random.random", return_value=0.0)
    def test_apply_status_success(self, _):
        status = Status(
            id="poison",
            remaining_turns=2,
            magnitude=5,
            source="test"
        )
        result = self.char.apply_status(status)
        self.assertTrue(result["applied"])
        self.assertTrue(self.char.has_status("poison"))

    def test_clear_negative_statuses(self):
        self.char.statuses.append(Status("poison", 1, 5, "test"))
        self.char.clear_negative_statuses()
        self.assertEqual(len(self.char.statuses), 0)

class TestWarriorInitialization(unittest.TestCase):
    def test_warrior_base_setup(self):
        w = Warrior("Conan")

        self.assertEqual(w.class_id, "warrior")
        self.assertGreater(w.max_hp, 70)
        self.assertEqual(w.resource_current, w.resource_max)
        self.assertTrue(len(w.usable_skills) > 0)


class TestWarriorDamageReduction(unittest.TestCase):
    def setUp(self):
        self.warrior = Warrior("Conan")

    def test_take_damage_is_reduced(self):
        starting_hp = self.warrior.hp
        self.warrior.take_damage(10)

        expected_damage = int(10 * 0.9)
        self.assertEqual(self.warrior.hp, starting_hp - expected_damage)

class TestStatusObject(unittest.TestCase):
    def test_status_initialization(self):
        status = Status(
            id="test_status",
            remaining_turns=3,
            magnitude=5,
            source="unit_test"
        )

        self.assertEqual(status.id, "test_status")
        self.assertEqual(status.remaining_turns, 3)
        self.assertEqual(status.magnitude, 5)
        self.assertEqual(status.source, "unit_test")
        self.assertTrue(status.just_applied)
        self.assertFalse(status.expires_end_of_turn)

    def test_status_expires_end_of_turn_flag(self):
        status = Status(
            id="temp",
            remaining_turns=1,
            magnitude=None,
            expires_end_of_turn=True
        )

        self.assertTrue(status.expires_end_of_turn)


class TestEnemyRarityEnum(unittest.TestCase):
    def test_enemy_rarity_values(self):
        self.assertEqual(Enemy_Rarity.COMMON.value, 90)
        self.assertEqual(Enemy_Rarity.ELITE.value, 5)
        self.assertEqual(Enemy_Rarity.BOSS.value, 0)

    def test_enemy_rarity_is_enum(self):
        self.assertTrue(issubclass(Enemy_Rarity, Enum))


class TestInterruptResistanceByRarity(unittest.TestCase):
    def test_known_rarity_resistance_values(self):
        self.assertEqual(INTERRUPT_RESISTANCE_BY_RARITY[Enemy_Rarity.COMMON], 0.0)
        self.assertEqual(INTERRUPT_RESISTANCE_BY_RARITY[Enemy_Rarity.ELITE], 0.5)
        self.assertEqual(INTERRUPT_RESISTANCE_BY_RARITY[Enemy_Rarity.BOSS], 1.0)

    def test_resistance_values_are_valid_probabilities(self):
        for value in INTERRUPT_RESISTANCE_BY_RARITY.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

class TestSkillInitialization(unittest.TestCase):
    def test_minimal_skill_initialization(self):
        skill = Skill(
            id="test_skill",
            name="Test Skill",
            description="A test skill",
            target="enemy"
        )

        self.assertEqual(skill.id, "test_skill")
        self.assertEqual(skill.name, "Test Skill")
        self.assertEqual(skill.description, "A test skill")
        self.assertEqual(skill.target, "enemy")

        self.assertIsNone(skill.damage)
        self.assertEqual(skill.hit_chance, 1.0)
        self.assertIsNone(skill.apply_status)
        self.assertEqual(skill.trigger, "immediate")
        self.assertIsNone(skill.cost)

        self.assertEqual(skill.forbid_if_target_has, [])
        self.assertIsNone(skill.cooldown_turns)
        self.assertIsNone(skill.locks_actor)
        self.assertFalse(skill.allowed_while_locked)
        self.assertTrue(skill.requires_target_alive)
        self.assertIsNone(skill.intent_hint)


class TestSkillOptionalFields(unittest.TestCase):
    def test_full_skill_initialization(self):
        skill = Skill(
            id="poison_strike",
            name="Poison Strike",
            description="Deals damage and poisons the target",
            target="enemy",
            damage={"type": "flat", "amount": 5},
            hit_chance=0.8,
            apply_status={"id": "poison", "duration": 3},
            trigger="immediate",
            cost={"resource": "stamina", "amount": 10},
            forbid_if_target_has=["poison"],
            cooldown_turns=2,
            locks_actor={"skill_id": "poison_strike", "turns": 1},
            allowed_while_locked=True,
            requires_target_alive=False,
            intent_hint="Apply poison"
        )

        self.assertEqual(skill.damage["amount"], 5)
        self.assertEqual(skill.hit_chance, 0.8)
        self.assertEqual(skill.apply_status["id"], "poison")
        self.assertEqual(skill.cost["amount"], 10)
        self.assertEqual(skill.forbid_if_target_has, ["poison"])
        self.assertEqual(skill.cooldown_turns, 2)
        self.assertEqual(skill.locks_actor["turns"], 1)
        self.assertTrue(skill.allowed_while_locked)
        self.assertFalse(skill.requires_target_alive)
        self.assertEqual(skill.intent_hint, "Apply poison")


class TestSkillDefaultSafety(unittest.TestCase):
    def test_forbid_list_is_not_shared_between_instances(self):
        skill_a = Skill(
            id="a",
            name="A",
            description="A",
            target="enemy"
        )
        skill_b = Skill(
            id="b",
            name="B",
            description="B",
            target="enemy"
        )

        skill_a.forbid_if_target_has.append("burn")

        self.assertEqual(skill_a.forbid_if_target_has, ["burn"])
        self.assertEqual(skill_b.forbid_if_target_has, [])

class TestMakeOutcome(unittest.TestCase):
    def test_item_make_outcome_structure(self):
        result = item_make_outcome(
            actor_name="Hero",
            action="use_item",
            target_name="Enemy",
            damage=5,
            blocked=True,
            critical=False,
            died=True,
            extra={"key": "value"}
        )

        self.assertEqual(result["actor"], "Hero")
        self.assertEqual(result["action"], "use_item")
        self.assertEqual(result["target"], "Enemy")
        self.assertEqual(result["damage"], 5)
        self.assertTrue(result["blocked"])
        self.assertFalse(result["critical"])
        self.assertTrue(result["died"])
        self.assertEqual(result["extra"]["key"], "value")

class TestItemInitialization(unittest.TestCase):
    def test_item_defaults(self):
        item = Items(
            name="Potion",
            category=Item_Type.CONSUMABLE,
            stackable=True,
            unique=False
        )

        self.assertIsNone(item.id)
        self.assertEqual(item.name, "Potion")
        self.assertEqual(item.category, Item_Type.CONSUMABLE)
        self.assertTrue(item.stackable)
        self.assertFalse(item.unique)
        self.assertEqual(item.stats, {})
        self.assertEqual(item.passive_modifiers, {})
        self.assertIsNone(item.effect)

class DummyTarget:
    def __init__(self, name="Dummy"):
        self.name = name
        self.hp = 10

    def heal(self, amount):
        self.hp += amount

    def is_alive(self):
        return self.hp > 0


class TestConsumableHealing(unittest.TestCase):
    def test_healing_item(self):
        item = Items(
            name="Potion",
            category=Item_Type.CONSUMABLE,
            stackable=True,
            unique=False,
            effect={"heal": 5}
        )

        player = DummyTarget()
        target = DummyTarget()

        outcome = item.use(player, target)

        self.assertEqual(target.hp, 15)
        self.assertEqual(outcome["action"], "use_item")
        self.assertEqual(outcome["damage"], 0)

class TestConsumableDamage(unittest.TestCase):
    def test_damage_item(self):
        item = Items(
            name="Bomb",
            category=Item_Type.CONSUMABLE,
            stackable=True,
            unique=False,
            effect={"damage": 5}
        )

        player = DummyTarget()
        target = DummyTarget()

        outcome = item.use(player, target)

        self.assertEqual(target.hp, 5)
        self.assertEqual(outcome["damage"], 5)

class TestInvalidItemUse(unittest.TestCase):
    def test_non_consumable_use_fails(self):
        item = Items(
            name="Sword",
            category=Item_Type.WEAPON,
            stackable=False,
            unique=True
        )

        player = DummyTarget()
        target = DummyTarget()

        outcome = item.use(player, target)

        self.assertEqual(outcome["action"], "use_item_fail")

class TestSpawnItem(unittest.TestCase):
    def test_spawn_basic_sword(self):
        item = spawn_item("basic_sword")

        self.assertEqual(item.id, "basic_sword")
        self.assertEqual(item.name, "Basic Sword")
        self.assertEqual(item.category, Item_Type.WEAPON)
        self.assertIn("damage", item.stats)

class DummyEnemy:
    def __init__(self):
        self.gold_reward = 10
        self.loot_table = [
            {"item": "basic_sword", "chance": 1.0}
        ]


class TestRollLoot(unittest.TestCase):
    @patch("random.random", return_value=0.0)
    def test_roll_loot_drops_item(self, _):
        enemy = DummyEnemy()

        loot = roll_loot(enemy)

        self.assertEqual(loot["gold"], 10)
        self.assertEqual(len(loot["items"]), 1)
        self.assertEqual(loot["items"][0].id, "basic_sword")

class TestSkillRegistryIntegrity(unittest.TestCase):
    def test_skill_registry_contains_only_skills(self):
        for skill_id, skill in SKILL_REGISTRY.items():
            self.assertIsInstance(skill_id, str)
            self.assertIsInstance(skill, Skill)

    def test_skill_id_matches_registry_key(self):
        for skill_id, skill in SKILL_REGISTRY.items():
            self.assertEqual(skill.id, skill_id)

    def test_skill_targets_are_valid(self):
        valid_targets = {"self", "enemy", "all_enemies", "random_enemy"}
        for skill in SKILL_REGISTRY.values():
            self.assertIn(skill.target, valid_targets)

class TestSkillRegistryFields(unittest.TestCase):
    def test_skill_damage_shapes(self):
        for skill in SKILL_REGISTRY.values():
            if skill.damage is None:
                continue

            self.assertIn("type", skill.damage)

            dmg_type = skill.damage["type"]
            self.assertIn(dmg_type, {"flat", "multiplier", "hybrid"})

    def test_hit_chance_bounds(self):
        for skill in SKILL_REGISTRY.values():
            self.assertGreaterEqual(skill.hit_chance, 0.0)
            self.assertLessEqual(skill.hit_chance, 1.0)

class TestClassProgressionStructure(unittest.TestCase):
    def test_each_class_has_required_keys(self):
        required = {"level_cap", "xp_per_level", "level_rewards"}

        for class_id, data in CLASS_PROGRESSION.items():
            self.assertTrue(required.issubset(data.keys()), class_id)

    def test_xp_table_length_matches_level_cap(self):
        for class_id, data in CLASS_PROGRESSION.items():
            level_cap = data["level_cap"]
            xp_table = data["xp_per_level"]

            self.assertGreaterEqual(len(xp_table), level_cap + 1)

class TestLevelRewards(unittest.TestCase):
    def test_reward_levels_within_bounds(self):
        for class_id, data in CLASS_PROGRESSION.items():
            level_cap = data["level_cap"]
            rewards = data.get("level_rewards", {})

            for level in rewards:
                self.assertGreaterEqual(level, 2)
                self.assertLessEqual(level, level_cap)

    def test_reward_skill_ids_exist(self):
        for data in CLASS_PROGRESSION.values():
            rewards = data.get("level_rewards", {})

            for reward in rewards.values():
                for skill_id in reward.get("skills", []):
                    self.assertIn(skill_id, SKILL_REGISTRY)

class TestXPProgression(unittest.TestCase):
    def test_xp_is_non_decreasing(self):
        for data in CLASS_PROGRESSION.values():
            xp = data["xp_per_level"]

            for i in range(1, len(xp)):
                self.assertGreaterEqual(xp[i], xp[i - 1])

class TestEnemyInitialization(unittest.TestCase):
    def test_enemy_is_character(self):
        enemy = spawn_enemy(Enemy_type.ENEMY_GOBLIN)

        self.assertIsInstance(enemy, Character)
        self.assertEqual(enemy.type, Enemy_type.ENEMY_GOBLIN)
        self.assertEqual(enemy.sub_type, Enemy_sub_type.HUMANOID)
        self.assertEqual(enemy.behavior_tag, Enemy_behavior_tag.NORMAL)
        self.assertIsInstance(enemy.usable_skills, list)

class TestEnemySkillCooldowns(unittest.TestCase):
    def test_tick_skill_cooldowns_removes_expired(self):
        enemy = spawn_enemy(Enemy_type.ENEMY_GOBLIN)
        enemy.skill_cooldowns = {
            "skill_a": 1,
            "skill_b": 2,
        }

        enemy.tick_skill_cooldowns()

        self.assertNotIn("skill_a", enemy.skill_cooldowns)
        self.assertIn("skill_b", enemy.skill_cooldowns)
        self.assertEqual(enemy.skill_cooldowns["skill_b"], 1)

class TestEnemyScaling(unittest.TestCase):
    def test_enemy_scales_only_once(self):
        enemy = spawn_enemy(Enemy_type.ENEMY_GOBLIN)

        original_hp = enemy.hp
        enemy.scale_stats(day_counter=10, depth=5)

        scaled_hp = enemy.hp
        self.assertGreaterEqual(scaled_hp, original_hp)

        enemy.scale_stats(day_counter=100, depth=50)
        self.assertEqual(enemy.hp, scaled_hp)

    def test_enemy_scaling_never_invalid(self):
        enemy = spawn_enemy(Enemy_type.ENEMY_GOBLIN)

        enemy.scale_stats(day_counter=0, depth=-5)

        self.assertGreaterEqual(enemy.hp, 1)
        self.assertGreaterEqual(enemy.damage, 1)
        self.assertGreaterEqual(enemy.defence, 0)

class TestSpawnEnemyFactory(unittest.TestCase):
    def test_spawn_enemy_copies_skill_list(self):
        enemy_a = spawn_enemy(Enemy_type.ENEMY_GOBLIN)
        enemy_b = spawn_enemy(Enemy_type.ENEMY_GOBLIN)

        enemy_a.usable_skills.append("fake_skill")

        self.assertNotIn("fake_skill", enemy_b.usable_skills)

    def test_spawn_enemy_sets_rewards(self):
        enemy = spawn_enemy(Enemy_type.ENEMY_GOBLIN)

        self.assertGreaterEqual(enemy.xp_reward, 0)
        self.assertGreaterEqual(enemy.gold_reward, 0)

class TestEnemySpawner(unittest.TestCase):
    @patch("random.uniform", return_value=0.0)
    def test_weighted_spawn_returns_valid_enemy(self, _):
        enemy_type = Enemy_Spawner.get_random_template_weighted()

        self.assertIn(enemy_type, Enemy_type)

    def test_forbid_rarities_excludes(self):
        forbidden = {Enemy_Rarity.COMMON}

        table = Enemy_Spawner.build_weight_table(forbidden)

        for enemy_type, _ in table:
            rarity = ENEMY_DEFINITIONS[enemy_type]["rarity"]
            self.assertNotIn(rarity, forbidden)

    @patch("random.choice")
    def test_miniboss_selection(self, mock_choice):
        mock_choice.return_value = Enemy_type.ENEMY_BOSS_DRAGON

        enemy_type = Enemy_Spawner.get_random_miniboss_template()
        self.assertEqual(enemy_type, Enemy_type.ENEMY_BOSS_DRAGON)

class TestCoreImports(unittest.TestCase):
    def test_core_imports(self):
        import game.core.character
        import game.core.Enemy_class
        import game.core.Heroes
        import game.core.Item_class
        import game.core.Skill_class
        import game.core.Status