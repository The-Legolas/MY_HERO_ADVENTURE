from game.core.Character_class import Character
from game.core.Heroes import Warrior
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.game_engine import GameEngine
# Missing from the game still:

# Exploration System:  | Safe areas ( rest rooms, save points)  | 

# Progression & Balance:  |  Resource scarcity tuning (HP, MP, items)  | Grind tolerance (optional but intentional)

# Saving & Persistence:  |  Save system / load system



#later
# Story Framework:   | Intro / setup  | World premise  |  Player motivation  |  Ending(s)

# Worldbuilding: |  Enemy flavor text  | Lore snippets/Environmental storytelling

# NPCs:  | Quest-givers or guides  |  NPCs with conditional dialogue

# Advanced Combat:  | Elemental weaknesses/resistances  |  Multi-target attacks   |  Skill cooldowns or costs



# Testing


"""
Bugs:



Like to have:
note 1: Statuses should have a chance to apply even if the attack is blocked. (or makeing it so if defence is more than the attack (and not defending) only doing halve dmg)
note 2: add burn to flame_breath skill, add bleed to rending_bite, add armor_down (weakening for defence) to acid_splash
note 3: add Skill priority overrides per enemy type, Multi-enemy coordination behaviors
note 4: in the code base search for #fix to find things to remove before final game release
note 5: Add dynamic merchant dialogue (based on demand, discounts, etc.)
note 6: update shop and tressure inventory to hold some of the new items
# Items & Equipment:  done but maybe the supposed map mechanic

"""


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
    player_hero = Warrior(hero_name, starting_items={
        "grand_healing_potion": 1,
        "medium_healing_potion": 1,
        "explosive_potion": 1,
        "elixir_of_battle_focus": 1,
        "lesser_fortitude_draught": 1,
        "antivenom_vial": 1,
        "volatile_concoction": 1,
        "sluggish_brew": 1,
        "poison_flask": 1,
        "strength_elixir": 1,
        "regeneration_draught": 1,
    })
    
    return player_hero





if __name__ == "__main__":
    main()
