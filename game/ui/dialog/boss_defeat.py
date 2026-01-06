from game.ui.class_text_screens import TextScreen

def show_boss_defeat():
    defeat = TextScreen(
        title="Defeat",
        pages=[
            (
                "The heat becomes unbearable.\n\n"
                "Your strength fails you as the dragon looms overhead."
            ),

            (
                "Steel and resolve are not enough.\n\n"
                "The ancient guardian of the castle remains unbroken."
            ),

            (
                "The beast settles back into the depths.\n\n"
                "The castle stays sealed.\n"
                "And the town below waits… unaware how close hope came."
            ),
        ]
    )

    defeat.show()
    print()
