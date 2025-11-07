class Item:
    def __init__(self, name: str, description: str, murder_weapon: bool = False) -> None:
        self.name: str = name
        self.description: str = description
        # TODO: self.danger: int = danger
        # TODO: self.effect: Effect = effect
        # TODO: self.uses: int = uses
        # TODO: self.danger: int = danger
        self.murder_weapon: bool = murder_weapon