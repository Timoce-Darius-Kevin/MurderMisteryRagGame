from Player import Player
class Conversation:
    def __init__(self, player: Player, question: str, response: str, suspicion_change: int):
        self.player = player
        self.question = question
        self.response = response
        self.suspicion_change = suspicion_change