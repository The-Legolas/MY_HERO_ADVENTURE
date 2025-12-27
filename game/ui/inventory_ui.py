from game.core.Character_class import Character
from game.core.Item_class import Items, Item_Type
from game.ui.status_ui import describe_status_compact, sort_statuses_by_priority, inspect_entity_statuses
from game.systems.combat.status_registry import STATUS_REGISTRY

ITEM_TYPE_ORDER = [
    Item_Type.CONSUMABLE,
    Item_Type.WEAPON,
    Item_Type.ARMOR,
    Item_Type.RING,
    Item_Type.SCRAP,
]

def run_inventory_menu(player: Character):
   while True:
        render_player_status(player)

        print("\n--- BACKPACK ---")
        print("1. View equipped items")
        print("2. View inventory")
        print("3. Inspect status")
        print("4. Equip item")
        print("5. Unequip item")
        print("6. Use Item")
        print("7. Back")

        choice = input("> ").strip()

        if choice == "1":
            _show_equipped_items(player)
        elif choice == "2":
            _show_inventory_items(player, equippable_only=False)
        elif choice == "3":
            _inspect_player_statuses(player)
        elif choice == "4":
            _equip_flow(player)
        elif choice == "5":
            _unequip_flow(player)
        elif choice == "6":
            _use_item_flow(player)
        elif choice == "7":
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
        print(f"{idx}. {slot.title()}: {item.name}")


def _show_inventory_items(player: Character, equippable_only: bool):
    items = get_inventory_items(player, equippable_only)
    
    print("\n--- Inventory ---")

    if not items:
        print("Inventory is empty.")
        return []

    current_category = None
    category_counts = {}

    for _, item, count in items:
        category_counts[item.category] = category_counts.get(item.category, 0) + count

    for idx, (_, item, count) in enumerate(items, start=1):
        if item.category != current_category:
            current_category = item.category
            total = category_counts[current_category]
            print(f"\n--- {current_category.value.title()} ({total}) ---")

        print(f"{idx}. {item.name} x{count}")
        tooltip = item.get_tooltip()
        if tooltip:
            print(f"\t{tooltip}\n")

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


def get_inventory_items(player: Character, equippable_only: bool = False) -> list[tuple[str, Items, int]]:

    results = []

    for item_id, entry in player.inventory["items"].items():
        item = entry["item"]
        assert isinstance(item, Items), f"Inventory item for {item_id} is not Items"
        count = entry["count"]

        if equippable_only:
            if item.category not in (Item_Type.WEAPON, Item_Type.ARMOR, Item_Type.RING):
                continue

        results.append((item_id, item, count))
    
     # --- automatic sorting ---
    def sort_key(entry):
        _, item, _ = entry
        type_index = ITEM_TYPE_ORDER.index(item.category)
        name_key = item.name.lower()
        return (type_index, name_key)

    results.sort(key=sort_key)

    return results

def _use_item_flow(player: Character):
    items = get_inventory_items(player, equippable_only=False)

    consumables = [
        (key, item, count)
        for (key, item, count) in items
        if item.category == Item_Type.CONSUMABLE
    ]

    if not consumables:
        print("\nYou have no usable consumables.")
        input("Press Enter to continue...")
        return

    print("\n--- Use Item ---")
    for idx, (_, item, count) in enumerate(consumables, start=1):
        print(f"{idx}. {item.name} x{count}")
        tooltip = item.get_tooltip()
        if tooltip:
            print(f"\t{tooltip}")
        print() #spacing
    print("c. Cancel")

    choice = input("> ").strip().lower()
    if choice in ("c", "cancel", "back"):
        return

    if not choice.isdigit():
        print("Invalid choice.")
        return

    idx = int(choice) - 1
    if idx < 0 or idx >= len(consumables):
        print("Invalid selection.")
        return

    inv_key, item, _ = consumables[idx]

    outcome = item.use(player, player)

    _render_inventory_item_outcome(outcome)


    if outcome and outcome.get("action") == "use_item":
        player.remove_item(inv_key, amount=1)

    input("\nPress Enter to continue...")

def _render_inventory_item_outcome(outcome: dict):
    if not outcome:
        print("Nothing happens.")
        return

    action = outcome.get("action")
    target = outcome.get("target")
    extra = outcome.get("extra", {})

    if action == "use_item":
        item_name = extra.get("item", "item")
        details = extra.get("details", [])

        print(f"\nYou used {item_name}.")

        for d in details:
            effect = d.get("effect")

            if effect == "heal":
                print(f"You recover {d['amount']} HP.")

            elif effect == "damage":
                print(f"It deals {d['amount']} damage.")

            elif effect == "apply_status":
                status = d["status"].replace("_", " ").title()
                if d.get("applied"):
                    print(f"{status} is now applied.")
                else:
                    print(f"{status} has no effect.")

            elif effect == "remove_status":
                status = d["status"].replace("_", " ").title()
                if d.get("success"):
                    print(f"{status} is now cured.")
                else:
                    print(f"No {status} to remove.")

    elif action == "use_item_fail":
        reason = extra.get("reason", "unknown")
        item = extra.get("item", "item")

        if reason == "not_consumable":
            print(f"{item} cannot be used outside of combat.")
        elif reason == "no_effect":
            print(f"{item} has no effect right now.")
        else:
            print("Nothing happens.")
    

    else:
        print("Nothing happens.")

def render_player_status(player: Character):
    print("\n=== PLAYER STATUS ===")
    print(f"HP: {player.hp}/{player.max_hp}")

    if player.statuses:
        print("Active effects:")
        for status in sort_statuses_by_priority(player.statuses):
            print(f" - {describe_status_compact(status)}")
    else:
        print("No active effects.")

def _inspect_player_statuses(player: Character):
    if not player.statuses:
        print("\nNo active statuses.")
        input("\nPress Enter to continue...")
        return
    while True:
        print("\n--- Your Status Effects ---")
        inspect_entity_statuses(player)