from enum import Enum
from .town_names import Town_names

class Location_Type(Enum):
    EXTERIOR = "exterior"
    INTERIOR = "interior"
    SPECIAL  = "special"

class Town_Actions(Enum):
    ENTER_INN        = "enter inn"
    ENTER_TAVERN     = "enter tavern"
    ENTER_SHOP       = "enter shop"
    LEAVE_BUILDING   = "leave building"
    REST             = "rest"
    TALK             = "talk"
    ENTER_CAVE       = "enter cave"
    ENTER_CASTLE     = "enter castle"
    LEAVE_TOWN       = "leave town"
    BUY_BEER         = "buy beer"
    BUY_FROM_SHOP    = "buy from shop"
    SELL_FROM_SHOP   = "sell from shop"


class Location():
    def __init__(self, name: str, location_type: Location_Type, actions: list[Town_Actions], adjacent_locations: list[str], extra_metadata: dict | None = None):
        self.name = name
        self.location_type = location_type
        self.actions = actions
        self.adjacent_locations = adjacent_locations
        self.extra_metadata = extra_metadata or {}

    def is_interior(self) -> bool:
        return self.location_type == Location_Type.INTERIOR

    def is_exterior(self) -> bool:
        return self.location_type == Location_Type.EXTERIOR

    def is_special(self) -> bool:
        return self.location_type == Location_Type.SPECIAL


