class Room:
    
    def __init__(self, name: str, description: str, capacity: int, room_type="general") -> None:
        self.name: str = name
        self.description: str = description
        # TODO: self.effect: Effect = effect
        self.room_type = room_type # general, bedroom, outdoor, service, special
        self.capacity: int = capacity
        self.connected_rooms: list[Room] = []