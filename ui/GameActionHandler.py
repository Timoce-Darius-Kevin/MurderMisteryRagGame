"""Handles game actions separated from UI concerns"""

from typing import Callable, Optional
from entities.Player import Player
from entities.Question import Question
from entities.Room import Room
from managers.GameManager import GameManager
from game_logic import ask_about_inventory, get_user_inventory


class GameActionHandler:
    """Handles game logic actions without UI dependencies"""
    
    def __init__(self, game_manager: GameManager, user_player: Player):
        self.game_manager = game_manager
        self.user_player = user_player
    
    def ask_question(self, player: Player, question_text: str) -> tuple[str, int, int]:
        """
        Ask a question to a player
        
        Args:
            player: The player to ask
            question_text: The question to ask
            
        Returns:
            tuple: (response, suspicion_change_speaker, suspicion_change_listener)
        """
        conversation = Question(self.user_player, player, question_text)
        return self.game_manager.strike_conversation(conversation)
    
    def accuse_player(self, accused: Player) -> bool:
        """
        Accuse a player of being the murderer
        
        Args:
            accused: The player to accuse
            
        Returns:
            bool: True if accusation is correct, False otherwise
        """
        return self.game_manager.accuse_player(self.user_player, accused)
    
    def ask_about_inventory(self, player: Player) -> dict:
        """
        Ask a player about their inventory
        
        Args:
            player: The player to ask
            
        Returns:
            dict: Response data with suspicion changes
        """
        return ask_about_inventory(self.game_manager, player)
    
    def move_to_room(self, room: Room) -> None:
        """
        Move the user player to a different room
        
        Args:
            room: The room to move to
        """
        self.game_manager.move_player(self.user_player, room)
    
    def get_players_in_current_room(self) -> list[Player]:
        """
        Get all other players in the current room
        
        Returns:
            list[Player]: Players in the current room (excluding user)
        """
        return self.game_manager.get_other_players_in_current_room()
    
    def get_all_rooms(self) -> list[Room]:
        """
        Get all available rooms
        
        Returns:
            list[Room]: All rooms in the location
        """
        return self.game_manager.get_rooms()
    
    def get_current_room(self) -> Room:
        """
        Get the current room
        
        Returns:
            Room: The room the user is currently in
        """
        return self.game_manager.get_current_room()
    
    def get_user_inventory(self) -> dict:
        """
        Get the user's inventory
        
        Returns:
            dict: Inventory data
        """
        return get_user_inventory(self.user_player)
    
    def get_player_details(self, player: Player) -> dict:
        """
        Get detailed information about a player
        
        Args:
            player: The player to get details for
            
        Returns:
            dict: Player details including known items
        """
        known_items = player.get_known_items()
        return {
            'player': player,
            'known_items': known_items
        }
    
    def is_game_active(self) -> bool:
        """
        Check if the game is still active
        
        Returns:
            bool: True if game is active, False otherwise
        """
        return self.game_manager.is_game_active()
    
    def cleanup(self) -> None:
        """Clean up game resources"""
        self.game_manager.cleanup()
