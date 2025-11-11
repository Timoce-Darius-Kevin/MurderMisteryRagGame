import random
from entities.Location import Location
from entities.Player import Player
from entities.Room import Room


class PlayerManager:
    
    def __init__(self):
        self.player_tracking: dict[Player, Room] = {}
        
    def setup_players(self, location: Location, user_player: Player):
        player_names = ["James", "Mary", "Michael", "Patricia", "John", "Jennifer", "Robert", "Linda", "David", "Elizabeth",\
            "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Karen", "Christopher", "Sarah"]

        player_surnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",\
            "Martinez", "Hernandez", "Lopez", "Gonzales", "Wilson", "Anderson"]
        
        self.add_player(user_player, location.starting_room)
        for player_idx in range(1, location.max_players):
            new_player = Player(id=player_idx, name=f"{random.choice(player_names)} {random.choice(player_surnames)}", suspicion=0)
            self.add_player(new_player, location.starting_room)
            
    def select_murderer(self):
        murderer = random.choice([player for player in self.get_players() \
            if player.id != 0])
        murderer.murderer = True
        print(f"DEBUG: Murderer is {murderer.name}")
        
    def add_player(self, player, room: Room) -> None:
        self.player_tracking[player] = room
        
    def move_player_to_room(self, player: Player, room: Room) -> None:
        if player in self.player_tracking:
            self.player_tracking[player] = room
    
    def get_other_players_in_room(self, room: Room, exclude_player: Player) -> list[Player]:
        return [player for player, player_room in self.player_tracking.items() \
                if player_room == room and player.id != exclude_player.id]
        
    def get_players(self) -> list[Player]:
        return list(self.player_tracking.keys())
    
    def get_player_by_name(self, name: str) -> Player | None:
        for player in self.player_tracking.keys():
            if player.name == name:
                return player
            
    def get_current_room(self, player: Player):
        return self.player_tracking[player]