from game.core.Character_class import Character
from game.core.Heroes import Warrior
from game.world.dungeon_manager import Dungeon_Manager
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.input_parser import normalize_input
from game.world.town_logic.town_creation import Location, Town_Actions
from game.world.town_logic.town_shop_system import initialize_shop_inventory


def main():

    title_screen()

    player_hero = pick_character_and_name()
    
    game_world = Game_World(player_hero, day_counter=1)
    game_town = game_world.get_town()
    game_town.set_starting_location(Town_names.TOWN_GATE.value)

    print("let's play")

def title_screen() -> None:
    print("  _________________________________")
    print("\tHello and welcome to:")
    print("\tMy hero adventure")
    print("\n\t\t    by The-Legolas")
    print("  _________________________________\n")

def pick_character_and_name() -> Character:
    while True:
        print("\nPlease pick your character from amoung these options")
        hero_choice = input("(Warrior, Archer, or Wizard): ").strip().lower()

        if hero_choice in ("warrior", "archer", "wizard"):
            break

        print("please try again.")
    
    while True:
        hero_name = input("\nAnd what shall be your name?\n: ")
        yes_no = input(f"Is '{hero_name}' correct? (Yes or No)\n: ").strip().lower()

        if yes_no == "yes" or yes_no == "y":
            break

    if hero_choice: #hero_choice == "warrior":
        player_hero = Warrior(hero_name)
    
    return player_hero

    
class GameEngine:
    def __init__(self, player: Character, game_world: Game_World):
        self.player = player
        self.world = game_world
        self.state = "town"

    def run(self):
        while True:
            if self.state == "town":
                self.run_town_mode()
            elif self.state == "dungeon":
                self.run_dungeon_mode()
            elif self.state == "combat":
                self.run_combat_mode()

    def run_town_mode(self, game_world: Game_World):
        game_town = game_world.get_town()

        while self.state == "town":
            self.player_current_loca = game_town.current_location()

            self.show_town_menu(self.player_current_loca)

            player_input = self.get_town_input()
            normal_input = normalize_input(player_input)
            action = self.cmd_to_action(normal_input, self.player_current_loca)

            if action == None:
                print("This action is now avalible.")
                continue
            action_result = game_town.perform_action(action)
   

    def show_town_menu(self, location: Location) -> None:
        name = location.name

        if name == Town_names.TOWN_GATE.value:
            print("1. Enter Shop")
            print("2. Enter Inn")
            print("3. Enter Tavern")
            print("4. Leave Town")

        elif "Exterior" in name:
            print("1. Enter Building")
            print("2. Talk")
            print("3. Return to Town Gate")

        else:  # interior
            print("1. Talk")
            print("2. Perform Action (rest/buy/etc)")
            print("3. Leave Building")
        

    def get_town_input(self):
        choice = input("> ")
        command_string = normalize_input(choice)
        return command_string
    

    def cmd_to_action(self, cmd: str, location: Location):
        if location.name == Town_names.TOWN_GATE.value:
            if cmd == "enter_shop":
                return Town_Actions.ENTER_BUILDING
            if cmd == "enter_inn":
                return Town_Actions.ENTER_BUILDING
            if cmd == "enter_tavern":
                return Town_Actions.ENTER_BUILDING
            if cmd == "leave_town":
                return Town_Actions.LEAVE_TOWN
            
        # Inside buildings
        if cmd == "leave_building":
            return Town_Actions.LEAVE_BUILDING

        if cmd == "talk":
            return Town_Actions.TALK

        # Leave Town submenu
        if cmd == "enter_cave":
            return Town_Actions.ENTER_CAVE

        if cmd == "enter_castle":
            return Town_Actions.ENTER_CASTLE

        return None
    

    def handle_town_action(self, result: dict):
        if result["type"] == "move_interior":
            self.world.get_town().move_location(result["destination"])
        if result["type"] ==  "leave_building":
            self.world.get_town().move_location(result["destination"])
        if result["type"] == "rest":
            self.world.player.hp = self.world.player.max_hp
            self.world.player.inventory["gold"] -= result["cost"]
            self.world.on_day_advance()
        if result["type"] == "talk":
            print("no")
        if result["type"] =="buy_menu" | result["type"] == "sell_menu":
            initialize_shop_inventory(result["inventory"])
        if result["type"] == "enter_cave":
            self.state = "dungeon"
            self.world.get_cave()
        if result["type"] == "enter_castle":
            self.state = "dungeon"
            self.world.get_castle()
        if result["type"] == "leave_town":
            self.show_leave_town_submenu()

    
    def show_leave_town_submenu(self):
        print("\n--- Leave Town ---")
        print("1. Go back")
        print("2. Enter cave")
        print("3. Enter castle")
        
        choice = input("\nWhere do you go? ")
        cmd = normalize_input(choice)

        if cmd == "go_back":
            return
        
        if cmd == "enter_cave":
            self.state = "dungeon"
            self.world.get_cave()
            return
        
        if cmd == "enter_castle":
            self.state = "dungeon"
            self.world.get_castle()
            return       
        
        print("Invalid choice.")


if __name__ == "__main__":
    main()