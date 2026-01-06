from game.ui.dialog.guide_dialogue import GUIDE_NAME, INTRO_DIALOGUE, HINT_MESSAGES, CASTLE_UNLOCKED_MESSAGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine.game_engine import GameEngine
    from game.world.Gen_Game_World import Game_World

def get_guide_display_name(world: 'Game_World') -> str:
    return GUIDE_NAME if world.guide_state["introduced"] else "Unknown Figure"


def get_guide_dialogue(engine: 'GameEngine') -> str:
    world = engine.world

    # Priority 1: First introduction
    if not world.guide_state["introduced"]:
        world.guide_state["introduced"] = True
        return INTRO_DIALOGUE
    
    # Priority 2: Castle unlocked message (once)
    if world.castle_unlocked and not world.guide_state["castle_notice_given"]:
        world.guide_state["castle_notice_given"] = True
        return CASTLE_UNLOCKED_MESSAGE

    # Priority 3: Cycled hints
    return engine._cycle_message("guide", HINT_MESSAGES)
