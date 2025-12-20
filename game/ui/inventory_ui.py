from game.core.Character_class import Character
from game.core.Item_class import Items, Item_Type, ITEM_DEFINITIONS



def run_inventory_menu(player: Character):
   while True:
        print("\n--- BACKPACK ---")
        print("1. View equipped items")
        print("2. View inventory")
        print("3. Equip item")
        print("4. Unequip item")
        print("5. Back")

        choice = input("> ").strip()

        if choice == "1":
            _show_equipped_items(player)
        elif choice == "2":
            _show_inventory_items(player, equippable_only=False)
        elif choice == "3":
            _equip_flow(player)
        elif choice == "4":
            _unequip_flow(player)
        elif choice == "5":
            return
        else:
            print("Invalid option.")


def _show_equipped_items(player: Character) -> None:

    equipped = get_equipped_items(player)

    print("\n--- Equipped Items ---")
    if not equipped:
        print("Nothing equipped.")
        return
    
    for idx, (slot, item) in enumerate(equipped, start=1):
        stats = ""
        if item.stats:
            stats = " | ".join(
                f"{k.title()}: {v}" for k, v in item.stats.items()
                )

        print(f"{idx}. {slot.title()}: {item.name}  {stats}")



def _show_inventory_items(player: Character, equippable_only: bool) -> list[tuple[str, Items, int]]:
    
    items = get_inventory_items(player, equippable_only)
    print("\n--- Inventory ---")

    if not items:
        print("Inventory is empty.")
        return []


    for idx, (_, item, count) in enumerate(items, start=1):
            stats = ""
            if item.stats:
                stats = " | ".join(
                    f"{k.title()}: {v}" for k, v in item.stats.items()
                )

            print(f"{idx}. {item.name} x{count}  ({item.category.value})  {stats}")
            print(f"\t{item.get_tooltip()}")
    

    return items


def _equip_flow(player: Character) -> None:
    items = _show_inventory_items(player, equippable_only=True)

    if not items:
        return

    while True:
        choice = input("\nEquip which item? (number or 'back'): ").strip()

        if choice.lower() in ("back", "c"):
            return

        if not choice.isdigit():
            print("Invalid input.")
            continue

        index = int(choice) - 1
        if index < 0 or index >= len(items):
            print("Invalid selection.")
            continue

        _, item, _ = items[index]
        player.equip_item(item)
        return


def _unequip_flow(player: Character) -> None:
    equipped = get_equipped_items(player)

    print("\n--- Unequip ---")

    if not equipped:
        print("Nothing to unequip.")
        return

    for idx, (slot, item) in enumerate(equipped, start=1):
        print(f"{idx}. {slot.title()}: {item.name}")

    while True:
        choice = input("\nUnequip which item? (number or 'back'): ").strip()

        if choice.lower() in ("back", "c"):
            return

        if not choice.isdigit():
            print("Invalid input.")
            continue

        index = int(choice) - 1
        if index < 0 or index >= len(equipped):
            print("Invalid selection.")
            continue

        _, item = equipped[index]
        player.unequip_item(item)
        return


def get_equipped_items(player: Character) -> list[tuple[str, Items]]:
    equipped = []

    for slot, item in player.equipment.items():
        if item is not None:
            equipped.append((slot, item))

    return equipped


def get_inventory_items(
        player: Character, equippable_only: bool = False
        ) -> list[tuple[str, Items, int]]:

    results = []

    for item_id, entry in player.inventory["items"].items():
        item = entry["item"]
        count = entry["count"]

        if equippable_only:
            if item.category not in (Item_Type.WEAPON, Item_Type.ARMOR, Item_Type.RING):
                continue

        results.append((item_id, item, count))

    return results
