from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    # APP CONFIG
    app_env: str = "development"
    project_name: str = "RAG PDF Backend"
    api_v1_str: str = "/api/v1"
    debug: bool = True
    
    # CORS
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
    
    # DATABASE
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/ragpdf"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # GOOGLE GEMINI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 4096
    
    # VECTOR STORE (PGVECTOR)
    vector_collection: str = "documents"
    vector_top_k: int = 5
    vector_distance: str = "cosine"
    
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunk_separators: List[str] = ["\n\n", "\n", ".", " ", ""]
    
    # FILE UPLOAD
    upload_dir: str = "./data/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [
        ".pdf", ".docx", ".txt", ".md", ".csv"
    ]
    
    # REDIS (CACHE)
    redis_url: str = "redis://redis:6379/0"
    cache_ttl: int = 3600  # 1 hour
    
    # LOGGING
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()