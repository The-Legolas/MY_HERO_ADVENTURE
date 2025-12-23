class Status():
    def __init__(self, id: str, remaining_turns: int, magnitude: int | dict | None, source: str | None = None):
        self.id = id
        self.remaining_turns = remaining_turns
        self.source = source
        self.magnitude = magnitude
        self.just_applied = True