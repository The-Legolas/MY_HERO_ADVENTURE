import unittest
from unittest.mock import patch

from game.world.Gen_Game_World import Game_World
from game.core.character import Character
from game.world.dungeon_manager import Dungeon_Manager


class TestGameWorldInitialization(unittest.TestCase):

    def test_world_initializes_with_town_and_dungeons(self):
        player = Character("Hero", 10, 1, 1)

        world = Game_World(player=player, day_counter=1, seed=123)

        self.assertIn("Town", world.areas)
        self.assertIn("Cave", world.areas)
        self.assertIn("Castle", world.areas)

        self.assertIsInstance(world.get_cave(), Dungeon_Manager)
        self.assertIsInstance(world.get_castle(), Dungeon_Manager)


class TestDayAdvance(unittest.TestCase):

    @patch("game.world.Gen_Game_World.restock_shop_for_new_day")
    def test_on_day_advance_increments_day_and_refreshes(self, mock_restock):
        player = Character("Hero", 10, 1, 1)
        world = Game_World(player=player, day_counter=1, seed=42)

        old_cave = world.get_cave()
        old_castle = world.get_castle()

        result = world.on_day_advance()

        self.assertEqual(world.day_counter, 2)
        self.assertNotEqual(world.get_cave(), old_cave)
        self.assertNotEqual(world.get_castle(), old_castle)

        self.assertIn("shops_restocked", result["events"])
        self.assertIn("dungeons_refreshed", result["events"])


class TestCastleUnlock(unittest.TestCase):

    def test_unlock_castle_sets_flag_and_rebuilds_town(self):
        player = Character("Hero", 10, 1, 1)
        world = Game_World(player=player, day_counter=1, seed=0)

        self.assertFalse(world.castle_unlocked)

        world.unlock_castle()

        self.assertTrue(world.castle_unlocked)
        self.assertIn("Town", world.areas)

    def test_unlock_castle_idempotent(self):
        player = Character("Hero", 10, 1, 1)
        world = Game_World(player=player, day_counter=1, seed=0)

        world.unlock_castle()
        town_before = world.get_town()

        world.unlock_castle()
        town_after = world.get_town()

        self.assertIs(town_before, town_after)


class TestShopRestocking(unittest.TestCase):

    @patch("game.world.Gen_Game_World.restock_shop_for_new_day")
    def test_restock_all_shops_called_for_shop_locations(self, mock_restock):
        player = Character("Hero", 10, 1, 1)
        world = Game_World(player=player, day_counter=1, seed=0)

        town = world.get_town()
        world.restock_all_shops(town)

        self.assertTrue(mock_restock.called)
