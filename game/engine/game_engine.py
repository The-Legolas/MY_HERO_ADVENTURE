from game.core.Character_class import Character
from game.world.Gen_Game_World import Game_World
from game.world.town_logic.town_names import Town_names
from game.engine.input_parser import parse_interior_input, parse_leave_town_input, parse_town_gate_input, inventory_input_parser, parse_shop_input
from game.world.town_logic.town_creation import Location, Town_Actions, TownGraph
from game.core.Item_class import spawn_item
from game.ui.shop_ui import ShopUI
from game.ui.tavern_ui import TavernUI
from game.ui.inn_ui import InnUI
from game.ui.inventory_ui import run_inventory_menu
from enum import Enum

class Command_Context(Enum):
    TOWN_GATE = "town_gate"
    INTERIOR = "interior"
    SHOP = "shop"
    LEAVE_TOWN = "leave_town"
    DUNGEON = "dungeon"
    COMBAT = "combat"



class GameEngine:
    def __init__(self, player: Character, game_world: Game_World):
        self.player = player
        self.world = game_world
        self.state = "town"

        self.current_dungeon = None
        self.current_room = None

        self.shop_ui = ShopUI(self.player)
        self.tavern_ui = TavernUI(self.player)
        self.inn_ui = InnUI(self.player, self.world)

    def get_player_command(self, raw_input: str, context: str) -> str | None:
        cmd = inventory_input_parser(raw_input)
        if cmd:
            return cmd
        
        if raw_input == "debug":
            return "debug_menu"

        if context == Command_Context.SHOP.value:
            return parse_shop_input(raw_input)
        
        if context == Command_Context.INTERIOR.value:
            return parse_interior_input(raw_input)

        if context == Command_Context.TOWN_GATE.value:
            return parse_town_gate_input(raw_input)

        if context == Command_Context.LEAVE_TOWN.value:
            return parse_leave_town_input(raw_input)

        """ if context == Command_Context.DUNGEON.value:
            return parse_dungeon_input(raw_input)

        if context == Command_Context.COMBAT.value:
            return parse_combat_input(raw_input)
"""
        return None


    def run(self):
        while True:
            if self.state == "town":
                self.run_town_mode()
            elif self.state == "dungeon":
                self.run_dungeon_mode()
            elif self.state == "combat":
                self.run_combat_mode()


    def run_town_mode(self) -> None:
        game_town = self.world.get_town()

        while self.state == "town":
            location = game_town.current_location()
            self.show_town_menu(location)

            raw_input = input("> ")

            context = self._town_input_context(location)

            command = self.get_player_command(raw_input, context)

            if command == "open_inventory":
                run_inventory_menu(self.player)
                continue

            if command == "debug_menu":
                self.run_debug_menu()
                continue

            if command is None:
                print("I don't understand that. Try again.")
                continue
            
            if context == "shop":
                if command in ("buy_item", "sell_item", "leave_shop"):
                    shop_metadata = location.extra_metadata
                    self.shop_ui.handle_command(command, shop_metadata)
                    continue

            action = self.cmd_to_action(command, location)
            if action == None:
                print("That action is not available here.")
                continue
            
            result = game_town.perform_action(action)
            if not result.get("success", False):
                print(result.get("reason", "Action failed."))
                continue

            self.handle_town_action(result, game_town)
    
    def _town_input_context(self, location: Location) -> str:
        if location.name == Town_names.TOWN_GATE.value:
            return "town_gate"

        if location.is_interior():
            return "interior"

        return "unknown"

   

    def show_town_menu(self, location: Location) -> None:
        name = location.name

        if name == Town_names.TOWN_GATE.value:
            print("\n\nYou are at the Town Gate.")
            print("1. Enter Shop")
            print("2. Enter Inn")
            print("3. Enter Tavern")
            print("4. Leave Town")
            return

        print(f"\n\nYou are inside the {name}.")
        print("1. Talk")
        if name == Town_names.SHOP_INTERIOR.value:
            print("2. Menu (Buy/Sell)")
        elif name == Town_names.INN_INTERIOR.value:
            print("2. Rest")
        elif name == Town_names.TAVERN_INTERIOR.value:
            print("2. Buy Beer")
        print("3. Leave Building")
        

    def get_town_input(self, location: Location) -> str | None:
        raw = input("> ")
        if raw.strip().lower() == "debug":
            return "debug_menu"

        if location.name == Town_names.TOWN_GATE.value:
            return parse_town_gate_input(raw)

        if location.is_interior():
            # BUT: detect shop UI separately
            return parse_interior_input(raw)

        return None
        

    def cmd_to_action(self, cmd: str, location: Location) -> Town_Actions | None:
        name = location.name

        # Town Gate mapping
        if name == Town_names.TOWN_GATE.value:
            if cmd == "enter_shop":
                return Town_Actions.ENTER_SHOP
            if cmd == "enter_inn":
                return Town_Actions.ENTER_INN
            if cmd == "enter_tavern":
                return Town_Actions.ENTER_TAVERN
            if cmd == "leave_town":
                return Town_Actions.LEAVE_TOWN
            
        # Inside buildings
        if location.is_interior():
            if cmd == "talk":
                return Town_Actions.TALK

            if cmd == "menu":
                if name == Town_names.INN_INTERIOR.value:
                    return Town_Actions.REST

                if name == Town_names.SHOP_INTERIOR.value:
                    return Town_Actions.BUY_FROM_SHOP

                if name == Town_names.TAVERN_INTERIOR.value:
                    return Town_Actions.BUY_BEER
            
            if cmd == "leave_building":
                return Town_Actions.LEAVE_BUILDING

        # Leave Town submenu
        if cmd == "enter_cave":
            return Town_Actions.ENTER_CAVE

        if cmd == "enter_castle":
            return Town_Actions.ENTER_CASTLE

        return None
    

    def handle_town_action(self, result: dict, town: TownGraph) -> None:
        t_action = result["type"]

        # leave_building: result should contain destination (e.g., Town Gate)
        if t_action == "leave_building":
            town.move_location(result["destination"])
            return

        if t_action == "enter_shop":
            town.move_location(result["destination"])
            return

        if t_action == "enter_tavern":
            metadata = town.current_location().extra_metadata
            self.tavern_ui.run_tavern_menu(metadata)
            return

        if t_action == "enter_inn":
            metadata = town.current_location().extra_metadata
            self.inn_ui.run_inn_menu(metadata)
            return
                
        # Talk
        if t_action == "talk":
            print(result.get("dialogue", "\nYou have a pleasant chat."))
            input()
            return
        
        # Shop menus: result should provide 'location_metadata' or similar
        if t_action in ("buy_menu", "sell_menu"):
            shop_metadata = town.current_location().extra_metadata
            self.shop_ui.run_shop_menu(shop_metadata)
            return

        
        # Enter cave/castle transitions: set dungeon and flip state
        if t_action == "enter_cave":
            self.current_dungeon = self.world.get_cave()
            self.state = "dungeon"
            print("\nYou enter the cave.")
            return
        
        if t_action == "enter_castle":
            self.current_dungeon = self.world.get_castle()
            self.state = "dungeon"
            print("\nYou enter the castle.")
            return

        # Leave town - show submenu
        if t_action == "leave_town":
            self.show_leave_town_submenu()
            return

    
    def show_leave_town_submenu(self):
        while True:
            print("\n--- Leave Town ---")
            print("1. Go back")
            print("2. Enter cave")
            print("3. Enter castle")
            
            choice = input("\nWhere do you go? ")
            cmd = parse_leave_town_input(choice)

            if cmd == "go_back":
                return
            
            if cmd == "enter_cave":
                self.current_dungeon = self.world.get_cave()
                self.state = "dungeon"
                return
            if cmd == "enter_castle":
                if not self.world.castle_unlocked:
                    print("\nThe castle is locked.")
                    continue
                self.current_dungeon = self.world.get_castle()
                self.state = "dungeon"
                return

            print("\nInvalid choice. Type 'back' to cancel.")


    def run_debug_menu(self):
        while True:
            print("\n=== DEBUG MENU ===")
            print("1. Add Gold")
            print("2. Add Item")
            print("3. Exit Debug Menu")

            choice = input("> ").strip()

            if choice == "1":
                amount = input("\nHow much gold to add? ")
                if amount.isdigit():
                    self.player.inventory["gold"] += int(amount)
                    print(f"\nAdded {amount} gold.")
                else:
                    print("\nInvalid amount.")

            elif choice == "2":
                item_id = input("\nEnter item ID to give player: ").strip()
                try:
                    item_obj = spawn_item(item_id)
                    self.player.add_item(item_obj)
                    print(f"\nGave player: {item_obj.name}")
                except:
                    print("\nInvalid item ID.")

            elif choice == "3":
                print("\nExiting debug menu.")
                return

            else:
                print("\nInvalid choice.")

