from Item import Item

class Player:
    
    def __init__(self, id: int, name: str, suspicion: int, inventory: list[Item] = []) -> None:
        self.id: int = id
        self.name: str = name
        # TODO: self.job: Job = job
        # TODO: self.job: str = job
        self.suspicion: int = suspicion
        self.murderer: bool = False
        self.inventory: list[Item] = inventory