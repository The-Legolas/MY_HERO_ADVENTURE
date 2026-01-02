from game.ui.text_screens import TextScreen

def show_boss_intro():
    intro = TextScreen(
        title="The Castle Depths",
        pages=[
            (
                "The air grows heavy as you step forward.\n\n"
                "Each breath feels warmer than the last. "
                "The stone beneath your feet is scorched and cracked."
            ),

            (
                "This place was not abandoned.\n\n"
                "It was sealed.\n\n"
                "Whatever sleeps here was never meant to wake again."
            ),

            (
                "A deep rumble echoes through the chamber.\n\n"
                "Something ancient stirs in the darkness ahead."
            ),
        ]
    )

    intro.show()
    print()
