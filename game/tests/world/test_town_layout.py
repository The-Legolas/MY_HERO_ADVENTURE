import unittest

from game.world.town_logic.town_layout import build_town_graph
from game.world.town_logic.town_creation import Location_Type, Town_Actions
from game.systems.enums.town_names import Town_names


class TestTownLayoutStructure(unittest.TestCase):

    def setUp(self):
        self.town = build_town_graph(castle_unlocked=False)

    def test_build_returns_towngraph(self):
        self.assertIsNotNone(self.town)
        self.assertIsNotNone(self.town.locations)

    def test_starting_location_is_town_gate(self):
        self.assertEqual(self.town.player_location, Town_names.TOWN_GATE.value)

    def test_all_expected_locations_exist(self):
        expected = {
            Town_names.TOWN_GATE.value,
            Town_names.SHOP_INTERIOR.value,
            Town_names.INN_INTERIOR.value,
            Town_names.TAVERN_INTERIOR.value,
        }
        self.assertEqual(set(self.town.locations.keys()), expected)


class TestTownGateDefinition(unittest.TestCase):

    def setUp(self):
        self.town = build_town_graph(castle_unlocked=False)
        self.gate = self.town.locations[Town_names.TOWN_GATE.value]

    def test_town_gate_type(self):
        self.assertEqual(self.gate.location_type, Location_Type.EXTERIOR)

    def test_town_gate_actions(self):
        actions = self.gate.actions

        self.assertIn(Town_Actions.ENTER_SHOP, actions)
        self.assertIn(Town_Actions.ENTER_INN, actions)
        self.assertIn(Town_Actions.ENTER_TAVERN, actions)
        self.assertIn(Town_Actions.TALK, actions)
        self.assertIn(Town_Actions.LEAVE_TOWN, actions)

    def test_town_gate_adjacency(self):
        self.assertCountEqual(
            self.gate.adjacent_locations,
            [
                Town_names.SHOP_INTERIOR.value,
                Town_names.INN_INTERIOR.value,
                Town_names.TAVERN_INTERIOR.value,
            ],
        )


class TestShopInterior(unittest.TestCase):

    def setUp(self):
        self.town = build_town_graph(castle_unlocked=False)
        self.shop = self.town.locations[Town_names.SHOP_INTERIOR.value]

    def test_shop_type(self):
        self.assertEqual(self.shop.location_type, Location_Type.INTERIOR)

    def test_shop_actions(self):
        self.assertIn(Town_Actions.BUY_FROM_SHOP, self.shop.actions)
        self.assertIn(Town_Actions.SELL_FROM_SHOP, self.shop.actions)
        self.assertIn(Town_Actions.LEAVE_BUILDING, self.shop.actions)

    def test_shop_metadata_structure(self):
        meta = self.shop.extra_metadata

        self.assertIn("inventory", meta)
        self.assertIn("buy_multiplier", meta)
        self.assertIn("sell_multiplier", meta)

        self.assertIsInstance(meta["inventory"], list)
        for entry in meta["inventory"]:
            self.assertIn("item_id", entry)
            self.assertIn("max_stock", entry)

    def test_shop_adjacency(self):
        self.assertEqual(self.shop.adjacent_locations, [Town_names.TOWN_GATE.value])


class TestInnInterior(unittest.TestCase):

    def setUp(self):
        self.town = build_town_graph(castle_unlocked=False)
        self.inn = self.town.locations[Town_names.INN_INTERIOR.value]

    def test_inn_type(self):
        self.assertEqual(self.inn.location_type, Location_Type.INTERIOR)

    def test_inn_actions(self):
        self.assertIn(Town_Actions.REST, self.inn.actions)
        self.assertIn(Town_Actions.TALK, self.inn.actions)
        self.assertIn(Town_Actions.LEAVE_BUILDING, self.inn.actions)

    def test_inn_metadata(self):
        meta = self.inn.extra_metadata

        self.assertIn("night_cost", meta)
        self.assertIn("heal_amount", meta)

    def test_inn_adjacency(self):
        self.assertEqual(self.inn.adjacent_locations, [Town_names.TOWN_GATE.value])


class TestTavernInterior(unittest.TestCase):

    def setUp(self):
        self.town = build_town_graph(castle_unlocked=False)
        self.tavern = self.town.locations[Town_names.TAVERN_INTERIOR.value]

    def test_tavern_type(self):
        self.assertEqual(self.tavern.location_type, Location_Type.INTERIOR)

    def test_tavern_actions(self):
        self.assertIn(Town_Actions.BUY_BEER, self.tavern.actions)
        self.assertIn(Town_Actions.TALK, self.tavern.actions)
        self.assertIn(Town_Actions.LEAVE_BUILDING, self.tavern.actions)

    def test_tavern_metadata(self):
        meta = self.tavern.extra_metadata

        self.assertIn("beer_price", meta)
        self.assertIn("rumors", meta)
        self.assertIsInstance(meta["rumors"], list)

    def test_tavern_adjacency(self):
        self.assertEqual(self.tavern.adjacent_locations, [Town_names.TOWN_GATE.value])
        