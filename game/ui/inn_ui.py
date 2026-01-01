from game.core.Character_class import Character
from game.world.Gen_Game_World import Game_World
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.engine.game_engine import GameEngine


class InnUI:
    def __init__(self, player: Character, world: Game_World, engine: 'GameEngine'):
        self.player = player
        self.world = world
        self.engine = engine

    def run_inn_menu(self, metadata: dict):
        night_cost = metadata.get("night_cost", 50)
        heal_amount = metadata.get("heal_amount", "full")

        while True:
            print("\n--- INN ---")
            print(f"Gold: {self.player.inventory['gold']}")
            print("1. Rest (Recover HP)")
            print("2. Talk")
            print("3. Leave Inn\n")

            choice = input("> ").strip().lower()

            if choice in ("1", "rest", "sleep"):
                self.rest(night_cost, heal_amount)

            elif choice in ("2", "talk", "speak"):
                self.talk()

            elif choice in ("3", "leave", "exit"):
                return

            else:
                print("Invalid input.")

    def rest(self, cost: int, heal_amount: str):
        if self.player.inventory["gold"] < cost:
            print("\nYou cannot afford to stay the night.")
            input()
            return

        while True:
            confirm = input(f"Do you want to rest for {cost}? (yes/no) > ").strip().lower()
            if confirm not in ("yes", "y"):
                print("Purchase cancelled.")
                input()
                return                

            self.player.inventory["gold"] -= cost

            if heal_amount == "full":
                self.player.hp = self.player.max_hp
                self.player.clear_negative_statuses()

            self.engine._handle_day_transition(context="rest")
            return

    def talk(self):
        print("\nThe innkeeper smiles: 'Stay safe out there, adventurer.'")
        input()
