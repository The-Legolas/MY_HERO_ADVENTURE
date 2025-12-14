from game.core.Character_class import Character
from game.core.Heroes import Warrior
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.game_engine import GameEngine
# did about 2 hour

def main():

    title_screen()

    player_hero = pick_character_and_name()
    
    game_world = Game_World(player_hero, day_counter=1)
    game_town = game_world.get_town()
    game_town.set_starting_location(Town_names.TOWN_GATE.value)

    engine = GameEngine(player=player_hero, game_world=game_world)

    print("let's play\n")

    engine.run()




def title_screen() -> None:
    print("  _________________________________")
    print("\tHello and welcome to:")
    print("\tMy hero adventure")
    print("\n\t\t    by The-Legolas")
    print("  _________________________________\n")

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
    player_hero = Warrior(hero_name)
    
    return player_hero

    


        


if __name__ == "__main__":
    main()