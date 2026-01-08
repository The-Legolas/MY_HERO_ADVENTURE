from game.core.character import Character
from game.core.Heroes import Warrior

from game.world.Gen_Game_World import Game_World
from game.systems.enums.town_names import Town_names

from game.engine.game_engine import GameEngine

from game.ui.class_text_screens import TextScreen
from game.ui.save_menu_ui import run_save_load_menu

from game.engine.save_system import load_game


"""
currently __ lines of code as of the previous git commit
Bugs:

Test:


Fixed:


Like to have:
If I ever go back to this project then add: A new dungeon type (a swamp and a crypt maybe); add a wizard character who uses mana and an archer who uses arrows as ressources;
maybe experiment with pygame and actually make some visuals for this game

"""


def main():

    title_screen()

    main_menu()



def main_menu() -> None:
    while True:
        print("\n--- MAIN MENU ---")
        print("1. New Game")
        print("2. Load Game")
        print("3. Tutorial")
        print("4. Exit")


        choice = input("> ").strip().lower()

        if choice in ("1", "new", "new game"):
            start_new_game()
            return

        elif choice in ("2", "load", "load game"):
            start_loaded_game()
            input("\nPress Enter to continue...")

        elif choice in ("3", "tutorial", "guide", "help"):
            show_system_guide()
            input("\nPress Enter to return to the main menu...")

        elif choice in ("4", "exit", "quit"):
            print("\nGoodbye.")
            exit()

        else:
            print("Invalid choice.")

def start_new_game() -> None:
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

def start_loaded_game():
    slot = run_save_load_menu(mode="load")

    if slot is None:
        return

    try:
        player, world = load_game(slot)
    except FileNotFoundError:
        print("Save file not found.")
        input("Press Enter to continue...")
        return

    engine = GameEngine(player=player, game_world=world)

    print(f"\nLoaded save '{slot}'.\n")
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
    input()

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
                "- load\n"
                "- exit"
            ),

            (
                "SHORT COMMANDS:\n\n"
                "Many commands can be shortened:\n"
                "- i → inventory\n"
                "- c → cancel / back\n"
                "- exit → immediately quit the game\n\n"
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
                "☠   Poison       → takes damage over time\n"
                "🔥  Burn         → takes % health damage over time\n"
                "🩸  Bleed        → takes stacked damage over time\n"
                "✚   Regen        → recovers health over time\n"
                "⚔⬇  Weakened     → reduced outgoing damage\n"
                "🛡⬇  Armor Down   → reduced defence\n"
                "⚔⬆  Strength     → increased outgoing damage\n"
                "💫  Stun         → cannot act\n"
                "🛡   Defending    → increased defence"
            ),
            (
                "EXIT COMMAND:\n\n"
                "Typing 'exit' at any time will immediately close the game.\n\n"
                "⚠ This does NOT save your progress.\n"
                "Use this only if you are sure you want to quit."
            ),
        ]
    )
    guide.show()
    print("\n")


def pick_character_and_name() -> Character:
    while True:
        print("\n--- Choose Your Class ---")
        print("1. Warrior")
        print("— Trained for battle and built to endure. High vitality and strong armor make the Warrior difficult to bring down, even in the deepest depths.\n")
        print("2. Archer   (Locked – In development)")
        print("3. Wizard   (Locked – In development)\n")

        choice = input("> ").strip().lower()

        if choice in ("c", "back"):
            continue

        if choice in ("1", "warrior"):
            hero_choice = "warrior"
            break

        elif choice in ("2", "archer"):
            print("\nThe Archer class is not finished yet. Please choose another class.")
            input("Press Enter to continue...")
            continue

        elif choice in ("3", "wizard"):
            print("\nThe Wizard class is not finished yet. Please choose another class.")
            input("Press Enter to continue...")
            continue

        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

    while True:
        hero_name = input("\nAnd what shall be your name?\n> ").strip()

        if not hero_name:
            print("Name cannot be empty.")
            continue

        confirm = input(f"Is '{hero_name}' correct? (y/n)\n> ").strip().lower()
        if confirm in ("y", "yes"):
            break
    

    starting_items={
        "basic_sword":1, "improved_sword":1, "venom_fang_dagger":1, 
        "frostbrand_sword":1, "bloodletter_axe":1, "ring_of_corruption":1, 
        "ring_of_iron_will":1, "ring_of_vital_flow":1, "basic_armor":1, "improved_armor":1, "ring_of_vital_flow":1, 
        "ring_of_iron_will":1, "ring_of_corruption":1, "small_healing_potion":1, "medium_healing_potion":2,
        "grand_healing_potion":3, "stamina_tonic":4, "antivenom_vial":5, "second_wind_potion":6, "cooling_salve":7, 
        "coagulant_tonic":8, "battle_elixir":9, "reinforcement_draught":10, "explosive_potion":2,
        "lesser_fortitude_draught":5,
    }
    if hero_choice == "warrior":
        player_hero = Warrior(hero_name, starting_items=None)

    return player_hero

if __name__ == "__main__":
    main()
