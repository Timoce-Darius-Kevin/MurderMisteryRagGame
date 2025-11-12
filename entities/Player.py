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
    
    def change_mood_based_on_conversation(self, question: str, response: str, suspicion_change: int) -> None:
        """Update player mood based on conversation content and suspicion changes"""
        question_lower = question.lower()
        response_lower = response.lower()
        
        aggressive_keywords = ["murder", "kill", "weapon", "blood", "guilty", "accuse", "alibi"]
        defensive_keywords = ["none of your business", "stop asking", "not your concern", "i refuse"]
        cooperative_keywords = ["help", "assist", "truth", "honest", "cooperate"]
        
        mood_change = "neutral"

        if suspicion_change >= 5:
            mood_change = "angry"
        elif suspicion_change >= 3:
            mood_change = "defensive"
        elif suspicion_change <= -2:
            mood_change = "cooperative"
        
        # Question content affects mood
        elif any(keyword in question_lower for keyword in aggressive_keywords):
            if self.mood == "neutral":
                mood_change = "defensive"
            elif self.mood == "defensive":
                mood_change = "angry"
        
        # Response content affects mood
        elif any(keyword in response_lower for keyword in defensive_keywords):
            mood_change = "defensive"
        elif any(keyword in response_lower for keyword in cooperative_keywords):
            mood_change = "cooperative"
        
        # Apply mood change
        if mood_change != "neutral":
            self.mood = mood_change

    def decay_mood_toward_neutral(self) -> None:
        """Gradually return mood to neutral over time"""
        if self.mood != "neutral":
            # 20% chance per turn to return to neutral
            if random.random() < 0.2:
                if self.mood == "angry":
                    self.mood = "defensive"
                elif self.mood == "defensive" or self.mood == "cooperative":
                    self.mood = "neutral"