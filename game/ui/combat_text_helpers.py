
def format_name(name: str | None) -> str:
    return name if name else "Unknown"


def format_skill_name(skill_id: str | None) -> str:
    if not skill_id:
        return "Skill"
    return skill_id.replace("_", " ").title()


def describe_wait(extra: dict) -> str:
    state = extra.get("state")
    if state:
        return f"is {state}"
    return "is gathering power"


def describe_attack(actor, target, damage, blocked, critical):
    if blocked:
        return f"{actor}'s attack was blocked by {target}!"
    text = f"{actor} hits {target} for {damage} damage"
    if critical:
        text += " CRITICAL HIT"
    return text + "."


def describe_skill(actor, target, extra, damage, blocked):
    skill_name = format_skill_name(extra.get("skill"))
    missed = extra.get("missed", False)

    if missed:
        return f"{actor} uses {skill_name}, but misses!"

    if blocked:
        return f"{actor}'s {skill_name} was blocked by {target}!"

    text = f"{actor} uses {skill_name}"
    if target:
        text += f" on {target}"
    if damage > 0:
        text += f" for {damage} damage"
    return text + "."
