from game.core.character import Character
from game.engine.input_parser import parse_shop_input

class ShopUI:
    def __init__(self, player: Character):
        self.player = player

    def run_shop_menu(self, shop_metadata: dict[str, any]):
            inventory = shop_metadata.get("inventory", [])
            buy_mult = shop_metadata.get("buy_multiplier", 1.0)
            sell_mult = shop_metadata.get("sell_multiplier", 0.5)

            while True:
                print("\n\n--- SHOP MENU ---")
                print("Your gold:", self.player.inventory["gold"])
                
                print("\nMenu Options:")
                print("1. Buy Item")
                print("2. Sell item")
                print("3. Exit shop\n")

                choice = parse_shop_input(input("> "))

                if choice == "leave_shop":
                    return

                elif choice == "buy_item":
                    self.handle_buy_item(inventory, buy_mult)
                    
                
                elif choice == "sell_item":
                    self.handle_sell_item(sell_mult)
                    
                
                else:
                    print("Invalid input.")
    




    def handle_buy_item(self, inventory: dict[str, any], buy_mult: float):
        while True:
            print("\n\n--- SHOP MENU ---")
            print("Your gold:", self.player.inventory["gold"])
            print("\nItems for sale:")

            print("\nWhich item do you want to buy?")
            
            visible_items = []
            for record in inventory:
                if record.stock > 0:
                    price = int(record.current_price * buy_mult)
                    visible_items.append(record)
                    print(f"{len(visible_items)}. {record.item.name}  |  Price {price}  |  Stock {record.stock}")

                
            if not visible_items:
                print("\n\tThere is nothing more to buy.")
                input()
                return
            
            if self.player.inventory["gold"] <= 0:
                print("\nYou have no gold.")
                input()
                return
            
            print("\nType number to buy, or 'back' to return.")
            choice = input("> ")

            if choice in  ("leave_shop", "back", "c"):
                return

            if not (choice and choice.isdigit()):
                print("\nInvalid choice. Provide an item number.")
                input()
                continue

            index = int(choice) - 1
            if index < 0 or index >= len(visible_items):
                print("Invalid selection.")
                input()
                continue
            
            record = visible_items[index]            
            price = int(record.current_price * buy_mult)

            print(f"\nHow many {record.item.name} do you want? (max {record.stock})")
            qty_raw = input("> ").strip().lower()

            if qty_raw in ("back", "cancel", "c"):
                continue

            if not qty_raw.isdigit():
                print("Please enter a valid number.")
                input()
                continue

            qty = int(qty_raw)

            if qty <= 0:
                print("Quantity must be at least 1.")
                input()
                continue

            if qty > record.stock:
                print("Not enough stock.")
                input()
                continue

            total_price = price * qty

            print(f"\nConfirm purchase:")
            print(f"{qty} × {record.item.name} × {price} each = {total_price} gold")
            confirm = input("\nBuy these items? (yes/no) > ").strip().lower()

            if confirm not in ("yes", "y"):
                print("\nPurchase cancelled.")
                input()
                continue

            if self.player.inventory["gold"] < total_price:
                print("\nYou cannot afford that.")
                input()
                continue

            self.player.inventory["gold"] -= total_price
            record.stock -= qty
            record.sold_today += qty

            for _ in range(qty):
                self.player.add_item(record.item)

            print(f"\nYou bought {qty} × {record.item.name}!")
            input()
            

    def handle_sell_item(self, sell_mult: float):
        while True:
            print("\n--- SELL MENU ---")
            print("\nYour inventory:")
            player_items = self.player.inventory["items"]

            if not player_items:
                print("You have nothing to sell.")
                input()
                return

            listed = []
            for idx, (item_id, data) in enumerate(player_items.items(), start=1):
                item_obj = data["item"]
                count = data["count"]
                value = int(item_obj.value * sell_mult)
                print(f"{idx}. {item_obj.name} x{count}  |  Sell price: {value} each")
                listed.append((item_id, data))

            print("\nType number to sell, or 'back' to return.")
            choice = input("\n> ").strip().lower()

            if choice in ("leave", "back", "c"):
                return

            if not (choice and choice.isdigit()):
                print("Invalid input. Provide an item number.")
                input()
                continue

            index = int(choice) - 1
            if index < 0 or index >= len(listed):
                print("Invalid selection.")
                input()
                continue

            item_id, data = listed[index]
            item_obj = data["item"]
            player_count = data["count"]
            sell_price = int(item_obj.value * sell_mult)

            print(f"\nHow many '{item_obj.name}' do you want to sell? (max {player_count})")
            qty_raw = input("> ").strip().lower()

            if qty_raw in ("back", "cancel", "c"):
                continue

            if not qty_raw.isdigit():
                print("Please enter a valid number.")
                input()
                continue

            qty = int(qty_raw)

            if qty <= 0:
                print("Quantity must be at least 1.")
                input()
                continue
            
            if qty > player_count:
                print("You don't have that many.")
                input()
                continue

            total_gold = sell_price * qty

            print(f"\nConfirm sale:")
            print(f"{qty} × {item_obj.name} × {sell_price} each = {total_gold} gold")
            confirm = input("\nSell these items? (yes/no) > ").strip().lower()

            if confirm not in ("yes", "y"):
                print("\nSale cancelled.")
                continue

            for _ in range(qty):
                self.player.remove_item(item_id)

            self.player.inventory["gold"] += total_gold

            print(f"\nYou sold {qty} × {item_obj.name} for {total_gold} gold!")
            input()

        