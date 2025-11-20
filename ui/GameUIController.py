"""Controller layer between the Tkinter UI and game logic.

This module provides `GameUIController`, which wraps `GameActionHandler`,
`ThreadingService`, and `ErrorHandler` so the UI layer can remain focused
purely on widgets and presentation concerns.
"""

from __future__ import annotations
from typing import Callable, Optional, Dict, Any, Tuple

from entities.Player import Player
from entities.Room import Room
from managers.GameManager import GameManager
from Services.ErrorHandler import ErrorHandler
from Services.ThreadingService import ThreadingService
from ui.GameActionHandler import GameActionHandler
from queue import Queue 


LogCallback = Callable[[str, str], None]


class GameUIController:
    """Orchestrates game actions for the UI layer.

    The controller exposes high-level operations that the Tkinter UI can call
    without needing direct access to `GameManager` or other domain objects.
    Long‑running operations are executed asynchronously via `ThreadingService`.
    """

    def __init__(
        self,
        game_manager: GameManager,
        user_player: Player,
        error_handler: Optional[ErrorHandler] = None,
    ) -> None:
        """Create a new controller instance.

        Args:
            game_manager: The underlying game manager.
            user_player: The human‑controlled player.
            error_handler: Optional shared error handler instance.
        """
        self._game_manager = game_manager
        self._user_player = user_player
        self._error_handler = error_handler or ErrorHandler()
        self._action_handler = GameActionHandler(game_manager, user_player)
        self._threading_service = ThreadingService(error_handler=self._error_handler)

    def get_players_in_current_room(self) -> list[Player]:
        """Return all other players in the current room."""
        return self._action_handler.get_players_in_current_room()

    def get_all_rooms(self) -> list[Room]:
        """Return all rooms in the current location."""
        return self._action_handler.get_all_rooms()

    def get_current_room(self) -> Room:
        """Return the room where the user currently is."""
        return self._action_handler.get_current_room()

    def get_user_inventory(self) -> Dict[str, Any]:
        """Return the user's inventory data structure."""
        return self._action_handler.get_user_inventory()

    def get_player_details(self, player: Player) -> Dict[str, Any]:
        """Return detail information about a player.

        The returned dictionary contains the player entity and their known
        items, suitable for rendering in the UI.
        """
        return self._action_handler.get_player_details(player)

    def is_game_active(self) -> bool:
        """Return ``True`` if the game is still active."""
        return self._action_handler.is_game_active()

    def move_to_room(self, room: Room) -> None:
        """Move the user player to the given room."""
        self._action_handler.move_to_room(room)

    def accuse_player(self, accused: Player) -> bool:
        """Accuse a player of being the murderer.

        Returns ``True`` if the accusation is correct, ``False`` otherwise.
        """
        return self._action_handler.accuse_player(accused)

    def cleanup(self) -> None:
        """Clean up underlying game resources."""
        self._action_handler.cleanup()

    def start_conversation_async(
        self, player: Player, question_text: str
    ) -> "Queue[Tuple[str, Any]]":
        """Start a background conversation with a player.

        The result queue will contain exactly one tuple of the form
        ``("success", result_dict)`` or ``("error", error_message)`` where
        ``result_dict`` has keys ``response``, ``suspicion_change_speaker``,
        ``suspicion_change_listener``, ``player`` and ``question_text``.
        """

        def task() -> Dict[str, Any]:
            response, sus_speaker, sus_listener = self._action_handler.ask_question(
                player, question_text
            )
            return {
                "response": response,
                "suspicion_change_speaker": sus_speaker,
                "suspicion_change_listener": sus_listener,
                "player": player,
                "question_text": question_text,
            }

        queue: Queue[Tuple[str, Any]] = self._threading_service.execute_async(task)
        return queue

    def start_inventory_query_async(
        self, player: Player
    ) -> "Queue[Tuple[str, Any]]":
        """Start a background inventory query for the given player.

        The result queue will contain a tuple ``("success", result_dict)`` or
        ``("error", error_message)``. ``result_dict`` will be the dictionary
        returned by :meth:`GameActionHandler.ask_about_inventory` with an
        additional ``"player"`` key referencing the queried player.
        """
        from queue import Queue

        def task() -> Dict[str, Any]:
            result = self._action_handler.ask_about_inventory(player)
            # Attach the player object so the UI can log their name.
            result["player"] = player
            return result

        queue: Queue[Tuple[str, Any]] = self._threading_service.execute_async(task)
        return queue
