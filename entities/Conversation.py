from entities.Question import Question
class Conversation:
    def __init__(self, question: Question, response: str = "") -> None:
        self.question = question
        self.response = response