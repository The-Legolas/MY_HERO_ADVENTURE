
class Items():
    def __init__(self, name: str, type: str, effect:any=None, damage: int=None):
        self.name = name
        self.type = type
        self.damage = damage
        self.effect = effect

    def list():
        list_of_items = []

        list_of_items.append(Items("sword", "weapon", None, 10))
        list_of_items.append(Items("bag", "key item", "holds more space user is now lighter"))
        list_of_items.append(Items("hp potion", "usable", "give hp", 100))

        return list_of_items