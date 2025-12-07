
def normalize_input(text_input: str) -> str | None:
    t = text_input.strip().lower()

    if t in ("1", "shop", "enter shop", "go shop", "go to shop"):
        return "enter_shop"

    if t in ("2", "inn", "enter inn", "go inn", "go to inn"):
        return "enter_inn"

    if t in ("3", "tavern", "enter tavern", "go tavern", "go to tavern"):
        return "enter_tavern"

    if t in ("4", "leave", "leave town", "exit", "go outside"):
        return "leave_town"

    if t in ("talk", "5", "speak"):
        return "talk"

    if t in ("leave building", "exit building", "leave", "back"):
        return "leave_building"

    #    Leave Town submenu
    if t in ("1", "back", "return"):
        return "go_back"

    if t in ("2", "enter cave", "cave", "go cave"):
        return "enter_cave"

    if t in ("3", "enter castle", "castle", "go castle"):
        return "enter_castle"

    return None
