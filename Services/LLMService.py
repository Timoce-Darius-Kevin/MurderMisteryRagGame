from config.ModelConfig import ModelConfig
from langchain_huggingface import HuggingFaceEmbeddings

class LLMService:
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=ModelConfig.EMBEDDING_MODEL
        )