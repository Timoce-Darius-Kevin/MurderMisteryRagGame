import random
from entities.Item import Item
from entities.Location import Location
from entities.Player import Player
from entities.Room import Room
from config.GameConfig import GameConfig


class PlayerManager:
    
    def __init__(self):
        self.player_tracking: dict[Player, Room] = {}
        
    def setup_players(self, location: Location, user_player: Player):
        player_names = ["James", "Mary", "Michael", "Patricia", "John", "Jennifer", "Robert", "Linda", "David", "Elizabeth"]
        player_surnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        jobs = ["Doctor", "Professor", "Businessperson", "Artist", "Writer", "Engineer", "Detective", "Servant"]
        
        self.add_player(user_player, location.starting_room)
        
        for player_idx in range(1, location.max_players):
            name = f"{random.choice(player_names)} {random.choice(player_surnames)}"
            job = random.choice(jobs)
            new_player = Player(id=player_idx, name=name, suspicion=0, job=job)
            
            # Add to random room (except starting room for variety)
            random_room = random.choice(location.rooms)
            self.add_player(new_player, random_room)
        
        self._assign_inventories()

    def _assign_inventories(self) -> None:
        """Assign inventories to all players"""
        for player in self.get_players():
            is_murderer = player.murderer
            self._generate_inventory(player, is_murderer)
            
    def select_murderer(self):
        murderer = random.choice([player for player in self.get_players() \
            if player.id != 0])
        murderer.murderer = True
        print(f"DEBUG: Murderer is {murderer.name}")
        
    def _generate_inventory(self, player: Player, is_murderer: bool) -> None:
        """Generate random inventory for players"""
        common_items = [
            Item("Pocket Watch", "A silver pocket watch", "personal", False, 5),
            Item("Handkerchief", "A monogrammed handkerchief", "personal", False, 1),
            Item("Letter", "A folded letter", "clue", False, 3),
            Item("Key", "A small brass key", "tool", False, 2),
            Item("Coin Purse", "A leather coin purse", "personal", False, 4)
        ]
        
        weapon_items = [
            Item("Candlestick", "A heavy silver candlestick", "weapon", True, 8),
            Item("Dagger", "A sharp ornamental dagger", "weapon", True, 9),
            Item("Poison Vial", "A small glass vial", "weapon", True, 7),
            Item("Rope", "A length of strong rope", "weapon", True, 6)
        ]
        player.inventory.clear()
        if is_murderer:
            murder_weapon = random.choice(weapon_items)
            murder_weapon.murder_weapon = True
            player.inventory.append(murder_weapon)
            player.inventory.extend(random.sample(common_items, random.randint(1, 2)))
        else:
            player.inventory.extend(random.sample(common_items, random.randint(2, 3)))
        
        # Make some items known by default (personal items)
        for item in player.inventory:
            if item.item_type == "personal" and not item.murder_weapon:
                item.known = True
            
    def move_npcs_randomly(self) -> None:
        """Move NPCs to random connected rooms"""
        for player in self.get_players():
            if player.id != 0:
                current_room = self.get_current_room(player)
                if random.random() < GameConfig.NPC_MOVE_PROBABILITY:
                    if current_room.connected_rooms:
                        self.decay_mood_toward_neutral(player)  # moving makes people more stable
                        new_room = random.choice(current_room.connected_rooms)
                        players_in_room = self.get_players_in_room(new_room)
                        if len(players_in_room) < new_room.capacity:
                            self.move_player_to_room(player, new_room)

    def get_players_in_room(self, room: Room) -> list[Player]:
        """Get all players in a specific room"""
        return [player for player, player_room in self.player_tracking.items() if player_room == room]
    
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
    
    def change_mood_based_on_conversation(self, player: Player, question: str, response: str, suspicion_change: int) -> None:
        """Update player mood based on conversation content and suspicion changes"""
        question_lower = question.lower()
        response_lower = response.lower()
        
        aggressive_keywords = ["murder", "kill", "weapon", "blood", "guilty", "accuse", "alibi"]
        defensive_keywords = ["none of your business", "stop asking", "not your concern", "i refuse"]
        cooperative_keywords = ["help", "assist", "truth", "honest", "cooperate"]
        
        mood_change = "neutral"

        if suspicion_change >= 5:
            mood_change = "angry"
        elif suspicion_change >= 3:
            mood_change = "defensive"
        elif suspicion_change <= -2:
            mood_change = "cooperative"
        
        # Question content affects mood
        elif any(keyword in question_lower for keyword in aggressive_keywords):
            if player.mood == "neutral":
                mood_change = "defensive"
            elif player.mood == "defensive":
                mood_change = "angry"
        
        # Response content affects mood
        elif any(keyword in response_lower for keyword in defensive_keywords):
            mood_change = "defensive"
        elif any(keyword in response_lower for keyword in cooperative_keywords):
            mood_change = "cooperative"
        
        # Apply mood change
        if mood_change != "neutral":
            player.mood = mood_change

    def decay_mood_toward_neutral(self, player: Player) -> None:
        """Gradually return mood to neutral over time"""
        if player.mood != "neutral":
            if random.random() < GameConfig.MOOD_DECAY_PROBABILITY:
                if player.mood == "angry":
                    player.mood = "defensive"
                elif player.mood == "defensive" or player.mood == "cooperative":
                    player.mood = "neutral"
