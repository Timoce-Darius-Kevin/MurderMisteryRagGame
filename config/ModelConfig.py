import os

class ModelConfig:
    DEFAULT_MODEL = os.getenv("MISTRAL_7B_HUGGINGFACEHUB")
    FALLBACK_MODEL = os.getenv("ZEPHYR_7B_HUGGINGFACEHUB")
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"