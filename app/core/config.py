"""
Application settings, loaded from environment variables (.env).
"""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central place for all configurable values."""

    # General
    PROJECT_NAME: str = "Student Database Backend"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./students.db")

    # Gemini / LangGraph chatbot
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # ChromaDB (vector store)
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "students")
    GEMINI_EMBEDDING_MODEL: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "models/text-embedding-004"
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we only build the object once."""
    return Settings()


settings = get_settings()
