import unittest
from types import SimpleNamespace

from game.world.town_logic.guide_logic import (
    get_guide_display_name,
    get_guide_dialogue,
)

from game.ui.dialog.guide_dialogue import (
    GUIDE_NAME,
    INTRO_DIALOGUE,
    CASTLE_UNLOCKED_MESSAGE,
    HINT_MESSAGES,
)


class DummyWorld:
    def __init__(self):
        self.castle_unlocked = False
        self.guide_state = {
            "introduced": False,
            "castle_notice_given": False,
        }


class DummyEngine:
    def __init__(self, world):
        self.world = world
        self._cycle_calls = []

    def _cycle_message(self, key, messages):
        self._cycle_calls.append((key, messages))
        return messages[0]


class TestGuideDisplayName(unittest.TestCase):

    def test_guide_name_hidden_before_intro(self):
        world = DummyWorld()

        name = get_guide_display_name(world)

        self.assertEqual(name, "Unknown Figure")

    def test_guide_name_visible_after_intro(self):
        world = DummyWorld()
        world.guide_state["introduced"] = True

        name = get_guide_display_name(world)

        self.assertEqual(name, GUIDE_NAME)


class TestGuideDialogueFlow(unittest.TestCase):

    def test_first_interaction_returns_intro(self):
        world = DummyWorld()
        engine = DummyEngine(world)

        dialogue = get_guide_dialogue(engine)

        self.assertEqual(dialogue, INTRO_DIALOGUE)
        self.assertTrue(world.guide_state["introduced"])

    def test_castle_unlocked_message_only_once(self):
        world = DummyWorld()
        engine = DummyEngine(world)

        get_guide_dialogue(engine)

        world.castle_unlocked = True

        dialogue = get_guide_dialogue(engine)

        self.assertEqual(dialogue, CASTLE_UNLOCKED_MESSAGE)
        self.assertTrue(world.guide_state["castle_notice_given"])

        dialogue_2 = get_guide_dialogue(engine)

        self.assertNotEqual(dialogue_2, CASTLE_UNLOCKED_MESSAGE)

    def test_hint_cycle_used_after_intro_and_castle_notice(self):
        world = DummyWorld()
        engine = DummyEngine(world)

        get_guide_dialogue(engine)

        world.castle_unlocked = True
        get_guide_dialogue(engine)

        dialogue = get_guide_dialogue(engine)

        self.assertEqual(dialogue, HINT_MESSAGES[0])
        self.assertEqual(engine._cycle_calls[0][0], "guide")
