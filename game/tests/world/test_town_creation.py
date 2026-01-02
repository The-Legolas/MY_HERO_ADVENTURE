import unittest

from game.world.town_logic.town_creation import (
    Location,
    TownGraph,
    Location_Type,
    Town_Actions,
)
from game.world.town_logic.town_names import Town_names


def make_basic_town(castle_unlocked=False) -> TownGraph:
    town = TownGraph(castle_unlocked=castle_unlocked)

    town.locations = {
        Town_names.TOWN_GATE.value: Location(
            name=Town_names.TOWN_GATE.value,
            location_type=Location_Type.EXTERIOR,
            actions=[
                Town_Actions.ENTER_SHOP,
                Town_Actions.ENTER_INN,
                Town_Actions.ENTER_TAVERN,
                Town_Actions.ENTER_CAVE,
                Town_Actions.ENTER_CASTLE,
                Town_Actions.LEAVE_TOWN,
            ],
            adjacent_locations=[
                Town_names.SHOP_INTERIOR.value,
                Town_names.INN_INTERIOR.value,
                Town_names.TAVERN_INTERIOR.value,
            ],
        ),
        Town_names.SHOP_INTERIOR.value: Location(
            name=Town_names.SHOP_INTERIOR.value,
            location_type=Location_Type.INTERIOR,
            actions=[
                Town_Actions.BUY_FROM_SHOP,
                Town_Actions.SELL_FROM_SHOP,
                Town_Actions.LEAVE_BUILDING,
            ],
            adjacent_locations=[Town_names.TOWN_GATE.value],
            extra_metadata={
                "inventory": [],
                "buy_multiplier": 1.0,
                "sell_multiplier": 0.5,
            },
        ),
        Town_names.INN_INTERIOR.value: Location(
            name=Town_names.INN_INTERIOR.value,
            location_type=Location_Type.INTERIOR,
            actions=[
                Town_Actions.REST,
                Town_Actions.TALK,
                Town_Actions.LEAVE_BUILDING,
            ],
            adjacent_locations=[Town_names.TOWN_GATE.value],
            extra_metadata={
                "night_cost": 50,
                "heal_amount": "full",
            },
        ),
    }

    town.set_starting_location(Town_names.TOWN_GATE.value)
    return town

class TestLocation(unittest.TestCase):

    def test_location_type_helpers(self):
        loc = Location(
            "Test",
            Location_Type.INTERIOR,
            actions=[],
            adjacent_locations=[],
        )

        self.assertTrue(loc.is_interior())
        self.assertFalse(loc.is_exterior())
        self.assertFalse(loc.is_special())

class TestTownGraphMovement(unittest.TestCase):

    def test_move_location_success(self):
        town = make_basic_town()
        result = town.move_location(Town_names.SHOP_INTERIOR.value)

        self.assertTrue(result["success"])
        self.assertEqual(town.player_location, Town_names.SHOP_INTERIOR.value)

    def test_move_location_invalid(self):
        town = make_basic_town()
        result = town.move_location("nonexistent")

        self.assertFalse(result["success"])

class TestTownActions(unittest.TestCase):

    def test_available_actions(self):
        town = make_basic_town()
        actions = town.get_available_actions()

        self.assertIn(Town_Actions.ENTER_SHOP, actions)
        self.assertIn(Town_Actions.LEAVE_TOWN, actions)

    def test_is_valid_action_success(self):
        town = make_basic_town()
        result = town.is_valid_action(Town_Actions.ENTER_SHOP)

        self.assertTrue(result["success"])

    def test_is_valid_action_failure(self):
        town = make_basic_town()
        result = town.is_valid_action(Town_Actions.REST)

        self.assertFalse(result["success"])

class TestBuildingTransitions(unittest.TestCase):

    def test_enter_shop(self):
        town = make_basic_town()
        result = town.perform_action(Town_Actions.ENTER_SHOP)

        self.assertTrue(result["success"])
        self.assertEqual(result["destination"], Town_names.SHOP_INTERIOR.value)

    def test_leave_building_success(self):
        town = make_basic_town()
        town.move_location(Town_names.SHOP_INTERIOR.value)

        result = town.perform_action(Town_Actions.LEAVE_BUILDING)

        self.assertTrue(result["success"])
        self.assertEqual(result["destination"], Town_names.TOWN_GATE.value)

    def test_leave_building_fail_if_not_interior(self):
        town = make_basic_town()
        result = town.perform_action(Town_Actions.LEAVE_BUILDING)

        self.assertFalse(result["success"])

class TestInnActions(unittest.TestCase):

    def test_rest_only_allowed_in_inn(self):
        town = make_basic_town()
        result = town.perform_action(Town_Actions.REST)

        self.assertFalse(result["success"])

    def test_rest_in_inn(self):
        town = make_basic_town()
        town.move_location(Town_names.INN_INTERIOR.value)

        result = town.perform_action(Town_Actions.REST)

        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "rest")
        self.assertIn("cost", result)

class TestShopActions(unittest.TestCase):

    def test_buy_only_in_shop(self):
        town = make_basic_town()
        result = town.perform_action(Town_Actions.BUY_FROM_SHOP)

        self.assertFalse(result["success"])

    def test_buy_in_shop(self):
        town = make_basic_town()
        town.move_location(Town_names.SHOP_INTERIOR.value)

        result = town.perform_action(Town_Actions.BUY_FROM_SHOP)

        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "buy_menu")

    def test_sell_in_shop(self):
        town = make_basic_town()
        town.move_location(Town_names.SHOP_INTERIOR.value)

        result = town.perform_action(Town_Actions.SELL_FROM_SHOP)

        self.assertTrue(result["success"])
        self.assertEqual(result["type"], "sell_menu")

class TestDungeonAccess(unittest.TestCase):

    def test_enter_cave_from_gate(self):
        town = make_basic_town()
        result = town.perform_action(Town_Actions.ENTER_CAVE)

        self.assertTrue(result["success"])

    def test_enter_castle_locked(self):
        town = make_basic_town(castle_unlocked=False)
        result = town.perform_action(Town_Actions.ENTER_CASTLE)

        self.assertFalse(result["success"])

    def test_enter_castle_unlocked(self):
        town = make_basic_town(castle_unlocked=True)
        result = town.perform_action(Town_Actions.ENTER_CASTLE)

        self.assertTrue(result["success"])

