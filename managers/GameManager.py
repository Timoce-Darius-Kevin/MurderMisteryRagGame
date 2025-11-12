from entities.Player import Player
from entities.Room import Room
from entities.Conversation import Question
from entities.Location import Location
from managers.AccusationManager import AccusationManager
from managers.ConversationManager import ConversationManager
from managers.GameStateManager import GameStateManager
from managers.PlayerManager import PlayerManager
from .RagManager import RagManager

class GameManager:
    
    def __init__(self, location: Location, user_player: Player, max_turns: int = 20, suspicion_limit: int = 35):
        self.location = location
        self.user_player = user_player
        
        self.player_manager = PlayerManager()
        self.game_state_manager = GameStateManager(max_turns, suspicion_limit)
        self.rag_manager = RagManager()
        self.conversation_manager = ConversationManager(self.rag_manager, self.game_state_manager, self.player_manager, self.location)
        self.accusation_manager = AccusationManager(self.game_state_manager)
        
        self.initialize_game()
    
    def initialize_game(self) -> None:
        """Place all players in the starting room """
        self.player_manager.setup_players(self.location, self.user_player)
        self.player_manager.select_murderer()
        
    def advance_turn_with_npc_movement(self) -> None:
        """Advance turn and move NPCs"""
        self.game_state_manager.advance_turn()
        self.player_manager.move_npcs_randomly()
    
    def move_player(self, player: Player, room: Room) -> None:
        self.player_manager.move_player_to_room(player, room)
        if player is self.user_player:
            self.advance_turn_with_npc_movement()
    
    def strike_conversation(self, question: Question) -> tuple[str, int, int]:
        response, suspicion_change_speaker, suspicion_change_listener = self.conversation_manager.strike_conversation(question)
        self.advance_turn_with_npc_movement()
        return response, suspicion_change_speaker, suspicion_change_listener
    
    def accuse_player(self, accuser: Player, accused: Player) -> bool:
        result = self.accusation_manager.accuse_player(accuser, accused)
        if result is True:
            self.game_state_manager.end_game(win_condition=True)
        return result

    def get_rooms(self) -> list[Room]:
        return list(self.location.rooms)
    
    def get_current_room(self) -> Room:
        return self.player_manager.get_current_room(self.user_player)
    
    def get_other_players_in_current_room(self) -> list[Player]:
        current_room = self.get_current_room()
        return self.player_manager.get_other_players_in_room(current_room, self.user_player)
    
    def is_game_active(self) -> bool:
        return self.game_state_manager.is_game_active()
    
