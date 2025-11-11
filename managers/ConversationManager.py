from entities.Conversation import Conversation, Question
from entities.Location import Location
from managers.PlayerManager import PlayerManager
from managers.RagManager import RagManager
from managers.GameStateManager import GameStateManager


class ConversationManager:
    
    def __init__(self, rag_manager: RagManager, game_state_manager: GameStateManager, player_manager: PlayerManager, location: Location):
        self.rag_manager = rag_manager
        self.game_state = game_state_manager.game_state
        self.player_manager = player_manager
        self.location = location

    def strike_conversation(self, question: Question) -> tuple[str, int, int]:
        # Get current room and nearby players for context
        current_room = self.player_manager.get_current_room(question.listener)
        nearby_players = self.player_manager.get_players_in_room(current_room)
        
        response_text, suspicion_change_speaker, suspicion_change_listener = self.rag_manager.generate_response(
            question, self.location, current_room, nearby_players
        )
        conversation = Conversation(question, response_text)
        self.rag_manager.add_conversation(conversation, self.game_state.current_turn)
        question.listener.suspicion += suspicion_change_listener
        question.speaker.suspicion += suspicion_change_speaker
        return response_text, suspicion_change_speaker, suspicion_change_listener