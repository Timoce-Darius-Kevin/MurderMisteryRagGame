from .Player import Player

class Question:
    def __init__(self, speaker: Player, listener: Player, question: str) -> None:
        self.speaker = speaker
        self.listener = listener
        self.question = question
        
class Conversation:
    def __init__(self, question: Question, response: str = "") -> None:
        self.question = question
        self.response = response