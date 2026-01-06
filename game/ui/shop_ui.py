from game.core.character import Character
import math
from game.engine.input_parser import parse_shop_input
from game.ui.inventory_ui import ITEM_TYPE_ORDER, get_inventory_items

ITEMS_PER_PAGE = 10

class ShopUI:
    def __init__(self, player: Character):
        self.player = player

    def run_shop_menu(self, shop_metadata: dict[str, any]) -> None:
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
    


    def handle_buy_item(self, inventory: dict[str, any], buy_mult: float) -> None:
        page = 0

        while True:
            visible_items = []
            for record in inventory:
                if record.stock <= 0:
                    continue
                price = int(record.current_price * buy_mult)
                visible_items.append(record)
                #print(f"{len(visible_items)}. {record.item.name}  |  Price {price}  |  Stock {record.stock}")

            total_pages = max(1, math.ceil(len(visible_items) / ITEMS_PER_PAGE))
            page = max(0, min(page, total_pages - 1))

            start = page * ITEMS_PER_PAGE
            end = start + ITEMS_PER_PAGE
            page_items = visible_items[start:end]

            name_width = max(len(r.item.name) for r in page_items)
            name_width += 2
            price_width = max(len(str(int(r.current_price * buy_mult))) for r in page_items)
            stock_width = max(len(str(r.stock)) for r in page_items)
            
            print("\n--- SHOP MENU ---")
            print(f"Gold: {self.player.inventory['gold']}\n")

            print(
                f"{'#':>2}  "
                f"{'Item Name'.ljust(name_width)} | "
                f"{'Price'.rjust(price_width)} | "
                f"{'Stock'.rjust(stock_width)}"
            )
            print("-" * (6 + name_width + price_width + stock_width + 6))

            for i, record in enumerate(page_items, start=1):
                price = int(record.current_price * buy_mult)
                print(
                    f"{i:>2}  "
                    f"{record.item.name.ljust(name_width)} | "
                    f"{str(price).rjust(price_width)} | "
                    f"{str(record.stock).rjust(stock_width)}"
                )
            print(f"\nPage {page + 1} / {total_pages}")
            print("Type number to buy, [n]ext, [p]revious, or [back]")
            choice = input("> ").strip().lower()

            if choice in ("back", "c"):
                return

            if choice == "n":
                page = (page + 1) % total_pages
                continue

            if choice == "p":
                page = (page - 1) % total_pages
                continue

            if not choice.isdigit():
                print("Invalid input.")
                input()
                continue

            index = int(choice) - 1
            if index < 0 or index >= len(page_items):
                print("Invalid selection.")
                input()
                continue

            record = page_items[index]
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


    def handle_sell_item(self, sell_mult: float) -> None:
        player = self.player

        while True:
        # ─── REBUILD INVENTORY EACH LOOP ───────────────────
            items = get_inventory_items(player, equippable_only=False)

            if not items:
                print("\nYou have nothing to sell.")
                input()
                return

            # Group by category
            grouped = {}
            for item_id, item, count in items:
                grouped.setdefault(item.category, []).append((item_id, item, count))

            grouped = {k: v for k, v in grouped.items() if v}
            categories = [cat for cat in ITEM_TYPE_ORDER if cat in grouped]

            # ─── CATEGORY SELECTION ────────────────────────────
            print("\n--- SELL MENU ---")
            print(f"Gold: {player.inventory['gold']}\n")
            print("--- Inventory Categories ---")

            for idx, cat in enumerate(categories, start=1):
                total = sum(count for _, _, count in grouped[cat])
                print(f"{idx}. {cat.value.title()} ({total})")

            print("c. Back")
            choice = input("> ").strip().lower()

            if choice in ("c", "back"):
                return

            if not choice.isdigit():
                print("Invalid input.")
                input()
                continue

            cat_index = int(choice) - 1
            if cat_index < 0 or cat_index >= len(categories):
                print("Invalid selection.")
                input()
                continue

            category = categories[cat_index]
            entries = grouped[category]

            # ─── PAGINATED ITEM LIST ───────────────────────────
            page = 0
            total_pages = max(1, math.ceil(len(entries) / ITEMS_PER_PAGE))

            sold_something = False

            while True:
                start = page * ITEMS_PER_PAGE
                end = start + ITEMS_PER_PAGE
                page_items = entries[start:end]

                name_width = max(len(item.name) for _, item, _ in page_items)
                qty_width = max(len(str(count)) for _, _, count in page_items)
                price_width = max(
                    len(str(int(item.value * sell_mult)))
                    for _, item, _ in page_items
                )

                print(f"\n--- {category.value.title()} (Page {page + 1}/{total_pages}) ---")
                print(
                    f"{'#':>2}  "
                    f"{'Item Name'.ljust(name_width)} | "
                    f"{'Qty'.rjust(qty_width)} | "
                    f"{'Price'.rjust(price_width)}"
                )
                print("-" * (8 + name_width + qty_width + price_width))

                for idx, (item_id, item, count) in enumerate(page_items, start=1):
                    price = int(item.value * sell_mult)
                    print(
                        f"{idx:>2}  "
                        f"{item.name.ljust(name_width)} | "
                        f"{str(count).rjust(qty_width)} | "
                        f"{str(price).rjust(price_width)}"
                    )

                print("\n[n]ext  [p]rev  [back]")
                choice = input("> ").strip().lower()

                # Navigation
                if choice in ("back", "c"):
                    break

                if choice == "n":
                    page = (page + 1) % total_pages
                    continue

                if choice == "p":
                    page = (page - 1) % total_pages
                    continue

                if not choice.isdigit():
                    print("Invalid input.")
                    input()
                    continue

                index = int(choice) - 1
                if index < 0 or index >= len(page_items):
                    print("Invalid selection.")
                    input()
                    continue

                # ─── SELL FLOW ──────────────────────────────────
                item_id, item, owned = page_items[index]
                price = int(item.value * sell_mult)

                print(f"\nHow many {item.name} do you want to sell? (max {owned})")
                qty_raw = input("> ").strip().lower()

                if qty_raw in ("c", "back", "cancel"):
                    continue

                if not qty_raw.isdigit():
                    print("Invalid number.")
                    input()
                    continue

                qty = int(qty_raw)
                if qty <= 0 or qty > owned:
                    print("Invalid quantity.")
                    input()
                    continue

                total_gold = qty * price

                print(f"\nConfirm sale:")
                print(f"{qty} × {item.name} × {price} = {total_gold} gold")
                confirm = input("Confirm? (y/n) > ").strip().lower()

                if confirm not in ("y", "yes"):
                    print("Sale cancelled.")
                    input()
                    continue

                # Apply sale
                player.remove_item(item_id, amount=qty)
                player.inventory["gold"] += total_gold

                print(f"\nSold {qty} × {item.name} for {total_gold} gold.")
                input()

                sold_something = True
                break  # exit pagination

            if sold_something:
                continue  # back to category selection