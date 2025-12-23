import random
from game.world.Dungeon_room_code import Room, Room_Types
from game.core.Enemy_class import Enemy_Spawner, spawn_enemy

class Dungeon_Manager():
    def __init__(self, day_counter: int, dungeon_type: str):
        self.day_counter = day_counter
        self.dungeon_type = dungeon_type
        
        self.player_starting_pos = (0,0)
        self.player_current_pos = (0,0)
        self.current_depth = 0
        self.generate_dungeon()

    
    def generate_dungeon(self):
        self.dungeon_rooms = {}

        start_x, start_y = self.player_starting_pos
        starting_room = Room(Room_Types.EMPTY, start_x, start_y, day_counter=self.day_counter)
        self.dungeon_rooms[start_x, start_y] = starting_room

        base_size = 20
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


    def get_available_moves(self) -> dict[str, tuple[int, int]]:
        px, py = self.player_current_pos

        candidates = {
            "north": (px, py + 1),
            "south": (px, py - 1),
            "east":  (px + 1, py),
            "west":  (px - 1, py),
        }

        return {
            direction: pos
            for direction, pos in candidates.items()
            if pos in self.dungeon_rooms
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

    def process_room_on_enter(self, room: Room) -> dict[str, list]:
        encounter = {
            "spawned_enemies": [],
            "special_events": []
        }

        if room.visited:
            return encounter
        
        room.visited = True

        if room.room_type == Room_Types.ENEMY_ROOM and not room.cleared:
            enemy = self.spawn_enemy_for_room(room)
            if enemy:
                encounter["spawned_enemies"].append(enemy)

        if room.room_type == Room_Types.BOSS_ROOM and not room.cleared:
            boss = self.spawn_boss_for_room(room)
            encounter["spawned_enemies"].append(boss)
        
        return encounter



    def spawn_enemy_for_room(self, room: Room):
        if room.room_type not in (Room_Types.ENEMY_ROOM, Room_Types.BOSS_ROOM):
            return
        
        if len(room.contents["enemies"]) > 2:
            return room.contents["enemies"]
        
        depth = self.compute_depth(pos=(room.pos_x, room.pos_y))

        enemy_type  = Enemy_Spawner.get_random_template_weighted()

        enemy_obj = spawn_enemy(enemy_type)
        
        enemy_obj.scale_stats(self.day_counter, depth)

        room.contents["enemies"].append(enemy_obj)

        return enemy_obj

    def spawn_boss_for_room(self, room):
        from game.core.Enemy_class import Enemy_type

        depth = self.compute_depth((room.pos_x, room.pos_y))

        boss = spawn_enemy(Enemy_type.ENEMY_BOSS_DRAGON)
        boss.scale_stats(self.day_counter, depth)

        room.contents["enemies"].append(boss)
        return boss


    def room_exists(self, x: int, y: int) -> dict[str, any]:
        pos = (x, y)
        room = self.dungeon_rooms.get(pos)

        return {
            "exists": room is not None,
            "room": room
        }
    
    def open_treasure(self, room: Room) -> list:
        if room.room_type != Room_Types.TREASURE_ROOM:
            return []

        if room.treasure_opened:
            return []
        
        room.treasure_opened = True
        return room.contents["items"]
    
    
    def inspect_room(self, room: Room) -> str:
        depth = self.compute_depth((room.pos_x, room.pos_y))
        boss_distance = self.distance_to_boss()
        dungeon = self.dungeon_type

        mood = pick_flavor(
            dungeon,
            "depth",
            depth_tier(depth),
        )
        boss_mood = pick_flavor(
            dungeon,
            "boss",
            boss_tier(boss_distance),
        )

        return (
            f"\n{mood}\n"
            f"You are {depth} levels deep.\n"
            f"{boss_mood}\n"
            )


    def resolve_room_entry(self, room: Room):
        encounter = self.process_room_on_enter(room)

        result = {
            "start_combat": False,
            "enemies": [],
            "message": None
        }

        if encounter["spawned_enemies"]:
            result["start_combat"] = True
            result["enemies"] = encounter["spawned_enemies"]

            if room.room_type == Room_Types.BOSS_ROOM:
                result["message"] = "A terrifying presence fills the room."
            
            else:
                result["message"] = "Enemies emerge from the shadows."
        
        return result
    
    def get_boss_position(self)  -> tuple:
        return compute_farthest(self.dungeon_rooms)
    
    def distance_to_boss(self):
        boss_pos = self.get_boss_position()
        player_pos = self.player_current_pos

        if boss_pos is None:
            return None
        
        bx, by = boss_pos
        px, py = player_pos

        dx = abs(bx - px)
        dy = abs(by - py)

        return dx + dy
    
    def get_room_action_label(self, room: Room) -> str | None:
        if room.room_type == Room_Types.TREASURE_ROOM and not room.treasure_opened:
            return "Open chest"

        if room.room_type == Room_Types.ENEMY_ROOM and room.cleared:
            return None

        return None
    
    def room_action(self, room: Room):
        if room.room_type == Room_Types.TREASURE_ROOM and not room.treasure_opened:
            items = self.open_treasure(room)
            if items:
                return {
                    "items": items,
                    "message": "You open the chest."
                }
            else:
                return {
                    "items": items,
                    "message": "You open the chest, but it was empty"
                }

        return None


    def room_visualize(self) -> list:
        x_values = [pos[0] for pos in self.dungeon_rooms.keys()]
        y_values = [pos[1] for pos in self.dungeon_rooms.keys()]

        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)

        map_rows = []

        for y in range(max_y, min_y - 1, -1):
            row_string = ""

            for x in range(min_x, max_x + 1):
                position = (x, y)

                if position in self.dungeon_rooms:
                    room_pos = self.dungeon_rooms[position]

                    if position == self.player_current_pos:
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

