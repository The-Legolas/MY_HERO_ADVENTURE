"""import sys
import os
# Add the project's root folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
import random
from Dungeon_room_code import Room, Room_Types
from dungeon_manager import Dungeon_Manager, compute_farthest
from .town_logic.town_layout import build_town_graph

class Game_World():
    def __init__(self, day_counter, seed=None) -> None:
        self.seed = seed
        self.day_counter = day_counter
        self.areas = {}
        self.castle_unlocked = False

        random.seed(self.seed)
        self.build_town()
        self.build_persistent_dungeons()
    

    def build_town(self) -> None:
        self.areas["Town"] = build_town_graph()


    def build_persistent_dungeons(self) -> None:
        self.areas["Cave"] = Dungeon_Manager(self.day_counter)
        self.areas["Castle"] = self.build_castle_manager()


    def build_castle_manager(self):
        manager = Dungeon_Manager(self.day_counter)

        deepest_pos = compute_farthest(manager.dungeon_rooms)

        boss_room = manager.dungeon_rooms[deepest_pos]
        boss_room.room_type = Room_Types.BOSS_ROOM
        boss_room.contents["enemies"].clear()
        manager.spawn_boss_for_room(boss_room)

        return manager
    
    def on_day_advance(self):
        self.day_counter += 1
        self.build_persistent_dungeons()


    def __str__(self) -> str:

        output = ""

        for area_name, rooms in self.areas.items():
            room_strs = [str(room) for room in rooms]  # Use each Room's __str__
            output += f"{area_name}: {', '.join(room_strs)}\n"
        return output.strip()  # Remove trailing newline
    
    def room_visualize(self, room) -> list:
        x_values = [pos[0] for pos in room.keys()]
        y_values = [pos[1] for pos in room.keys()]

        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)

        map_rows = []

        for y in range(max_y, min_y - 1, -1):
            row_string = ""

            for x in range(min_x, max_x + 1):
                position = (x, y)

                if position in room:
                    room_pos = room[position]

                    if position == self.starting_position:
                        symbol = "| S |"
                    
                    elif room_pos.room_type == Room_Types.TREASURE_ROOM:
                        symbol = "| T |"

                    elif room_pos.room_type == Room_Types.ENEMY_ROOM:
                        symbol = "| E |"

                    elif room_pos.room_type == Room_Types.EMPTY:
                        symbol = "|EMP|"
                    
                    else:
                        symbol = "| . |"

                else:
                    symbol = "     "
                
                row_string += symbol
        
            map_rows.append(row_string)

        return map_rows



game  = Game_World(40)
print("helloe\n", game, "\n", "\n")

cave_rooms = game.areas["cave"]
map_view = game.room_visualize(cave_rooms)
for line in map_view:
    print(line)


print("\n")
for room in cave_rooms.values():
    print(room.visualize_encounter())