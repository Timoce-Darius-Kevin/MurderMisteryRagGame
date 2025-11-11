from entities.Player import Player
from managers.GameStateManager import GameStateManager


class AccusationManager:
    def __init__(self, game_state_manager: GameStateManager):
        self.game_state_manager = game_state_manager
    
    def accuse_player(self, accuser: Player, accused: Player) -> bool:
        if self.validate_accusation(accused):
            # TODO: Game should end
            return True
        else:
            self.handle_wrong_accusation(accuser, 30)
            return False
        
    def validate_accusation(self, accused: Player) -> bool:
        return accused.murderer
    
    def handle_wrong_accusation(self, accuser: Player, suspicion_change: int) -> None:
        accuser.suspicion += suspicion_change