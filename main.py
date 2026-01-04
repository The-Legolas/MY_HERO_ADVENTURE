from game.core.character import Character
from game.core.Heroes import Warrior
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.game_engine import GameEngine
from game.ui.text_screens import TextScreen

"""
currently __ lines of code as of the previous git commit
Bugs:

Fixed:
Statuses should have a chance to apply even if the attack is blocked. (or makeing it so if defence is more than the attack (and not defending) only doing halve dmg)
add burn to flame_breath skill, add bleed to rending_bite, add armor_down (weakening for defence) to acid_splash


Like to have:
note 4: in the code base search for #fix to find things to remove before final game release
note 6: update shop and tressure inventory to hold some of the new items

"""


def main():

    title_screen()

    show_intro_story()

    choice = input("Do you want to see the tutorial? (yes/no)\n> ").strip().lower()
    if choice in ("yes", "y"):
        show_system_guide()

    player_hero = pick_character_and_name()
    
    game_world = Game_World(player_hero, day_counter=1)
    game_town = game_world.get_town()
    game_town.set_starting_location(Town_names.TOWN_GATE.value)

    engine = GameEngine(player=player_hero, game_world=game_world)

    print("\nLet the adventure begin.\n")

    engine.run()




def title_screen() -> None:
    print("  _________________________________")
    print("\tHello and welcome to:")
    print("\tMy hero adventure")
    print("\n\t\t    by The-Legolas")
    print("  _________________________________\n")

def show_intro_story() -> None:
    intro = TextScreen(
        title="Prologue",
        pages=[
            (
                "The town was never meant to last.\n\n"
                "Built against the rock and shadow, it survives on trade, stubbornness, "
                "and the promise that the darkness below can be held back, for a time."
            ),

            (
                "Lately, the cave has changed.\n\n"
                "Creatures roam deeper than before. Paths collapse overnight. "
                "And some who enter do not return.\n\n"
                "The castle above the town remains sealed. Whatever lies within "
                "was locked away long ago… and for good reason."
            ),

            (
                "You arrive as many before you have armed, capable, and looking for work.\n\n"
                "Gold can be earned in the dark.\n"
                "Whether you leave richer, wiser, or not at all…\n"
                "depends on how deep you dare to go."
            )
            
        ]
    )

    intro.show()
    print("\n")


def show_system_guide():
    guide = TextScreen(
        title="System Guide",
        pages=[
            (
                "BASIC INPUT:\n\n"
                "Most menus use numbered choices. Simply type the number shown.\n\n"
                "Some actions require typed commands instead of numbers:\n"
                "- inventory\n"
                "- save\n"
                "- load"
            ),

            (
                "SHORT COMMANDS:\n\n"
                "Many commands can be shortened:\n"
                "- i → inventory\n"
                "- c → cancel / back\n\n"
                "The game will usually accept either form."
            ),

            (
                "DUNGEON MAP SYMBOLS:\n\n"
                "In the dungeon part of the game a map layout will be displayed.\n\n"
                "◎  You (player)\n"
                "⚔  Enemy room\n"
                "☠  Boss room\n"
                "✦  Treasure room\n"
                "✚  Rest area\n"
                "·  Empty room"
            ),

            (
                "STATUS ICONS:\n\n"
                "☠ Poison       → takes damage over time\n"
                "✚ Regen        → recovers health over time\n"
                "💫 Stun        → cannot act\n"
                "⬇ Weakened     → reduced damage\n"
                "⚔ Strength     → increased damage\n"
                "🛡 Defending    → increased defence"
            ),
        ]
    )
    guide.show()
    print("\n")


def pick_character_and_name() -> Character:
    print("skip")
    """while True:
        print("\nPlease pick your character from amoung these options")on_day_advance
        hero_choice = input("(Warrior, Archer, or Wizard): ").strip().lower()

        if hero_choice in ("warrior", "archer", "wizard"):
            break

        print("please try again.")"""
    
    while True:
        hero_name = input("\nAnd what shall be your name?\n: ")
        yes_no = input(f"Is '{hero_name}' correct? (Yes or No)\n: ").strip().lower()

        if yes_no == "yes" or yes_no == "y":
            break

    #if hero_choice: #hero_choice == "warrior":
    player_hero = Warrior(hero_name, starting_items=None)
    
    return player_hero


if __name__ == "__main__":
    main()
