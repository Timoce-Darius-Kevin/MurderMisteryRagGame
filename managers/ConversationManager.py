from entities.Conversation import Conversation, Question
from managers.RagManager import RagManager
from managers.GameStateManager import GameStateManager


class ConversationManager:
    
    def __init__(self, rag_manager: RagManager, game_state_manager: GameStateManager):
        self.rag_manager = rag_manager
        self.game_state = game_state_manager.game_state

    def strike_conversation(self, question: Question) -> tuple[str, int]:
        response_text, suspicion_change = self.rag_manager.generate_response(question)
        conversation = Conversation(question, response_text)
        self.rag_manager.add_conversation(conversation, self.game_state.current_turn)
        question.listener.suspicion += suspicion_change
        return response_text, suspicion_change