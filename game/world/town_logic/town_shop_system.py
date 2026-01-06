from dataclasses import dataclass

from game.core.Item_class import Items
from game.core.character import Character

from game.engine.item_spawner import spawn_item

MARK_UP_FACTOR = 1.4
SALE_FACTOR = 0.7

@dataclass
class ShopItemRecord():
    item_id: str
    item: Items
    base_price: int
    current_price: int
    max_stock: int
    stock: int
    is_unique: bool
    is_stackable: bool
    sold_today: int = 0


def initialize_shop_inventory(shop_metadata: dict[str, any]) -> None:

    raw_inventory = shop_metadata.get("inventory", [])
    built_inventory: list[ShopItemRecord] = []

    for entry in raw_inventory:
        item_id = entry["item_id"]
        max_stock = entry.get("max_stock", 1)
        
        item_obj = spawn_item(item_id)
        base_price = getattr(item_obj, "value", 0)
        is_unique = getattr(item_obj, "unique", False)
        is_stackable = getattr(item_obj, "stackable", False)

        record = ShopItemRecord(
            item_id         = item_id,
            item            = item_obj,
            base_price      = base_price,
            current_price   = base_price,
            max_stock       = max_stock,
            stock           = max_stock,
            is_unique       = is_unique,
            is_stackable    = is_stackable,
            sold_today      = 0,
        )
        built_inventory.append(record)

    shop_metadata["inventory"] = built_inventory


def record_purchase(shop_metadata: dict[str, any], item_id: str, quantity: int = 1) -> None:
    inventory: list[ShopItemRecord] = shop_metadata.get("inventory", [])
    
    for record in inventory:
        if record.item_id == item_id:
            actual_q = min(quantity, record.stock)
            record.stock -= actual_q
            record.sold_today += actual_q
            break


def player_owns_item(player: Character, item_id: str) -> bool:
    items = player.inventory["items"]
    return item_id in items


def restock_shop_for_new_day(shop_metadata: dict[str, any], player: Character) -> None:
    inventory: list[ShopItemRecord] = shop_metadata.get("inventory", [])

    for record in inventory:
        if record.is_unique:
            if player_owns_item(player, record.item_id):
                record.stock = 0
                record.sold_today = 0
                continue
            
            else:
                record.stock = record.max_stock
        
        elif record.is_stackable:
            record.stock = record.max_stock
        
        else:
            if record.stock == 0:
                record.stock = record.max_stock
        
    update_prices_based_on_demand(shop_metadata)

    for record in inventory:
        record.sold_today = 0


def update_prices_based_on_demand(shop_metadata: dict[str, any]):
    inventory: list[ShopItemRecord] = shop_metadata.get("inventory", [])

    for record in inventory:
        _adjust_price_for_record(record)


def _adjust_price_for_record(record: ShopItemRecord) -> None:

    if not record.is_stackable:
        record.current_price = record.base_price
        return

    percentage_sold = record.sold_today / record.max_stock
    percentage_not_sold = 1 - percentage_sold

    if percentage_sold == 1.0:
        record.current_price = int(round(record.base_price * MARK_UP_FACTOR))
    
    elif percentage_not_sold >= 0.9:
        record.current_price = int(round(record.base_price * SALE_FACTOR))

    elif record.current_price != record.base_price:
        record.current_price = record.base_price

