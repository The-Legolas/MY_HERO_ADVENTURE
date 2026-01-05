from game.core.character import Character
from game.core.Heroes import Warrior
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.game_engine import GameEngine
from game.ui.text_screens import TextScreen

"""
currently __ lines of code as of the previous git commit
Bugs:
note 1: Ring of Corruption and Ring of Vital Flow doesn't have a descipteve text like Ring of Iron Will
note 1.5: weapon effect aren't in the inventory description either
note 2: no ux for if the player is stunned

Test:
1. re-test combat wiht the correct amount of health and dmg

Fixed:
updated shop and tressure inventory to hold some of the new items
made it so a max of 1 special item can be awarded per chest
tested that all skills and stamna works correctly
tested all items to make sure they work
added add intents to all enemy skills
Tested all enemies and tested all attacks
made the inventory screen have the same beauty as the buy menu


Like to have:
note 1: in the code base search for #fix to find things to remove before final game release
note 2: make a proper start menu
note 3: make the sell menu have the same beauty as the buy menu
note 4: refractor when done so all enums and such have their own folder

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
    print("""
_______________________________________________________________________________________________                                                         
 _____     _ _                  _    _ _ _     _                      _       _ 
|  |  |___| | |___    ___ ___ _| |  | | | |___| |___ ___ _____ ___   | |_ ___|_|
|     | -_| | | . |  | .'|   | . |  | | | | -_| |  _| . |     | -_|  |  _| . |_ 
|__|__|___|_|_|___|  |__,|_|_|___|  |_____|___|_|___|___|_|_|_|___|  |_| |___|_|
""")
    input()
    print(
"""
  __  __         _                                _                 _                  
 |  \\/  |       | |                              | |               | |                 
 | \\  / |_   _  | |__   ___ _ __ ___     __ _  __| |_   _____ _ __ | |_ _   _ _ __ ___ 
 | |\\/| | | | | | '_ \\ / _ \\ '__/ _ \\   / _` |/ _` \\ \\ / / _ \\ '_ \\| __| | | | '__/ _ \\
 | |  | | |_| | | | | |  __/ | | (_) | | (_| | (_| |\\ V /  __/ | | | |_| |_| | | |  __/
 |_|  |_|\\__, | |_| |_|\\___|_|  \\___/   \\__,_|\\__,_| \\_/ \\___|_| |_|\\__|\\__,_|_|  \\___|
          __/ |                                                                        
         |___/         
_______________________________________________________________________________________________
""")
    print("\n\t\t\t\t\t\t\t\t\t\tby The-Legolas")

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
    player_hero = Warrior(hero_name, starting_items={
        "basic_sword":1, "improved_sword":1, "venom_fang_dagger":1, 
        "frostbrand_sword":1, "bloodletter_axe":1, "ring_of_corruption":1, 
        "ring_of_iron_will":1, "ring_of_vital_flow":1, "basic_armor":1, "improved_armor":1, "ring_of_vital_flow":1, 
        "ring_of_iron_will":1, "ring_of_corruption":1, "small_healing_potion":1, "medium_healing_potion":2,
        "grand_healing_potion":3, "stamina_tonic":4, "antivenom_vial":5, "second_wind_potion":6, "cooling_salve":7, 
        "coagulant_tonic":8, "battle_elixir":9, "reinforcement_draught":10, "explosive_potion":2,
        "lesser_fortitude_draught":5,
    })
    
    return player_hero


if __name__ == "__main__":
    main()
