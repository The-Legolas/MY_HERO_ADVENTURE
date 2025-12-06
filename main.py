from game.core.Character_class import Character
from game.core.Heroes import Warrior
from game.world.dungeon_manager import Dungeon_Manager
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names


def main():

    print("  ________________________________")
    print("\tHello and welcome to\n")
    print("\tMy hero adventure")
    print("  ________________________________\n")
    while True:
        print("\nPlease pick your character from amoung these options")
        hero_choice = input("(Warrior, Archer, or Wizard): ").strip().lower()

        if hero_choice in ("warrior", "archer", "wizard"):
            break

        print("please try again.")

    hero_name = input("\nAnd what shall be your name?\n: ")

    if hero_choice == "warrior":
        player_hero = Warrior(hero_name)
    
    game_world = Game_World(player_hero, day_counter=1)
    
    game_town = game_world.get_town()

    game_town.set_starting_location(Town_names.TOWN_GATE.value)

    print("let's play")




    

if __name__ == "__main__":
    main()