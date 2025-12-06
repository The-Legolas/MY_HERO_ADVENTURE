"""import sys
import os
# Add the project's root folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
import random
from .Dungeon_room_code import Room_Types
from .dungeon_manager import Dungeon_Manager, compute_farthest
from .town_logic.town_layout import build_town_graph
from .town_logic.town_shop_system import restock_shop_for_new_day, initialize_shop_inventory
from .town_logic.town_names import Town_names
from .town_logic.town_creation import TownGraph
from game.core.Character_class import Character

class Game_World():
    def __init__(self, player: Character, day_counter: any, seed: any =None) -> None:
        self.player = player
        self.seed = seed
        self.day_counter = day_counter
        self.areas = {}
        self.castle_unlocked = False

        random.seed(self.seed)
        self.build_town()
        self.build_persistent_dungeons()
    

    def build_town(self) -> None:
        self.areas["Town"] = build_town_graph()

        town = self.areas["Town"]

        for building in town.locations.values():
            if building.name == Town_names.SHOP_INTERIOR.value:
                initialize_shop_inventory(building.extra_metadata)


    def build_persistent_dungeons(self) -> None:
        self.areas["Cave"] = Dungeon_Manager(self.day_counter)
        self.areas["Castle"] = self.build_castle_manager()


    def build_castle_manager(self):
        manager = Dungeon_Manager(self.day_counter)

        deepest_pos = compute_farthest(manager.dungeon_rooms)

        boss_room = manager.dungeon_rooms[deepest_pos]
        boss_room.room_type = Room_Types.BOSS_ROOM
        boss_room.contents["enemies"].clear()
        boss_room.contents["items"].clear()
        manager.spawn_boss_for_room(boss_room)

        return manager
    
    def on_day_advance(self):
        self.day_counter += 1
        self.build_persistent_dungeons()
        self.restock_all_shops(self.areas["Town"])


    def restock_all_shops(self, town: TownGraph):
        for location in town.locations.values():
            if location.name == Town_names.SHOP_INTERIOR.value:
                restock_shop_for_new_day(location.extra_metadata, self.player)

    def get_town(self) -> TownGraph:
        return self.areas["Town"]

    def get_cave(self):
        return self.areas["Cave"]

    def get_castle(self):
        return self.areas["Castle"]
