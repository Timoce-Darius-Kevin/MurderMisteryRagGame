from random import randint, choice
from entities.Conversation import Conversation
from entities.Game_State import GameState
from entities.Location import Location
from entities.Player import Player
from entities.Room import Room

class Game_Manager:
    
    def __init__(self, location: Location) -> None:
        self.location: Location = location
        self.player_tracking: dict[Player, Room] = {}
        self.players: list[Player] = []
        self.conversations: list[Conversation] = []
        self.GameState = GameState()
        self.initialize_game()
        self.MAX_PROBABILITY = 1000000
        self.user_player_id = -1
        
    
    def initialize_game(self):
        for player_id in range(0, self.location.max_players - 1):
            player = Player(player_id, f"Player {player_id}", 0)
            self.add_player(player, self.location.starting_room)
        self.add_user_player(Player(self.user_player_id, "User Player", 0))
        
    def add_user_player(self, player: Player):
        room = self.location.starting_room
        self.player_tracking[player] = room
    
    def add_player(self, player: Player, room: Room):
        self.player_tracking[player] = room
    
    def move_player(self, player: Player, new_room: Room):
        if player in self.player_tracking:
            self.player_tracking[player] = new_room
        self.advance_turn()
        if self.GameState.current_turn > 100:
            self.end()
    
    def ask_question(self, player: Player, question: str, response: str, suspicion_change: int):
        conversation = Conversation(player, question, response, suspicion_change)
        self.conversations.append(conversation)
        player.suspicion += suspicion_change
        self.advance_turn()
        if self.GameState.current_turn > 100:
            self.end()
    
    def advance_turn(self):
        self.GameState.current_turn += 1
        if self.GameState.current_turn > 100:
            self.end()
        for player in self.player_tracking:
            if randint(0, self.MAX_PROBABILITY) < self.MAX_PROBABILITY / 100:
                room = choice(self.location.rooms)
                while(room == self.player_tracking[player]):
                    room = choice(self.location.rooms)
                self.move_player(player, room)
                print(f"=== GAME_MANAGER: {player.name} moved to {room.name} ===")
            
    def end(self):
        self.GameState.game_active = False
        
    