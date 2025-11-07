from Player import Player
class Conversation:
    def __init__(self, speaker: Player, listener: Player, question: str, response: str = "", suspicion_change_speaker: int = 0, suspicion_change_listener: int = 0) -> None:
        self.speaker = speaker
        self.listener = listener
        self.question = question
        self.response = response
        self.suspicion_change_speaker = suspicion_change_speaker
        self.suspicion_change_listener = suspicion_change_listener