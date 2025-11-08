from entities.Player import Player
from entities.Room import Room
from entities.Conversation import Conversation, Question
from entities.Location import Location
from entities.GameState import GameState
from .RagManager import RagManager
import random

class GameManager:
    
    def __init__(self, location: Location, user_player: Player, game_state: GameState = GameState(), max_turns: int = 20, suspicion_limit = 35) -> None:
        self.location = location
        self.user_player = user_player
        self.suspicion_limit = suspicion_limit
        self.player_tracking: dict[Player, Room] = {}
        self.game_state = game_state
        self.max_turns = max_turns
        self.conversation_history: list[Question] = []
        self.initialize_game()
        self.rag_manager = RagManager()
    
    def initialize_game(self) -> None:
        """ Place all players in the starting room """
        # In phase 1 this is the only room, where everyone is.
        # In phase 1 and 2 all players are placeholders with placeholder data.
        self.add_player(self.user_player)
        for player_idx in range(1, self.location.max_players):
            new_player = Player(id=player_idx, name=f"Player {player_idx}", suspicion=0)
            self.add_player(new_player)
        self.select_murderer()
    
    def select_murderer(self):
        murderer = random.choice([player for player in self.get_players() \
            if player.id != 0])
        murderer.murderer = True
        print(f"DEBUG: Murderer is {murderer.name}")

    def add_player(self, player) -> None:
        self.player_tracking[player] = self.location.starting_room
    
    def get_rooms(self) -> list[Room]:
        return list(self.location.rooms)
    
    def get_players(self) -> list[Player]:
        return list(self.player_tracking.keys())
    
    def get_player_by_name(self, name: str) -> Player | None:
        for player in self.player_tracking.keys():
            if player.name == name:
                return player
        return None

    def get_other_players_in_room(self, room: Room) -> list[Player]:
        return [player for player, player_room in self.player_tracking.items() \
                if player_room == room and player.id != 0]

    def get_current_room(self):
        return self.player_tracking[self.user_player]

    def move_player_to_room(self, player: Player, room: Room) -> None:
        if player in self.player_tracking:
            self.player_tracking[player] = room
        self.advance_turn()
    def strike_conversation(self, question: Question) -> tuple[str, int]:
        response_text, suspicion_change = self.rag_manager.generate_response(question)
        conversation = Conversation(question, response_text)
        self.rag_manager.add_conversation(conversation, self.game_state.current_turn)
        question.speaker.suspicion += suspicion_change
        self.advance_turn()
        self.advance_turn()
        return response_text, suspicion_change
    
    def accuse_player(self, accuser: Player, accused: Player) -> bool:
        if accused.murderer:
            self.end_game(positive=True)
            return True
        else:
            accuser.suspicion += 30
            self.advance_turn()
            return False
        

    
    def advance_turn(self) -> None:
        self.game_state.current_turn += 1
        if self.game_state.current_turn >= self.max_turns:
            self.end_game(positive=False)
        if self.user_player.suspicion > self.suspicion_limit:
            self.end_game(positive=False)
    
    def end_game(self, positive: bool) -> None:
        self.game_state.game_active = False 
        if positive:
            self.game_state.murder_solved = True