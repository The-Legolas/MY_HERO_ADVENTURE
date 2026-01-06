import json
import os
from typing import Tuple

from game.core.character import Character
from game.core.Heroes import Warrior
from game.core.Status import Status

from game.world.Gen_Game_World import Game_World
from game.world.dungeon_manager import Dungeon_Manager
from game.world.dungeon_room import Room, Room_Types

from game.engine.item_spawner import spawn_item


SAVE_ROOT = "saves"



# SERIALIZATION HELPERS

def _serialize_status(status: Status) -> dict:
    return {
        "id": status.id,
        "remaining_turns": status.remaining_turns,
        "magnitude": status.magnitude,
        "source": status.source,
        "just_applied": status.just_applied,
        "expires_end_of_turn": status.expires_end_of_turn,
    }


def _deserialize_status(data: dict) -> Status:
    s = Status(
        id=data["id"],
        remaining_turns=data["remaining_turns"],
        magnitude=data["magnitude"],
        source=data.get("source"),
        expires_end_of_turn=data.get("expires_end_of_turn", False),
    )
    s.just_applied = data.get("just_applied", False)
    return s


def _serialize_character(player: Character) -> dict:
    return {
        "name": player.name,
        "class_id": player.class_id,
        "base_hp": player.base_hp,
        "base_damage": player.base_damage,
        "base_defence": player.base_defence,
        "hp": player.hp,
        "level": player.level,
        "xp": player.xp,
        "level_bonuses": player.level_bonuses,
        "known_skills": list(player.known_skills),
        "usable_skills": list(player.usable_skills),
        "resource": {
            "current": player.resource_current,
            "max": player.resource_max,
            "name": player.resource_name,
        },
        "inventory": {
            "gold": player.inventory["gold"],
            "items": {
                item_id: entry["count"]
                for item_id, entry in player.inventory["items"].items()
            },
        },
        "equipment": {
            slot: item.id if item else None
            for slot, item in player.equipment.items()
        },
        "statuses": [_serialize_status(s) for s in player.statuses],
    }


def _deserialize_character(data: dict) -> Character:
    if data["class_id"] == "warrior":
        player = Warrior(
            name=data["name"],
            starting_items=None,
            gold=data["inventory"]["gold"],
        )
    else:
        raise ValueError(f"Unknown class_id: {data['class_id']}")

    player.base_hp = data["base_hp"]
    player.base_damage = data["base_damage"]
    player.base_defence = data["base_defence"]

    player.hp = data["hp"]
    player.level = data["level"]
    player.xp = data["xp"]
    player.level_bonuses = data["level_bonuses"]

    player.known_skills = set(data["known_skills"])
    player.usable_skills = list(data["usable_skills"])

    res = data.get("resource")
    if res:
        player.resource_name = res["name"]
        player.resource_current = res["current"]

        # Restore max resource via base + bonuses
        saved_max = res["max"]
        base = player.base_resource
        bonus = max(0, saved_max - base)

        player.level_bonuses["resource"] = bonus
    

    # Inventory
    player.inventory["items"].clear()
    for item_id, count in data["inventory"]["items"].items():
        item = spawn_item(item_id)
        player.inventory["items"][item_id] = {
            "item": item,
            "count": count,
        }

    # Equipment
    for slot, item_id in data["equipment"].items():
        if item_id:
            item = spawn_item(item_id)
            player.equipment[slot] = item

    # Statuses
    player.statuses = [_deserialize_status(s) for s in data["statuses"]]

    return player


def _serialize_dungeon(dungeon: Dungeon_Manager) -> dict:
    return {
        "dungeon_type": dungeon.dungeon_type,
        "day_counter": dungeon.day_counter,
        "player_current_pos": dungeon.player_current_pos,
        "current_depth": dungeon.current_depth,
        "miniboss_room_pos": dungeon.miniboss_room_pos,
        "miniboss_defeated": dungeon.miniboss_defeated,
        "rooms": [
            {
                "x": room.pos_x,
                "y": room.pos_y,
                "room_type": room.room_type.value,
                "visited": room.visited,
                "cleared": room.cleared,
                "treasure_opened": room.treasure_opened,
                "rest_used_day": room.rest_used_day,
                "is_miniboss_room": room.is_miniboss_room,
                "items": [item.id for item in room.contents["items"]],
            }
            for room in dungeon.dungeon_rooms.values()
        ],
    }


def _deserialize_dungeon(data: dict) -> Dungeon_Manager:
    dungeon = Dungeon_Manager(
        day_counter=data["day_counter"],
        dungeon_type=data["dungeon_type"],
    )

    dungeon.dungeon_rooms.clear()

    for r in data["rooms"]:
        room = Room(
            Room_Types(r["room_type"]),
            r["x"],
            r["y"],
            day_counter=data["day_counter"],
        )
        room.visited = r["visited"]
        room.cleared = r["cleared"]
        room.treasure_opened = r["treasure_opened"]
        room.rest_used_day = r.get("rest_used_day")
        room.is_miniboss_room = r["is_miniboss_room"]

        room.contents["items"] = [spawn_item(i) for i in r["items"]]
        room.contents["enemies"] = []  # enemies are respawned by state, not combat

        dungeon.dungeon_rooms[(r["x"], r["y"])] = room

    dungeon.player_current_pos = tuple(data["player_current_pos"])
    dungeon.current_depth = data["current_depth"]
    dungeon.miniboss_room_pos = (
        tuple(data["miniboss_room_pos"])
        if data["miniboss_room_pos"]
        else None
    )
    dungeon.miniboss_defeated = data["miniboss_defeated"]

    return dungeon


# PUBLIC API

def save_game(engine, slot_name: str) -> None:
    os.makedirs(SAVE_ROOT, exist_ok=True)
    slot_dir = os.path.join(SAVE_ROOT, slot_name)
    os.makedirs(slot_dir, exist_ok=True)

    data = {
        "player": _serialize_character(engine.player),
        "world": {
            "day_counter": engine.world.day_counter,
            "seed": engine.world.seed,
            "castle_unlocked": engine.world.castle_unlocked,
            "cave": _serialize_dungeon(engine.world.get_cave()),
            "castle": _serialize_dungeon(engine.world.get_castle()),
        },
    }

    with open(os.path.join(slot_dir, "save.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_game(slot_name: str) -> Tuple[Character, Game_World]:
    path = os.path.join(SAVE_ROOT, slot_name, "save.json")
    if not os.path.exists(path):
        raise FileNotFoundError("Save file does not exist.")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    player = _deserialize_character(data["player"])

    world_data = data["world"]
    world = Game_World(
        player=player,
        day_counter=world_data["day_counter"],
        seed=world_data["seed"],
    )

    world.castle_unlocked = world_data["castle_unlocked"]
    world.areas["Cave"] = _deserialize_dungeon(world_data["cave"])
    world.areas["Castle"] = _deserialize_dungeon(world_data["castle"])

    return player, world
