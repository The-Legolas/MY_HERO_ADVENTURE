from game.core.Character_class import Character
from game.world.town_logic.guide_logic import get_guide_display_name, get_guide_dialogue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine.game_engine import GameEngine

class TavernUI:
    def __init__(self, player: Character, engine: 'GameEngine'):
        self.player = player
        self.engine = engine

    def run_tavern_menu(self, metadata: dict):
        beer_price = metadata.get("beer_price", 15)

        while True:
            guide_name = get_guide_display_name(self.engine.world)

            print("\n--- TAVERN ---")
            print(f"Gold: {self.player.inventory['gold']}")
            print("1. Buy Beer")
            print("2. Talk to Tavern Keeper")
            print(f"3. Talk to {guide_name}")
            print("4. Leave Tavern\n")

            choice = input("> ").strip().lower()

            if choice in ("1", "buy", "buy beer"):
                self.buy_beer(beer_price)

            elif choice in ("2", "talk", "keeper"):
                self.talk_keeper()

            elif choice in ("3", "figure", "guide"):
                self.talk_guide()

            elif choice in ("4", "leave", "exit"):
                return

            else:
                print("Invalid input.")

    def buy_beer(self, price: int):
        if self.player.inventory["gold"] < price:
            print("\nYou cannot afford a beer.")
            input()
            return

        confirm = input(f"\nBuy beer cost {price}? (yes/no) > ").strip().lower()
        if confirm not in ("yes", "y"):
            print("\nPurchase cancelled.")
            input()
            return

        self.player.inventory["gold"] -= price
        print("\nYou enjoy a cold beer. Cheers!")
        input()
        return

    def talk_keeper(self):
        print("\nThe tavern keeper grunts: 'Not many adventurers make it this far…'")
        input()
    
    def talk_guide(self):
        text = get_guide_dialogue(self.engine)
        print(f"\n{text}")
        input()
