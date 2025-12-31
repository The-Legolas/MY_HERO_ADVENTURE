
def parse_leave_town_input(raw: str) -> str | None:
    t = raw.strip().lower()

    if t in ("1", "back", "return"):
        return "go_back"

    if t in ("2", "enter cave", "cave", "go cave", "go to cave"):
        return "enter_cave"

    if t in ("3", "enter castle", "castle", "go castle", "go to castle"):
        return "enter_castle"

    return None

def parse_town_gate_input(raw: str) -> str | None:
    t = raw.strip().lower()

    if t in ("1", "shop", "enter shop", "go shop", "go to shop"):
        return "enter_shop"

    if t in ("2", "inn", "enter inn", "go inn", "go to inn"):
        return "enter_inn"

    if t in ("3", "tavern", "enter tavern", "go tavern", "go to tavern"):
        return "enter_tavern"

    if t in ("4", "leave", "leave town", "exit", "go outside"):
        return "leave_town"

    return None

def parse_interior_input(raw: str) -> str | None:
    t = raw.strip().lower()

    if t in ("1", "talk", "speak"):
        return "talk"

    if t in ("2", "menu", "action", "rest", "shop", "buy", "buy beer", "beer"):
        return "menu"

    if t in ("3", "leave", "back", "exit", "leave building", "exit building",):
        return "leave_building"

    return None

def parse_shop_input(raw: str) -> str | None:
    t = raw.strip().lower()

    if t in ("1", "buy", "buy item", "buy_item"):
        return "buy_item"

    if t in ("2", "sell", "sell item", "sell_item"):
        return "sell_item"

    if t in ("3", "leave", "leave_shop", "leave the shop", "leave shop", "exit", "exit shop", "exit_shop"):
        return "leave_shop"

    return None

def inventory_input_parser(raw: str) -> str | None:
    t = raw.strip().lower()

    if t in ("i", "inventory", "bag", "equipment", "backpack"):
        return "open_inventory"
    
    return None

def parse_dungeon_input(raw: str, has_room_action: bool) -> str | None:
    t = raw.strip().lower()

    if t in ("1", "move", "go"):
        return "move"

    if has_room_action and t in ("2", "action", "open", "use"):
        return "room_action"

    if (
        (has_room_action and t in ("3", "inspect", "look")) or
        (not has_room_action and t in ("2", "inspect", "look"))
    ):
        return "inspect"

    if (
        (has_room_action and t in ("4", "leave", "exit")) or
        (not has_room_action and t in ("3", "leave", "exit"))
    ):
        return "leave_dungeon"

    return None
