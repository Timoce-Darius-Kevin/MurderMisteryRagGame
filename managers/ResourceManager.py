from typing import Optional
from Services.LLMService import LLMService
from Services.MemoryService import MemoryService
from repositories.ConversationRepository import ConversationRepository


class ResourceManager:
    """Manages lifecycle of system resources like LLM models and vector stores"""
    
    def __init__(self):
        self.llm_service: Optional[LLMService] = None
        self.memory_service: Optional[MemoryService] = None
        self.conversation_repository: Optional[ConversationRepository] = None
        self._initialized = False
    
    def initialize(self, llm_service: LLMService, memory_service: MemoryService, 
                  conversation_repository: ConversationRepository):
        """Initialize resources"""
        self.llm_service = llm_service
        self.memory_service = memory_service
        self.conversation_repository = conversation_repository
        self._initialized = True
    
    def cleanup(self):
        """Clean up all resources"""
        if not self._initialized:
            return
        
        try:
            if self.conversation_repository:
                self.conversation_repository.clear_database()
            
            if self.llm_service and hasattr(self.llm_service, 'model'):
                self.llm_service.model = None
            
            print("Resources cleaned up successfully.")
        except Exception as e:
            print(f"Error during resource cleanup: {e}")
        finally:
            self._initialized = False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
        return False
