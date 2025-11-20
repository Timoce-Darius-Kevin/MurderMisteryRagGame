from langchain_core.documents import Document
from entities.Conversation import Conversation
from entities.Question import Question
from Services.MemoryService import MemoryService


class ConversationRepository:
    """Handles conversation storage and retrieval using vector database"""
    
    def __init__(self, memory_service: MemoryService):
        self.vector_store = memory_service.vector_store
    
    def add_conversation(self, conversation: Conversation, turn: int) -> None:
        """Store a conversation in memory"""
        doc = Document(
            page_content=f"Question: {conversation.question.question}\nResponse: {conversation.response}",
            metadata={
                "player_ids": f"{conversation.question.speaker.id}-{conversation.question.listener.id}",
                "players": f"{conversation.question.speaker.name}-{conversation.question.listener.name}",
                "turn": turn
            }
        )
        self.vector_store.add_documents([doc])
    
    def get_conversation_context(self, current_question: Question, number_docs_to_retrieve: int = 3) -> str:
        """Retrieve relevant conversation history"""
        if self.vector_store._collection.count() == 0:
            return "No previous conversations."
        
        # Search for conversations between these two players
        player_filter = f"{current_question.speaker.id}-{current_question.listener.id}"
        results = self.vector_store.similarity_search(
            f"Conversation between {current_question.speaker.name} and {current_question.listener.name}: {current_question.question}",
            k=number_docs_to_retrieve,
            filter={"player_ids": player_filter}
        )
        
        if not results:
            return "No previous conversations with this person."
        
        context = "Previous conversations with this person:\n"
        for i, doc in enumerate(results):
            context += f"{i+1}. {doc.page_content}\n"
        
        return context
    
    def clear_database(self) -> None:
        """Clear the entire conversation database"""
        try:
            self.vector_store.delete_collection()
            print("Conversation database cleared.")
        except Exception as e:
            print(f"Error clearing database: {e}")
            try:
                all_docs = self.vector_store.get()
                if 'ids' in all_docs and all_docs['ids']:
                    self.vector_store.delete(ids=all_docs['ids'])
            except Exception as e2:
                print(f"Error with fallback cleanup: {e2}")
