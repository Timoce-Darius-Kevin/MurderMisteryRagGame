import os
from dotenv import load_dotenv

class ModelConfig:
    load_dotenv()
    DEFAULT_MODEL = os.getenv("MISTRAL_7B_HUGGINGFACEHUB")
    FALLBACK_MODEL = os.getenv("ZEPHYR_7B_HUGGINGFACEHUB")
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"