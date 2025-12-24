class Status():
    def __init__(self, id: str, remaining_turns: int, magnitude: int | dict | None, source: str | None = None, expires_end_of_turn: bool = False):
        self.id = id
        self.remaining_turns = remaining_turns
        self.source = source
        self.magnitude = magnitude
        self.just_applied = True
        self.expires_end_of_turn = expires_end_of_turn