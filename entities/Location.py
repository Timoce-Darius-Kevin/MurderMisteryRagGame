from entities.Room import Room
class Location:
    
    def __init__(self, name: str, description: str, max_players: int, event_description = "", rooms: list[Room] = []) -> None:
        self.name: str = name
        self.description: str = description
        self.event_description = event_description
        # TODO: self.effect: Effect = effect
        self.max_players: int = max_players
        self.rooms: list[Room] = rooms
        self.starting_room: Room = Room("Main Entrance", "The grand entrance to the manor, with a massive oak door and marble floors.", 10, "general")
        self.rooms.append(self.starting_room)
        self._connect_rooms_logically()
        
    def _connect_rooms_logically(self) -> None:
            """Connect rooms in a logical mansion layout"""
            entrance = self.starting_room
            
            # Categorize rooms by type
            main_rooms = [r for r in self.rooms if r.room_type == "general" and r != entrance]
            bedrooms = [r for r in self.rooms if r.room_type == "bedroom"]
            outdoor_areas = [r for r in self.rooms if r.room_type == "outdoor"]
            service_rooms = [r for r in self.rooms if r.room_type == "service"]
            special_rooms = [r for r in self.rooms if r.room_type == "special"]
            
            # Entrance connects to main gathering areas
            for room in main_rooms[:3]:  # Connect to first 3 main rooms
                entrance.connected_rooms.append(room)
                room.connected_rooms.append(entrance)
            
            # Main rooms connect to each other
            for i in range(len(main_rooms) - 1):
                main_rooms[i].connected_rooms.append(main_rooms[i + 1])
                main_rooms[i + 1].connected_rooms.append(main_rooms[i])
            
            # Some main rooms connect to outdoor areas
            if main_rooms and outdoor_areas:
                main_rooms[0].connected_rooms.extend(outdoor_areas[:2])
                for outdoor in outdoor_areas[:2]:
                    outdoor.connected_rooms.append(main_rooms[0])
            
            # Service areas connect to kitchen/dining areas
            kitchen = next((r for r in self.rooms if "Kitchen" in r.name), None)
            if kitchen and service_rooms:
                kitchen.connected_rooms.extend(service_rooms)
                for service in service_rooms:
                    service.connected_rooms.append(kitchen)