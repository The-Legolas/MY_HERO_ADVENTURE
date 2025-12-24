from game.core.Character_class import Character
from game.core.Heroes import Warrior
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.game_engine import GameEngine
# Missing from the game still:

# Exploration System:  | Safe areas ( rest rooms, save points)  | 
# Map logic (implicit, discovered, or explicit)      currently using a debug tool to render the map but should expand into an actual part of the game  |
# Dungeon progression logic (keys, switches, boss gates)

# Character System:  | Level-up system

# Enemies:  |  Boss-specific mechanics or behaviors  | Enemy intent |  Status immunities / resist tiers  |  Boss-only overrides

# Items & Equipment:  |  Item use out of combat:  like the supposed map mechanic

# Progression & Balance:  |  Resource scarcity tuning (HP, MP, items)  | Grind tolerance (optional but intentional)

# Saving & Persistence:  |  Save system / load system



#later
# Story Framework:   | Intro / setup  | World premise  |  Player motivation  |  Ending(s)

# Worldbuilding: |  Enemy flavor text  | Lore snippets/Environmental storytelling

# NPCs:  | Quest-givers or guides  |  NPCs with conditional dialogue

# Advanced Combat:  | Elemental weaknesses/resistances  |  Multi-target attacks   |  Skill cooldowns or costs

# Class & Build Depth:  |  Skill trees  |  Class-specific equipment

# Quests & Side Content:  | Side quests  |  Optional bosses  |  Rare items

# Meta Systems:  | Bestiary / enemy log   |  Statistics tracking (deaths, clears, etc.)

# Testing


"""
note 1: fleeing is succesful no matter what is displayed to the user.
note 2: Statuses should have a chance to apply even if the attack is blocked. (or makeing it so if defence is more than the attack (and not defending) only doing halve dmg)
note 3: Make it so more than 1 enemy can spawn at a time.
note 4: add burn to flame_breath skill, add bleed to rending_bite, add armor_down (weakening for defence) to acid_splash
note 5: add Skill priority overrides per enemy type, Multi-enemy coordination behaviors
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
    player_hero = Warrior(hero_name)
    
    return player_hero

    





if __name__ == "__main__":
    main()