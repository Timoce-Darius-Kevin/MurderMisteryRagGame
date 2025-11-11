from entities.GameState import GameState
from entities.Player import Player


class GameStateManager:
    def __init__(self, max_turns: int, suspicion_limit: int):
        self.game_state = GameState()
        self.max_turns = max_turns
        self.suspicion_limit = suspicion_limit
    
    def advance_turn(self) -> None:
        self.game_state.current_turn += 1
        if self.game_state.current_turn >= self.max_turns:
            self.end_game(win_condition=False)
        
    def check_game_conditions(self, user_player: Player) -> bool:
        if user_player.suspicion > self.suspicion_limit:
            return False
        return True
    
    def end_game(self, win_condition: bool) -> None:
        self.game_state.game_active = False 
        if win_condition:
            self.game_state.murder_solved = True
        
    def is_game_active(self) -> bool:
        return self.game_state.game_active
    
    def get_current_turn(self) -> int:
        return self.game_state.current_turn