def compute_farthest(dungeon_rooms) -> tuple:
    if not dungeon_rooms:
        return None

    best_pos = None
    best_depth = -1

    for pos in dungeon_rooms.keys():
        x, y = pos
        depth = max(abs(x), abs(y))
        if depth > best_depth:
            best_depth = depth
            best_pos = pos
        elif depth == best_depth:
            bx, by = best_pos
            if (abs(x), abs(y)) > (abs(bx), abs(by)):
                best_pos = pos

    return best_pos


def depth_tier(depth: int) -> str:
    if depth < 2:
        return "shallow"
    elif depth < 6:
        return "mid"
    else:
        return "deep"


def boss_tier(distance: int) -> str:
    if distance < 3:
        return "close"
    elif distance < 8:
        return "mid"
    else:
        return "far"


def pick_flavor(dungeon: str, category: str, tier: str) -> str:
    return random.choice(FLAVOR_TEXT[dungeon][category][tier])


FLAVOR_TEXT = {
    "cave": {
        "depth": {
            "shallow": [
                "The stone walls are cool to the touch, damp with condensation.",
                "Water drips steadily somewhere in the dark.",
                "The air smells of earth and wet rock.",
                "Faint echoes follow even the smallest sound.",
                "The cave feels quiet, but not abandoned.",
            ],
            "mid": [
                "The walls are uneven and scarred, as if something clawed through the stone.",
                "The air is thick and hard to breathe.",
                "Shadows cling unnaturally to the corners of the cave.",
                "The ground is slick, coated in mud and something darker.",
                "Every sound feels louder than it should.",
            ],
            "deep": [
                "Cracks split the walls, oozing moisture and decay.",
                "The air is stale and oppressive, heavy in your lungs.",
                "You feel watched, though nothing moves.",
                "The darkness here seems to swallow light.",
                "The cave feels hostile, as if it wants you gone.",
            ],
        },
        "boss": {
            "far": [
                "The echoes here feel slightly distorted.",
                "The cave air carries a faint, unfamiliar smell.",
                "Loose stones shift when you move.",
            ],
            "mid": [
                "The walls seem to close in around you.",
                "Your footsteps echo longer than they should.",
                "The air is heavy, pressing against your lungs.",
            ],
            "close": [
                "The stone vibrates faintly beneath your feet.",
                "The darkness feels alive, watching you.",
                "The cave itself seems to recoil from something ahead.",
            ],
        },
    },

    "castle": {
        "depth": {
            "shallow": [
                "Cold marble floors stretch out before you.",
                "Dust coats every surface, undisturbed for ages.",
                "The air is still and unnaturally quiet.",
                "Faded banners hang limply from the walls.",
                "Your footsteps echo through empty corridors.",
            ],
            "mid": [
                "Cracks run along the marble walls.",
                "The air is heavy and stale, clinging to your skin.",
                "Broken statues stare with hollow eyes.",
                "The silence feels deliberate, oppressive.",
                "The castle feels less abandoned than it should.",
            ],
            "deep": [
                "The walls are fractured and bleeding dark stains.",
                "The air is suffocating, thick with dread.",
                "Shadows writhe unnaturally across the stone.",
                "Every instinct tells you to flee.",
                "This place radiates malice.",
            ],
        },
        "boss": {
            "far": [
                "The air here is colder than the surrounding halls.",
                "Distant sounds echo briefly, then vanish.",
                "The walls bear fresh cracks and damage.",
            ],
            "mid": [
                "The silence is oppressive and deliberate.",
                "The air feels stale, heavy with old hatred.",
                "The castle seems to loom over you.",
            ],
            "close": [
                "The stone walls radiate malice.",
                "The air grows thick, choking and cold.",
                "You can feel the presence waiting just ahead.",
            ],
        },
    },

    "swamp": {
        "depth": {
            "shallow": [
                "The ground squelches beneath your feet.",
                "Thick reeds sway gently in the stagnant water.",
                "The air is humid and smells faintly of rot.",
                "Insects buzz lazily around you.",
                "Murky water reflects the dull sky above.",
            ],
            "mid": [
                "The water grows darker and deeper with every step.",
                "Rotting vegetation floats on the surface.",
                "The buzzing of insects becomes constant and maddening.",
                "The air feels warm and suffocating.",
                "You swear something moved beneath the water.",
            ],
            "deep": [
                "The water is black and foul, reeking of decay.",
                "Dead trees loom like twisted corpses.",
                "The air is thick with spores and rot.",
                "Every step threatens to pull you under.",
                "The swamp feels alive—and hungry.",
            ],
        },
        "boss": {
            "far": [
                "The water ripples without any clear cause.",
                "The insects grow suddenly quiet.",
                "A foul scent drifts on the stagnant air.",
            ],
            "mid": [
                "The swamp water churns slowly around you.",
                "The air is thick, heavy with decay.",
                "You feel something moving beneath the surface.",
            ],
            "close": [
                "The water pulls at your legs as if alive.",
                "The swamp grows unnaturally silent.",
                "You feel eyes on you from every direction.",
            ],
        },
    },
}
