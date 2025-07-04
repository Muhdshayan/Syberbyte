from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Model Paths
    MISTRAL_MODEL_PATH: str = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    CODELLAMA_MODEL_PATH: str = "models/codellama-7b.Q4_K_M.gguf"
    DISTILBERT_MODEL_NAME: str = "dslim/bert-base-NER"
    
    # Model Settings
    MODEL_N_CTX: int = 4096
    MODEL_N_THREADS: int = 8
    MODEL_TEMPERATURE: float = 0.7
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "data/vectors/chroma"
    FAISS_INDEX_PATH: str = "data/vectors/faiss.index"
    EMBEDDING_DIM: int = 768
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Bias Detection
    FAIRNESS_THRESHOLD: float = 0.8
    DEMOGRAPHIC_CATEGORIES: list = ["gender", "ethnicity", "age"]
    
    class Config:
        env_file = ".env"

settings = Settings()