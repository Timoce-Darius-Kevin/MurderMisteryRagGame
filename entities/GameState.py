class GameState:
    def __init__(self):
        self.current_turn: int = 0
        self.game_active: bool = True
        self.murder_solved: bool = False