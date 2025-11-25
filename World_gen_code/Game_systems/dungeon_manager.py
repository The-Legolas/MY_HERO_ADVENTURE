import random
from World_gen_code.Dungeon_room_code import Room, Room_Types
from Game_systems.Enemy_class import Enemy_Spawner, spawn_enemy

class Dungeon_Manager():
    def __init__(self, day_counter):
        self.day_counter = day_counter
        
        self.player_starting_pos = (0,0)
        self.player_current_pos = (0,0)
        self.current_depth = 0
        self.generate_dungeon()

    
    def generate_dungeon(self):
        self.dungeon_rooms = {}

        start_x, start_y = self.player_starting_pos
        starting_room = Room(Room_Types.EMPTY, start_x, start_y, day_counter=self.day_counter)
        self.dungeon_rooms[start_x, start_y] = starting_room

        base_size = 12
        dungeon_room_count = base_size + int(self.day_counter * 0.2)

        current_pos = (0, 0)

        for _ in range(dungeon_room_count):
            next_pos = pick_random_adjacent(current_pos)

            if next_pos not in self.dungeon_rooms:
                x, y = next_pos

                room_type = roll_room_type(self.day_counter)
                new_room = Room(room_type, x, y, day_counter=self.day_counter)

                self.dungeon_rooms[next_pos] = new_room

                current_pos = next_pos
    
    def direction_to_offset(self, direction: str) -> tuple:
        direction = direction.lower()
        
        match direction:
            case "north":
                return (0, 1)
            case "south":
                return (0, -1)
            case "east":
                return (1, 0)
            case "west":
                return (-1, 0)
        return None


    def move_player(self, direction: str):
        offset = self.direction_to_offset(direction)
        
        if offset is None:
            return {"success": False, "reason": "Invalid direction"}
    
        dx, dy = offset
        px, py = self.player_current_pos
        new_pos = (px + dx, py + dy)

        if new_pos not in self.dungeon_rooms:
            return {"success": False, "reason": "You cannot go that way."}
        
        self.player_current_pos = new_pos

        self.current_depth = self.compute_depth(new_pos)

        return {
            "success": True,
            "new_pos": new_pos,
            "depth": self.current_depth,
            "room": self.dungeon_rooms[new_pos]
        }
    

    def compute_depth(self, pos: tuple[int, int] | None = None):
        
        #   Computes ring-depth based on coordinates.
        #   If no position is supplied, computes depth of the player's position.
        
        if pos is None:
            pos = self.player_current_pos

        x, y = pos
        return max(abs(x), abs(y))


    def get_current_room(self):
        
        pos = self.player_current_pos

        return {
            "pos": pos,
            "room": self.dungeon_rooms.get(pos, None),
            "depth": self.compute_depth(pos)
        }


    def spawn_enemy_for_room(self, room: Room):
        if room.room_type != Room_Types.ENEMY_ROOM:
            return
        
        if len(room.contents["enemies"]) > 0:
            return room.contents["enemies"][0]
        
        depth = self.compute_depth(pos=(room.pos_x, room.pos_y))

        enemy_type  = Enemy_Spawner.get_random_template_weighted()

        enemy_obj = spawn_enemy(enemy_type)
        
        enemy_obj.scale_stats(self.day_counter, depth)

        room.contents["enemies"].append(enemy_obj)

        return enemy_obj


    def room_exists(self, x: int, y: int) -> dict[str, any]:
        pos = (x, y)
        room = self.dungeon_rooms.get(pos)

        return {
            "exists": room is not None,
            "room": room
        }




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


def roll_room_type(day_counter) -> Room_Types:
    enemy_chance = min(0.50 + day_counter * 0.01, 0.90)
    treasure_chance = max(0.20 - day_counter * 0.005, 0.05)

    rnd = random.random()

    if rnd < enemy_chance:
        return Room_Types.ENEMY_ROOM
    elif rnd < (enemy_chance + treasure_chance):
        return Room_Types.TREASURE_ROOM
    else:
        return Room_Types.EMPTY

