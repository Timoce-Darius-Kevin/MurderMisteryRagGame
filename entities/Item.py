class Item:
    def __init__(self, name: str, description: str, item_type: str, murder_weapon: bool = False, value: int = 0, known = False) -> None:
        self.name: str = name
        self.description: str = description
        self.item_type: str = item_type
        # TODO: self.danger: int = danger
        # TODO: self.effect: Effect = effect
        # TODO: self.number_of_uses: int = uses
        # TODO: self.danger: int = danger
        self.murder_weapon: bool = murder_weapon
        self.value: int = value
        self.known = known