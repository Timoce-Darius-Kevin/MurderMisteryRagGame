from langchain_huggingface import HuggingFaceEmbeddings
from config.ModelConfig import ModelConfig
from langchain_chroma import Chroma
class MemoryService:
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=ModelConfig.EMBEDDING_MODEL
        )

        self.vector_store = Chroma(
            collection_name="conversation_memory",
            embedding_function=self.embeddings,
            persist_directory="./database/conversation.db"
        )