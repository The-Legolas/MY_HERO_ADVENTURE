from game.ui.text_screens import TextScreen

def show_ending_screen(player_name: str):
    ending = TextScreen(
        title="Epilogue",
        pages=[
            (
                "The dragon lets out a final, echoing roar.\n\n"
                "Stone trembles. Dust rains from the ceiling.\n"
                "Then — silence."
            ),

            (
                "For the first time in generations, the castle grows still.\n\n"
                "No heat rises from the depths.\n"
                "No distant growls answer your footsteps."
            ),

            (
                "Word spreads quickly.\n\n"
                "The roads grow safer. Trade returns.\n"
                "The town breathes again, no longer living in fear of what slept above it."
            ),

            (
                f"You did not come seeking glory.\n"
                f"You did not come to save a kingdom.\n\n"
                f"But history will remember the name:\n\n"
                f"{player_name}"
            ),

            (
                "Your adventure ends here.\n\n"
                "Thank you for playing My Hero Adventure."
            ),
        ]
    )

    ending.show()
