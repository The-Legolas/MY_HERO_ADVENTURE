
# done about an hours worth of work so far: time 20:36
# Have done about 10 min worth

from enum import Enum
from game.core.Character_class import Character

class Location_Type(Enum):
    EXTERIOR = "exterior"
    INTERIOR = "interior"
    SPECIAL  = "special"

class Town_Actions(Enum):
   ENTER_BUILDING   = "enter building"
   LEAVE_BUILDING   = "leave building"
   REST             = "rest"
   TALK             = "talk"


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
    def __init__(self):
        self.locations: dict[str, Location] = {}

        self.player_location: str | None = None


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
                "reason": f"Destination '{destination}' does not exist."
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
        cur_location = self.current_location()
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
                "reason": f"Could not perform {action} in {cur_location.name}"
            }
            

    def get_available_actions(self) -> list[Town_Actions]:
        return self.current_location().actions


    def get_available_moves(self) -> list[str]:
        return self.current_location().adjacent_locations


    def is_interior(self) -> bool:
        return self.current_location().is_interior()
    

    def leave_building(self, exit_to: str = "Town Gate") -> dict:
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


