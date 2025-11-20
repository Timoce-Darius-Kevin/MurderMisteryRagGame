from typing import Optional, Tuple

from entities.Question import Question
from entities.Conversation import Conversation
from entities.Location import Location
from entities.Player import Player
from entities.Room import Room
from Services.LLMService import LLMService
from Services.MemoryService import MemoryService
from Services.PromptService import PromptService
from Services.ResponseService import ResponseService
from Services.SuspicionCalculator import SuspicionCalculator
from Services.ErrorHandler import ErrorHandler
from repositories.ConversationRepository import ConversationRepository


class RagManager:
    """Orchestrates RAG services for conversation generation."""

    def __init__(self, error_handler: Optional[ErrorHandler] = None) -> None:
        """Create a new RAG manager instance.

        Args:
            error_handler: Optional shared :class:`ErrorHandler` used for
                logging errors that occur during response generation.
        """
        self.error_handler: ErrorHandler = error_handler or ErrorHandler()

        self.memory_service = MemoryService()
        self.llm_service = LLMService()

        # Initialize specialized services
        self.prompt_service = PromptService()
        self.response_service = ResponseService(self.llm_service)
        self.suspicion_calculator = SuspicionCalculator()
        self.conversation_repository = ConversationRepository(
            self.memory_service, error_handler=self.error_handler
        )

        # For backward compatibility
        self.vector_store = self.conversation_repository.vector_store
    
    def add_conversation(self, conversation: Conversation, turn: int) -> None:
        """Store a conversation in memory"""
        self.conversation_repository.add_conversation(conversation, turn)
        
    def get_conversation_context(self, current_question: Question, number_docs_to_retrieve: int = 3) -> str:
        """Retrieve relevant conversation history"""
        return self.conversation_repository.get_conversation_context(current_question, number_docs_to_retrieve)

    def generate_response(
        self,
        question: Question,
        location: Location,
        current_room: Room,
        nearby_players: list[Player],
    ) -> Tuple[str, int, int]:
        """Generate NPC response using RAG with proper context.

        On any error during LLM invocation or suspicion calculation, a
        fallback response is generated and the error is logged via the
        configured :class:`ErrorHandler`.
        """
        try:
            # Get conversation context
            context = self.get_conversation_context(question)

            # Select template and create prompt
            template_type = self.prompt_service.select_template_type(question)
            prompt = self.prompt_service.create_prompt(
                question,
                location,
                current_room,
                context,
                template_type,
                nearby_players,
            )

            # Generate response
            if not self.response_service.llm:
                return self._generate_fallback_response(question)

            response_text = self.response_service.generate_response(prompt)

            # Calculate suspicion changes
            suspicion_change_speaker, suspicion_change_listener = (
                self.suspicion_calculator.calculate_suspicion_change(
                    question.question,
                    response_text,
                    question.listener.murderer,
                    question.listener.lying_ability,
                    question.listener.mood,
                )
            )

            # Mark items as known for inventory queries (innocent players only)
            if "inventory" in template_type and not question.listener.murderer:
                for item in question.listener.inventory:
                    if not item.murder_weapon:
                        item.known = True

            return response_text, suspicion_change_speaker, suspicion_change_listener

        except Exception as exception:  # pragma: no cover - defensive fallback
            self.error_handler.log_error(exception, context="RagManager.generate_response")
            return self._generate_fallback_response(question)
    
    def _generate_fallback_response(self, question: Question) -> Tuple[str, int, int]:
        """Generate fallback response when LLM is unavailable or fails."""
        response = self.response_service.generate_fallback_response(question)
        suspicion_change_speaker, suspicion_change_listener = (
            self.suspicion_calculator.calculate_fallback_suspicion(
                question.question,
                response,
                question.listener.murderer,
            )
        )
        return response, suspicion_change_speaker, suspicion_change_listener

    def clear_database(self) -> None:
        """Clear the entire conversation database"""
        self.conversation_repository.clear_database()
