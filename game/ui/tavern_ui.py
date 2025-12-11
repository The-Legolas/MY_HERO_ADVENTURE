from game.core.Character_class import Character

class TavernUI:
    def __init__(self, player: Character):
        self.player = player

    def run_tavern_menu(self, metadata: dict):
        beer_price = metadata.get("beer_price", 15)

        while True:
            print("\n--- TAVERN ---")
            print(f"Gold: {self.player.inventory['gold']}")
            print("1. Buy Beer")
            print("2. Talk")
            print("3. Leave Tavern\n")

            choice = input("> ").strip().lower()

            if choice in ("1", "buy", "buy beer"):
                self.buy_beer(beer_price)

            elif choice in ("2", "talk", "speak"):
                self.talk()

            elif choice in ("3", "leave", "exit"):
                return

            else:
                print("Invalid input.")

    def buy_beer(self, price: int):
        if self.player.inventory["gold"] < price:
            print("\nYou cannot afford a beer.")
            input()
            return
        while True:
            confirm = input(f"\nBuy beer cost {price}? (yes/no) > ").strip().lower()
            if confirm not in ("yes", "y"):
                print("\nPurchase cancelled.")
                input()
                return

            self.player.inventory["gold"] -= price
            print("\nYou enjoy a cold beer. Cheers!")
            input()
            return

    def talk(self):
        # Placeholder — you can expand this later
        print("\nThe tavern keeper grunts: 'Not many adventurers make it this far…'")
        input()
