import unittest

from game.world.town_logic.town_shop_system import (
    initialize_shop_inventory,
    record_purchase,
    restock_shop_for_new_day,
    update_prices_based_on_demand,
    MARK_UP_FACTOR,
    SALE_FACTOR,
    ShopItemRecord,
)

from game.core.character import Character


class DummyPlayer(Character):
    def __init__(self):
        super().__init__("Hero", hp=10, damage=1, defence=1)


def make_shop_metadata():
    return {
        "inventory": [
            {"item_id": "basic_sword", "max_stock": 1},
            {"item_id": "small_healing_potion", "max_stock": 5},
        ]
    }


class TestShopInitialization(unittest.TestCase):

    def test_initialize_shop_inventory_builds_records(self):
        metadata = make_shop_metadata()

        initialize_shop_inventory(metadata)

        inventory = metadata["inventory"]
        self.assertEqual(len(inventory), 2)

        for record in inventory:
            self.assertIsInstance(record, ShopItemRecord)
            self.assertEqual(record.stock, record.max_stock)
            self.assertEqual(record.current_price, record.base_price)
            self.assertEqual(record.sold_today, 0)


class TestRecordPurchase(unittest.TestCase):

    def setUp(self):
        self.metadata = make_shop_metadata()
        initialize_shop_inventory(self.metadata)

    def test_record_purchase_reduces_stock(self):
        record = self.metadata["inventory"][1]
        record_purchase(self.metadata, record.item_id, quantity=2)

        self.assertEqual(record.stock, record.max_stock - 2)
        self.assertEqual(record.sold_today, 2)

    def test_purchase_cannot_exceed_stock(self):
        record = self.metadata["inventory"][1]
        record_purchase(self.metadata, record.item_id, quantity=999)

        self.assertEqual(record.stock, 0)
        self.assertEqual(record.sold_today, record.max_stock)


class TestRestockLogic(unittest.TestCase):

    def setUp(self):
        self.metadata = make_shop_metadata()
        initialize_shop_inventory(self.metadata)
        self.player = DummyPlayer()

    def test_unique_item_removed_if_player_owns_it(self):
        unique = self.metadata["inventory"][0]
        self.player.add_item(unique.item)

        restock_shop_for_new_day(self.metadata, self.player)

        self.assertEqual(unique.stock, 0)

    def test_unique_item_restocked_if_not_owned(self):
        unique = self.metadata["inventory"][0]

        restock_shop_for_new_day(self.metadata, self.player)

        self.assertEqual(unique.stock, unique.max_stock)

    def test_stackable_items_fully_restock(self):
        stackable = self.metadata["inventory"][1]
        stackable.stock = 0

        restock_shop_for_new_day(self.metadata, self.player)

        self.assertEqual(stackable.stock, stackable.max_stock)


class TestPriceAdjustment(unittest.TestCase):

    def setUp(self):
        self.metadata = make_shop_metadata()
        initialize_shop_inventory(self.metadata)

    def test_full_sellout_increases_price(self):
        record = self.metadata["inventory"][1]
        record.sold_today = record.max_stock

        update_prices_based_on_demand(self.metadata)

        self.assertEqual(
            record.current_price,
            int(round(record.base_price * MARK_UP_FACTOR))
        )

    def test_low_sales_trigger_sale(self):
        record = self.metadata["inventory"][1]
        record.sold_today = 0

        update_prices_based_on_demand(self.metadata)

        self.assertEqual(
            record.current_price,
            int(round(record.base_price * SALE_FACTOR))
        )

    def test_partial_sales_reset_price(self):
        record = self.metadata["inventory"][1]
        record.sold_today = 2
        record.current_price = int(record.base_price * 1.2)

        update_prices_based_on_demand(self.metadata)

        self.assertEqual(record.current_price, record.base_price)

    def test_non_stackable_items_never_change_price(self):
        record = self.metadata["inventory"][0]
        record.sold_today = 1
        record.current_price = 999

        update_prices_based_on_demand(self.metadata)

        self.assertEqual(record.current_price, record.base_price)
        