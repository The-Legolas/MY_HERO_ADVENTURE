import unittest
from unittest.mock import patch

from game.world.dungeon_manager import Dungeon_Manager
from game.world.Dungeon_room_code import Room_Types
from game.core.Status import Enemy_Rarity


class TestDungeonGeneration(unittest.TestCase):

    def test_dungeon_generates_rooms(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        self.assertTrue(len(dungeon.dungeon_rooms) > 0)
        self.assertIn((0, 0), dungeon.dungeon_rooms)

    def test_miniboss_room_assigned(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        self.assertIsNotNone(dungeon.miniboss_room_pos)
        room = dungeon.dungeon_rooms[dungeon.miniboss_room_pos]
        self.assertTrue(room.is_miniboss_room)


class TestMovement(unittest.TestCase):

    def test_move_player_valid_direction(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        moves = dungeon.get_available_moves()
        direction = next(iter(moves))

        result = dungeon.move_player(direction)

        self.assertTrue(result["success"])
        self.assertEqual(dungeon.player_current_pos, result["new_pos"])

    def test_move_player_invalid_direction(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        result = dungeon.move_player("upwards")

        self.assertFalse(result["success"])


class TestDepthComputation(unittest.TestCase):

    def test_compute_depth_origin(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        self.assertEqual(dungeon.compute_depth((0, 0)), 0)

    def test_compute_depth_ring(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        self.assertEqual(dungeon.compute_depth((3, -1)), 3)


class TestRoomEntry(unittest.TestCase):

    def test_rest_room_no_enemies(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        rest_room = None
        for room in dungeon.dungeon_rooms.values():
            if room.room_type == Room_Types.REST_ROOM:
                rest_room = room
                break

        if rest_room is None:
            self.skipTest("No rest room generated")

        result = dungeon.process_room_on_enter(rest_room)
        self.assertEqual(result["spawned_enemies"], [])

    def test_enemy_room_spawns_enemies_once(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        enemy_room = None
        for room in dungeon.dungeon_rooms.values():
            if room.room_type == Room_Types.ENEMY_ROOM:
                enemy_room = room
                break

        if enemy_room is None:
            self.skipTest("No enemy room generated")

        first = dungeon.process_room_on_enter(enemy_room)
        second = dungeon.process_room_on_enter(enemy_room)

        self.assertTrue(first["spawned_enemies"])
        self.assertEqual(second["spawned_enemies"], [])


class TestRoomActions(unittest.TestCase):

    def test_rest_room_action(self):
        dungeon = Dungeon_Manager(day_counter=1, dungeon_type="cave")

        rest_room = None
        for room in dungeon.dungeon_rooms.values():
            if room.room_type == Room_Types.REST_ROOM:
                rest_room = room
                break

        if rest_room is None:
            self.skipTest("No rest room generated")

        result = dungeon.room_action(rest_room)

        self.assertTrue(result["rest"])
        self.assertIn("message", result)


class TestBossRoom(unittest.TestCase):

    def test_spawn_boss_for_room(self):
        dungeon = Dungeon_Manager(day_counter=5, dungeon_type="castle")

        boss_room = None
        for room in dungeon.dungeon_rooms.values():
            if room.room_type == Room_Types.BOSS_ROOM:
                boss_room = room
                break

        if boss_room is None:
            self.skipTest("No boss room generated")

        enemies = boss_room.contents["enemies"]

        self.assertEqual(len(enemies), 1)
        self.assertEqual(enemies[0].rarity, Enemy_Rarity.BOSS)
