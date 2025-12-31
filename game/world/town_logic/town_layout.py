from .town_creation import Town_Actions, TownGraph, Location, Location_Type
from .town_names import Town_names

def build_town_graph(castle_unlocked: bool) -> TownGraph:
    town = TownGraph(castle_unlocked)

    town_gate = _build_town_gate()
    
    all_locations = [
        town_gate,
        *_build_interior_locations(),
    ]

    for location in all_locations:
        town.locations[location.name] = location
    
    town.set_starting_location(town_gate.name)

    return town

def _build_town_gate() -> Location:

    adjacent_locations = [
        Town_names.SHOP_INTERIOR.value,
        Town_names.INN_INTERIOR.value,
        Town_names.TAVERN_INTERIOR.value,
    ]

    actions = [
        Town_Actions.ENTER_SHOP,
        Town_Actions.ENTER_INN,
        Town_Actions.ENTER_TAVERN,
        Town_Actions.TALK,
        Town_Actions.LEAVE_TOWN,
    ]

    town_gate = Location(
        name=Town_names.TOWN_GATE.value,
        location_type=Location_Type.EXTERIOR,
        actions=actions,
        adjacent_locations=adjacent_locations,
        extra_metadata={},
    )

    return town_gate

def _build_interior_locations() -> list[Location]:

    shop_metadata = {
        "inventory": [
            {"item_id": "basic_sword", "max_stock": 1},
            {"item_id": "small_healing_potion", "max_stock": 6}
        ],
        "buy_multiplier": 1.0,
        "sell_multiplier": 0.5,
    }
    shop_int = Location(
        name=Town_names.SHOP_INTERIOR.value,
        location_type=Location_Type.INTERIOR,
        actions=[
            Town_Actions.TALK,
            Town_Actions.BUY_FROM_SHOP,
            Town_Actions.SELL_FROM_SHOP,
            Town_Actions.LEAVE_BUILDING,
        ],
        adjacent_locations=[Town_names.TOWN_GATE.value],
        extra_metadata=shop_metadata,
    )

    inn_metadata = {
        "night_cost": 50,
        "heal_amount": "full",
    }
    inn_int = Location(
        name=Town_names.INN_INTERIOR.value,
        location_type=Location_Type.INTERIOR,
        actions=[
            Town_Actions.TALK,
            Town_Actions.REST,
            Town_Actions.LEAVE_BUILDING,
        ],
        adjacent_locations=[Town_names.TOWN_GATE.value],
        extra_metadata=inn_metadata,
    )

    tavern_metadata = {
        "beer_price": 15,
        "rumors": [],
    }
    tavern_int = Location(
        name=Town_names.TAVERN_INTERIOR.value,
        location_type=Location_Type.INTERIOR,
        actions=[
            Town_Actions.TALK,
            Town_Actions.BUY_BEER,
            Town_Actions.LEAVE_BUILDING,
        ],
        adjacent_locations=[Town_names.TOWN_GATE.value],
        extra_metadata=tavern_metadata,
    )

    return [shop_int, inn_int, tavern_int]

