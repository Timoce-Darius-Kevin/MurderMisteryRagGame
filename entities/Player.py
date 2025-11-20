import random
from entities.Item import Item
from config.GameConfig import GameConfig


class Player:
    
    def __init__(self, id: int, name: str, suspicion: int, job: str = "None", inventory: list[Item] = []) -> None:
        self.id: int = id
        self.name: str = name
        # TODO: self.job: Job = job; implement job entity
        self.job: str = job
        self.suspicion: int = suspicion
        self.murderer: bool = False
        self.inventory: list[Item] = inventory if inventory else []
        self.mood: str = "neutral"  # neutral, defensive, cooperative, angry
        self.lying_ability: int = random.randint(GameConfig.LYING_ABILITY_MIN, GameConfig.LYING_ABILITY_MAX)
    
    def get_known_items(self) -> list[Item]:
        """Get items that are known to others"""
        return [item for item in self.inventory if item.known]
