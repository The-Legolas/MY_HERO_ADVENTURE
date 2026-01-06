import unittest
from unittest.mock import patch

from game.world.dungeon_room import (
    Room,
    Room_Types,
    treasure_room_spawner,
    boss_room_spawner,
)
from game.core.Enemy_class import Enemy
from game.core.Item_class import Items


class TestRoomInitialization(unittest.TestCase):

    def test_empty_room_initializes_clean(self):
        room = Room(Room_Types.EMPTY, 0, 0)

        self.assertEqual(room.room_type, Room_Types.EMPTY)
        self.assertEqual(room.contents["enemies"], [])
        self.assertEqual(room.contents["items"], [])
        self.assertFalse(room.visited)
        self.assertFalse(room.cleared)
        self.assertFalse(room.treasure_opened)

    def test_enemy_room_has_no_pre_spawned_content(self):
        room = Room(Room_Types.ENEMY_ROOM, 1, 1)

        self.assertEqual(room.room_type, Room_Types.ENEMY_ROOM)
        self.assertEqual(room.contents["enemies"], [])
        self.assertEqual(room.contents["items"], [])

    def test_rest_room_has_no_pre_spawned_content(self):
        room = Room(Room_Types.REST_ROOM, 2, 2)

        self.assertEqual(room.room_type, Room_Types.REST_ROOM)
        self.assertEqual(room.contents["enemies"], [])
        self.assertEqual(room.contents["items"], [])
        self.assertIsNone(room.rest_used_day)

    def test_treasure_room_spawns_items(self):
        room = Room(Room_Types.TREASURE_ROOM, 3, 3)

        self.assertEqual(room.room_type, Room_Types.TREASURE_ROOM)
        self.assertIsInstance(room.contents["items"], list)

        for item in room.contents["items"]:
            self.assertIsInstance(item, Items)

    def test_boss_room_spawns_enemies(self):
        room = Room(Room_Types.BOSS_ROOM, 4, 4, day_counter=1)

        self.assertEqual(room.room_type, Room_Types.BOSS_ROOM)
        self.assertGreaterEqual(len(room.contents["enemies"]), 1)

        for enemy in room.contents["enemies"]:
            self.assertIsInstance(enemy, Enemy)


class TestTreasureRoomSpawner(unittest.TestCase):

    def test_treasure_spawner_returns_list(self):
        items = treasure_room_spawner()
        self.assertIsInstance(items, list)

    def test_treasure_spawner_items_are_valid(self):
        items = treasure_room_spawner()

        for item in items:
            self.assertIsInstance(item, Items)

    def test_treasure_spawner_max_reasonable_count(self):
        items = treasure_room_spawner()
        self.assertLessEqual(len(items), 4)


class TestBossRoomSpawner(unittest.TestCase):

    def test_boss_room_spawns_boss(self):
        enemies = boss_room_spawner(day_counter=1)

        self.assertTrue(any(isinstance(e, Enemy) for e in enemies))
        self.assertGreaterEqual(len(enemies), 1)

    def test_high_day_counter_can_spawn_extra_enemy(self):
        enemies = boss_room_spawner(day_counter=50)

        self.assertGreaterEqual(len(enemies), 1)
        for enemy in enemies:
            self.assertIsInstance(enemy, Enemy)


class TestRoomStringRepresentation(unittest.TestCase):

    def test_room_str_does_not_crash(self):
        room = Room(Room_Types.EMPTY, 0, 0)
        result = str(room)

        self.assertIsInstance(result, str)
        self.assertIn(room.room_type.value, result)