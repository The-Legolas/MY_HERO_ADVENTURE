from game.core.character import Character
from game.core.Item_class import Items

from game.systems.enums.item_type import Item_Type

from game.definitions.class_progression import CLASS_PROGRESSION
from game.definitions.item_type_order import ITEM_TYPE_ORDER

from game.ui.status_ui import describe_status_compact, sort_statuses_by_priority, inspect_entity_statuses


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

        if not choice.isdigit() or choice == "7":
            return

        if choice == "1":
            _show_equipped_items(player)
        elif choice == "2":
            _inventory_category_menu(player, mode="view")
        elif choice == "3":
            _inspect_player_statuses(player)
        elif choice == "4":
            _equip_flow(player)
        elif choice == "5":
            _unequip_flow(player)
        elif choice == "6":
            _use_item_flow(player)
        else:
            print("Invalid option.")


def _show_equipped_items(player: Character) -> None:

    equipped = get_equipped_items(player)

    print("\n--- Equipped Items ---")
    if not equipped:
        print("Nothing equipped.")
        input()
        return
    
    for idx, (slot, item) in enumerate(equipped, start=1):
        print(f"{idx}. {slot.title()}: {item.name}")
    input()


def _equip_flow(player: Character) -> None:
    items = get_inventory_items(player, equippable_only=True)

    if not items:
        print("\nYou have no equippable items.")
        input("Press Enter to continue...")
        return

    grouped = group_inventory_by_category(items)
    categories = [c for c in ITEM_TYPE_ORDER if c in grouped]

    while True:
        print("\n--- Equip Item ---")
        for i, cat in enumerate(categories, start=1):
            total = sum(count for _, _, count in grouped[cat])
            print(f"{i}. {cat.value.title()} ({total})")
        print("c. Back")

        choice = input("> ").strip().lower()
        if choice in ("c", "back"):
            return

        if not choice.isdigit():
            print("Invalid input.")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(categories):
            print("Invalid selection.")
            continue

        category = categories[idx]
        result = _paginated_equip_view(player, grouped[category])
        if result:
            player.equip_item(result)
            return


def _unequip_flow(player: Character) -> None:
    equipped = get_equipped_items(player)

    if not equipped:
        print("\nNothing to unequip.")
        input("Press Enter to continue...")
        return

    ITEMS_PER_PAGE = 6
    page = 0

    while True:
        total_pages = max(1, (len(equipped) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = max(0, min(page, total_pages - 1))

        start = page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = equipped[start:end]

        print(f"\n--- Unequip Item (Page {page + 1}/{total_pages}) ---")

        for idx, (slot, item) in enumerate(page_items, start=1):
            print(f"{idx}. {slot.title()}: {item.name}")

        print("\n[n]ext  [p]rev  [back]")
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
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(page_items):
            print("Invalid selection.")
            continue

        _, item = page_items[idx]
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
    
    def sort_key(entry):
        _, item, _ = entry
        type_index = ITEM_TYPE_ORDER.index(item.category)
        name_key = item.name.lower()
        return (type_index, name_key)

    results.sort(key=sort_key)

    return results



def _use_item_flow(player: Character):
    result = _inventory_category_menu(player, mode="use")
    if not result:
        return

    inv_key, item = result

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

def group_inventory_by_category(items):
    grouped = {}
    for entry in items:
        _, item, _ = entry
        grouped.setdefault(item.category, []).append(entry)
    return grouped

def _inventory_category_menu(player: Character, *, mode: str):
    items = get_inventory_items(player, equippable_only=False)
    if not items:
        print("\nInventory is empty.")
        input("Press Enter to continue...")
        return None

    grouped = group_inventory_by_category(items)

    categories = [c for c in ITEM_TYPE_ORDER if c in grouped]

    while True:
        print("\n--- Inventory Categories ---")
        for i, cat in enumerate(categories, start=1):
            total = sum(count for _, _, count in grouped[cat])
            print(f"{i}. {cat.value.title()} ({total})")
        print("c. Back")

        choice = input("> ").strip().lower()
        if choice in ("c", "back"):
            return None

        if not choice.isdigit():
            print("Invalid input.")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(categories):
            print("Invalid selection.")
            continue

        category = categories[idx]
        result = _paginated_inventory_view(
            player,
            grouped[category],
            category,
            mode=mode
        )

        if mode == "use" and result is not None:
            return result

def _paginated_inventory_view(
    player: Character,
    entries: list[tuple[str, Items, int]],
    category: Item_Type,
    *,
    mode: str,
):
    ITEMS_PER_PAGE = 8
    page = 0

    while True:
        total_pages = max(1, (len(entries) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = max(0, min(page, total_pages - 1))

        start = page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = entries[start:end]

        print(f"\n--- {category.value.title()} (Page {page + 1}/{total_pages}) ---")

        for idx, (inv_key, item, count) in enumerate(page_items, start=1):
            print(f"{idx}. {item.name} x{count}")
            tooltip = item.get_tooltip()
            if tooltip:
                print(f"{tooltip}\n")

        print("\n[n]ext  [p]rev  [back]")
        if mode == "use":
            print("Select item number to use")

        choice = input("> ").strip().lower()

        if choice in ("back", "c"):
            return None

        if choice == "n":
            page = (page + 1) % total_pages
            continue

        if choice == "p":
            page = (page - 1) % total_pages
            continue

        if not choice.isdigit():
            print("Invalid input.")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(page_items):
            print("Invalid selection.")
            continue

        if mode == "view":
            continue  # view-only; numbers do nothing

        # mode == "use"
        inv_key, item, _ = page_items[idx]
        return inv_key, item

def _paginated_equip_view(player: Character, entries: list[tuple[str, Items, int]]):
    ITEMS_PER_PAGE = 8
    page = 0

    while True:
        total_pages = max(1, (len(entries) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = max(0, min(page, total_pages - 1))

        start = page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_items = entries[start:end]

        print(f"\n--- Choose Item to Equip (Page {page + 1}/{total_pages}) ---")

        for idx, (_, item, count) in enumerate(page_items, start=1):
            print(f"{idx}. {item.name} x{count}")
            tooltip = item.get_tooltip()
            if tooltip:
                print(f"{tooltip}\n")

        print("\n[n]ext  [p]rev  [back]")
        choice = input("> ").strip().lower()

        if choice in ("back", "c"):
            return None

        if choice == "n":
            page = (page + 1) % total_pages
            continue

        if choice == "p":
            page = (page - 1) % total_pages
            continue

        if not choice.isdigit():
            print("Invalid input.")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(page_items):
            print("Invalid selection.")
            continue

        _, item, _ = page_items[idx]
        return item


def render_player_status(player: Character):
    print("\n=== PLAYER STATUS ===")
    print(f"Name: {player.name}")

    res = f"| {player.resource_name.upper()}: {player.resource_current}/{player.resource_max}"
    print(f"HP: {player.hp}/{player.max_hp} {res}")

    xp, xp_needed, at_cap = get_xp_progress(player)

    if at_cap:
        print(f"Level: {player.level} (MAX)")
        print(f"XP: {xp} / {xp_needed}")
    else:
        print(f"Level: {player.level}")
        print(f"XP: {xp} / {xp_needed}")

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

def get_xp_progress(player: Character) -> tuple[int, int, bool]:
    if player.class_id is None:
        return (0, 0, True)

    prog = CLASS_PROGRESSION[player.class_id]
    xp_table = prog["xp_per_level"]
    level_cap = prog["level_cap"]

    if player.level >= level_cap:
        return (player.xp, xp_table[level_cap], True)

    return (player.xp, xp_table[player.level], False)
