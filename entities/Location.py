from .Room import Room
class Location:
    
    def __init__(self, name: str, description: str, max_players: int, rooms: list[Room] = []) -> None:
        self.name: str = name
        self.description: str = description
        # TODO: self.effect: Effect = effect
        self.max_players: int = max_players
        self.rooms: list[Room] = rooms
        self.starting_room: Room = Room("Outside Entrance", "The entrance to the location.")
        self.rooms.append(self.starting_room)