import sys
import os
# Add the project's root folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from enum import Enum
from Dungeon_room_code import Room, Room_Types

class Game_World():
    def __init__(self, day_counter, seed=None) -> None:
        self.seed = seed
        self.areas = {}
        self.day_counter = day_counter
        self.build_world()
    
    def build_world(self) -> None:
        self.build_town()
        random.seed(self.seed)
        self.build_cave()
        self.build_castle()

    def build_town(self) -> None:
        town_rooms = []
        town_rooms.append(Room(Room_Types.TAVERN, day_counter=self.day_counter))
        town_rooms.append(Room(Room_Types.SHOP, day_counter=self.day_counter))
        town_rooms.append(Room(Room_Types.INN, day_counter=self.day_counter))

        self.areas["Town"] = town_rooms
    
    def build_cave(self) -> dict:
        self.starting_position = (0,0)
        self.starting_room = Room(Room_Types.EMPTY)

        cave_rooms = {
            self.starting_position: self.starting_room,
        }

        base_size = 12
        difficulty_factor = 1 + (self.day_counter * 0.05)
        room_count = base_size + int(self.day_counter * 0.2)

        enemy_room_chance = min(0.5 + self.day_counter * 0.01, 0.9)
        treasure_room_chance = max(0.2 - self.day_counter * 0.005, 0.05)

        current_position = self.starting_position

        for _ in range(room_count):
            next_position = pick_random_adjacent(current_position)

            if next_position not in cave_rooms:
                room_type = choose_room_type(enemy_room_chance, treasure_room_chance)
                x, y = next_position
                cave_rooms[next_position] = Room(room_type,
                                                 pos_x=x,
                                                 pos_y=y,
                                                 day_counter=self.day_counter)
            
                current_position = next_position
        
        self.areas["cave"] = cave_rooms

        return cave_rooms

        # old logic for liniar system
        """cave_rooms = []

        for _ in range(5):
            rnd = random.random()
            if rnd < 1:
                room = Room(Room_Types.ENEMY_ROOM, day_counter=self.day_counter)
            else:
                room = Room(Room_Types.TRESSURE_ROOM, day_counter=self.day_counter)
            cave_rooms.append(room)
        
        self.areas["Cave"] = cave_rooms"""
    
    def build_castle(self):
        castle_rooms = []

        for _ in range(5):
            rnd = random.random()
            if rnd < 0.6:
                room = Room(Room_Types.ENEMY_ROOM, day_counter=self.day_counter)
            else:
                room = Room(Room_Types.TREASURE_ROOM, day_counter=self.day_counter)
            castle_rooms.append(room)
        boss_room = Room(Room_Types.BOSS_ROOM)
        castle_rooms.append(boss_room)
        
        self.areas["Castle"] = castle_rooms

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



def pick_random_adjacent(position) -> tuple:
    x, y = position
    direction = random.choice(["north", "south", "east", "west"])

    match direction:
        case "north":
            return (x, y + 1)
        case "south":
            return (x, y - 1)
        case "east":
            return (x + 1, y)
        case "west":
            return (x - 1, y)


def choose_room_type(enemy_chance, treasure_chance) -> Enum:
    rnd = random.random()

    if rnd < enemy_chance:
        return Room_Types.ENEMY_ROOM
    elif rnd < (enemy_chance + treasure_chance):
        return Room_Types.TREASURE_ROOM
    else:
        return Room_Types.EMPTY



game  = Game_World(40)
print("helloe\n", game, "\n", "\n")

cave_rooms = game.build_cave()
map_view = game.room_visualize(cave_rooms)
for line in map_view:
    print(line)


print("\n")
for room in cave_rooms.values():
    print(room.visualize_encounter())