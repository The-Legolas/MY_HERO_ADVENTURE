import os
from typing import Optional

SAVE_ROOT = "saves"


def _get_save_slots() -> list[str]:
    if not os.path.exists(SAVE_ROOT):
        return []

    return sorted(
        name for name in os.listdir(SAVE_ROOT)
        if os.path.isdir(os.path.join(SAVE_ROOT, name))
    )


def run_save_load_menu(*, mode: str, current_slot: Optional[str] = None) -> Optional[str]:


    assert mode in ("save", "load")

    slots = _get_save_slots()

    while True:
        print("\n=== SAVE FILES ===")

        if not slots:
            print("No save files found.")
        else:
            for idx, slot in enumerate(slots, start=1):
                marker = ""
                if slot == current_slot:
                    marker = " (current)"
                print(f"{idx}. {slot}{marker}")

        print()

        option_idx = len(slots) + 1

        if mode == "save":
            print(f"{option_idx}. Create new save")
            option_idx += 1

        print(f"{option_idx}. Back")

        choice = input("\nChoose a slot (number or name): ").strip()

        if (choice.lower() in ("back", "b", "cancel", "c")):
            return None

        if choice.isdigit():
            num = int(choice)

            if 1 <= num <= len(slots):
                return slots[num - 1]

            if mode == "save" and num == len(slots) + 1:
                return _prompt_new_slot_name(slots)

            if num == option_idx:
                return None

            print("Invalid selection.")
            continue

        if choice:
            if choice in slots:
                return choice

            if mode == "save":
                return _prompt_custom_slot_name(choice, slots)

            print("Save not found.")
            continue


def _prompt_new_slot_name(existing_slots: list[str]) -> Optional[str]:
    while True:
        name = input("\nEnter new save name (or 'back'): ").strip()

        if not name or name.lower() == "back":
            return None

        if name in existing_slots:
            print("That save already exists.")
            continue

        return name


def _prompt_custom_slot_name(
    proposed_name: str,
    existing_slots: list[str],
) -> Optional[str]:
    if proposed_name in existing_slots:
        return proposed_name

    confirm = input(
        f"Create new save '{proposed_name}'? (y/n): "
    ).strip().lower()

    if confirm == "y":
        return proposed_name

    return None
