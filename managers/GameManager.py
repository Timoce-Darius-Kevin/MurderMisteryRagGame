from typing import Optional

from entities.Player import Player
from entities.Room import Room
from entities.Question import Question
from entities.Location import Location
from managers.AccusationManager import AccusationManager
from managers.ConversationManager import ConversationManager
from managers.GameStateManager import GameStateManager
from managers.PlayerManager import PlayerManager
from managers.ResourceManager import ResourceManager
from Services.ErrorHandler import ErrorHandler
from .RagManager import RagManager


class GameManager:
    """High-level façade coordinating game state and services."""

    def __init__(
        self,
        location: Location,
        user_player: Player,
        max_turns: int = 20,
        suspicion_limit: int = 35,
        error_handler: Optional[ErrorHandler] = None,
    ) -> None:
        """Create a new game manager.

        Args:
            location: The game location.
            user_player: The human‑controlled player.
            max_turns: Maximum number of turns before the game ends.
            suspicion_limit: Suspicion threshold at which the game ends.
            error_handler: Optional shared :class:`ErrorHandler` instance
                used by underlying services.
        """
        self.location = location
        self.user_player = user_player
        self.error_handler: ErrorHandler = error_handler or ErrorHandler()

        self.player_manager = PlayerManager()
        self.game_state_manager = GameStateManager(max_turns, suspicion_limit)
        self.rag_manager = RagManager(error_handler=self.error_handler)
        self.conversation_manager = ConversationManager(
            self.rag_manager,
            self.game_state_manager,
            self.player_manager,
            self.location,
        )
        self.accusation_manager = AccusationManager(self.game_state_manager)

        # Initialize resource manager
        self.resource_manager = ResourceManager(error_handler=self.error_handler)
        self.resource_manager.initialize(
            self.rag_manager.llm_service,
            self.rag_manager.memory_service,
            self.rag_manager.conversation_repository,
        )

        self.initialize_game()
    
    def initialize_game(self) -> None:
        """Place all players in the starting room."""
        self.player_manager.setup_players(self.location, self.user_player)
        self.player_manager.select_murderer()

    def advance_turn_with_npc_movement(self) -> None:
        """Advance the game turn and move NPCs."""
        self.game_state_manager.advance_turn()
        self.player_manager.move_npcs_randomly()

    def move_player(self, player: Player, room: Room) -> None:
        """Move a player to a different room.

        The game turn is advanced when the moving player is the user.
        """
        self.player_manager.move_player_to_room(player, room)
        if player is self.user_player:
            self.advance_turn_with_npc_movement()

    def strike_conversation(self, question: Question) -> tuple[str, int, int]:
        """Strike a conversation and advance the game turn."""
        response, suspicion_change_speaker, suspicion_change_listener = (
            self.conversation_manager.strike_conversation(question)
        )
        self.advance_turn_with_npc_movement()
        return response, suspicion_change_speaker, suspicion_change_listener

    def accuse_player(self, accuser: Player, accused: Player) -> bool:
        """Accuse a player and end the game on correct accusation."""
        result = self.accusation_manager.accuse_player(accuser, accused)
        if result is True:
            self.game_state_manager.end_game(win_condition=True)
        return result

    def get_rooms(self) -> list[Room]:
        """Return all rooms in the game location."""
        return list(self.location.rooms)

    def get_current_room(self) -> Room:
        """Return the user's current room."""
        return self.player_manager.get_current_room(self.user_player)

    def get_other_players_in_current_room(self) -> list[Player]:
        """Return all non‑user players in the current room."""
        current_room = self.get_current_room()
        return self.player_manager.get_other_players_in_room(
            current_room, self.user_player
        )

    def is_game_active(self) -> bool:
        """Return ``True`` if the game is still active."""
        return self.game_state_manager.is_game_active()

    def cleanup(self) -> None:
        """Clean up game resources via the resource manager."""
        self.resource_manager.cleanup()