class TownGraph():
    def __init__(self, castle_unlocked: bool):
        self.locations: dict[str, Location] = {}
        self.player_location: str | None = None

        self.castle_unlocked = castle_unlocked


    def current_location(self) -> Location:
        return self.locations[self.player_location]


    def move_location(self, destination: str) -> dict:
        if destination not in self.get_available_moves():
            return {
                "success": False,
                "reason": f"You cannot move from {self.current_location().name} to {destination}."
            }
        
        elif destination not in self.locations:
            return {
                "success": False,
                "reason": f"No such destination: {destination}"
            }
        
        self.player_location = destination
        return {
                "success": True,
                "new_location": destination
            }

    def set_starting_location(self, name: str) -> None:
        if name not in self.locations:
            raise ValueError(f"Starting location '{name}' does not exist in the TownGraph.")
        self.player_location = name


    def is_valid_action(self, action: Town_Actions) -> dict[str, any]:
        cur_location = self.current_location().name
        if action in self.get_available_actions():
            return {
                "success": True,
                "action": action,
                "location": cur_location
            }
        else:
            return {
                "success": False,
                "action": action,
                "reason": f"Could not perform {action} in {cur_location}"
            }
            

    def get_available_actions(self) -> list[Town_Actions]:
        return self.current_location().actions


    def get_available_moves(self) -> list[str]:
        return self.current_location().adjacent_locations


    def is_interior(self) -> bool:
        return self.current_location().is_interior()
    

    def leave_building(self, exit_to: str = Town_names.TOWN_GATE.value) -> dict:
        if not self.is_interior():
            return {
                "success": False,
                "reason": "You are not inside a building."
            }
        
        self.player_location = exit_to
        return {
            "success": True,
            "new_location": exit_to
        }


    def get_metadata(self) -> dict:
        return self.current_location().extra_metadata


    def update_metadata(self, key: str, value: any) -> None:
        self.current_location().extra_metadata[key] = value


    def perform_action(self, action: Town_Actions) -> dict:
        valid = self.is_valid_action(action)
        if not valid["success"]:
            return valid
        
        location = self.current_location()
        location_name = location.name
        metadata = location.extra_metadata

        match action:
            case Town_Actions.ENTER_SHOP:
                return {
                    "success": True,
                    "type": "enter_shop",
                    "destination": Town_names.SHOP_INTERIOR.value
                }

            case Town_Actions.ENTER_INN:
                return {
                    "success": True,
                    "type": "enter_inn",
                    "destination": Town_names.INN_INTERIOR.value
                }

            case Town_Actions.ENTER_TAVERN:
                return {
                    "success": True,
                    "type": "enter_tavern",
                    "destination": Town_names.TAVERN_INTERIOR.value
                }
                        
            # ============================
            # LEAVE BUILDING → back to Town Gate
            # ============================
            case Town_Actions.LEAVE_BUILDING:
                if not self.is_interior():
                    return {
                        "success": False,
                        "reason": "You are not inside a building."
                    }

                destination = Town_names.TOWN_GATE.value

                return {
                    "success": True,
                    "type": "leave_building",
                    "destination": destination,
                    "location": location_name,
                }
            
            # ============================
            # REST (Inn Interior only)
            # ============================
            case Town_Actions.REST:
                if location_name != Town_names.INN_INTERIOR.value:
                    return {
                        "success": False,
                        "reason": "You can only rest at the inn."
                    }
                
                night_cost = metadata.get("night_cost", 50)
                heal_amount = metadata.get("heal_amount", "full")

                return {
                    "success": True,
                    "type": "rest",
                    "cost": night_cost,
                    "heal_amount": heal_amount,
                    "location": location_name,
                }
            
            # ============================
            # TALK (all locations)
            # ============================
            case Town_Actions.TALK:
                return {
                    "success": True,
                    "type": "talk",
                    "location": location_name
                }
            
            # ============================
            # BUY BEER (Tavern only)
            # ============================
            case Town_Actions.BUY_BEER:
                if location_name != Town_names.TAVERN_INTERIOR.value:
                    return {
                        "success": False,
                        "reason": "You can only buy beer in the tavern."
                    }
                
                beer_price = metadata.get("beer_price", 15)
                return {
                    "success": True,
                    "type": "buy_beer",
                    "cost": beer_price,
                    "location": location_name
                }
            
            # ============================
            # BUY FROM SHOP (Shop Interior only)
            # ============================
            case Town_Actions.BUY_FROM_SHOP:
                if location_name != Town_names.SHOP_INTERIOR.value:
                    return {
                        "success": False,
                        "reason": "You can only buy items in the shop."
                    }
                
                shop_inventory = metadata.get("inventory", [])
                buy_multiplier = metadata.get("buy_multiplier", 1.0)

                return {
                    "success": True,
                    "type": "buy_menu",
                    "inventory": shop_inventory,
                    "buy_multiplier": buy_multiplier,
                    "location": location_name
                }
            
            # ============================
            # SELL TO SHOP (Shop Interior only)
            # ============================
            case Town_Actions.SELL_FROM_SHOP:
                if location_name != Town_names.SHOP_INTERIOR.value:
                    return {
                        "success": False,
                        "reason": "You can only sell items in the shop."
                    }
                
                sell_multiplier = metadata.get("sell_multiplier", 0.5)

                return {
                    "success": True,
                    "type": "sell_menu",
                    "sell_multiplier": sell_multiplier,
                    "location": location_name
                }
            
            # ============================
            # ENTER CASTLE (Town Gate only)
            # ============================
            case Town_Actions.ENTER_CASTLE:
                if location_name != Town_names.TOWN_GATE.value:
                    return {
                        "success": False,
                        "reason": "You can only enter the castle from the Town Gate."
                    }
                
                if not self.castle_unlocked:
                    return{
                        "success": False,
                        "reason": "The castle gates are locked."
                    }
            
                return {
                    "success": True,
                    "type": "enter_castle",
                    "location": location_name
                }
        
            # ============================
            # ENTER CAVE (Town Gate only)
            # ============================
            case Town_Actions.ENTER_CAVE:
                if location_name != Town_names.TOWN_GATE.value:
                    return {
                        "success": False,
                        "reason": "You can only enter the cave from the Town Gate."
                    }
                
                return {
                    "success": True,
                    "type": "enter_cave",
                    "location": location_name
                }
            
            # ============================
            # LEAVE TOWN (leads to submenu)
            # ============================
            case Town_Actions.LEAVE_TOWN:
                if location_name != Town_names.TOWN_GATE.value:
                    return {
                        "success": False,
                        "reason": "You can only leave town from the Town Gate."
                    }
                
                return {
                    "success": True,
                    "type": "leave_town",
                    "location": location_name
                }
            
            # ============================
            # Unknown action fallback
            # ============================
            case _:
                return {
                    "success": False,
                    "reason": f"Action '{action}' is not implemented in TownGraph."
                }
