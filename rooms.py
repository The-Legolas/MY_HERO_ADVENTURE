from enum import Enum
import random

class Game_World():
    def __init__(self, seed=None):
        self.seed = seed
        self.areas = {}
        self.build_world()
    
    def build_world(self):
        self.build_town()
        self.build_cave()
        self.build_castle()

    def build_town(self):
        town_rooms = []
        town_rooms.append(Room(Room_Types.TAVERN))
        town_rooms.append(Room(Room_Types.SHOP))
        town_rooms.append(Room(Room_Types.INN))

        self.areas["Town"] = town_rooms
    
    def build_cave(self):
        cave_rooms = []
        random.seed(self.seed)

        for _ in range(5):
            rnd = random.random()
            if rnd < 0.6:
                room = Room(Room_Types.ENEMY_ROOM)
            else:
                room = Room(Room_Types.TRESSURE_ROOM)
            cave_rooms.append(room)
        
        self.areas["Cave"] = cave_rooms
    
    def build_castle(self):
        castle_rooms = []
        random.seed(self.seed)

        for _ in range(5):
            rnd = random.random()
            if rnd < 0.6:
                room = Room(Room_Types.ENEMY_ROOM)
            else:
                room = Room(Room_Types.TRESSURE_ROOM)
            castle_rooms.append(room)
        boss_room = []
        castle_rooms.append(boss_room)
        
        self.areas["Castle"] = castle_rooms



class Room_Types(Enum):
    EMPTY = "empty"
    ENEMY_ROOM = "enemy room"
    TRESSURE_ROOM = "tressure room"
    TAVERN = "tavern"
    SHOP = "shop"
    INN = "inn"
    BOSS_ROOM = "boss room"


class Room():
    def __init__(self, room_type):
        
        match room_type:
            case Room_Types.TRESSURE_ROOM:
                self.room_type = ["item"]
            
            case Room_Types.ENEMY_ROOM:
                self.room_type = ["bat"]
            
            case _: #Types.EMPTY
                self.room_type = []




game  = Game_World()
print(game)