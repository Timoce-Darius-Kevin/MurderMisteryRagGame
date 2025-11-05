from Effect import Effect

class Room:
    
    def __init__(self, name: str, description: str) -> None:
        self.name: str = name
        self.description: str = description
        # TODO: self.effect: Effect = effect
        # TODO: self.capacity: int = capacity