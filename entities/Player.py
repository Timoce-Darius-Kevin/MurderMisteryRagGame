import random
from .Item import Item

class Player:
    
    def __init__(self, id: int, name: str, suspicion: int, job: str = "None", inventory: list[Item] = []) -> None:
        self.id: int = id
        self.name: str = name
        # TODO: self.job: Job = job; implement job entity
        self.job: str = job
        self.suspicion: int = suspicion
        self.murderer: bool = False
        self.inventory: list[Item] = inventory
        self.mood: str = "neutral" # neutral, defensive, cooperative, angry
        self.lying_ability: int = random.randint(1, 10)