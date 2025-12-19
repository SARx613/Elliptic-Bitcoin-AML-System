"""
Configuration utilities for the FastAPI application.
"""

from functools import lru_cache
import os
from pydantic import BaseModel


class Settings(BaseModel):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        neo4j_uri: Neo4j database connection URI.
        neo4j_user: Neo4j database username.
        neo4j_password: Neo4j database password.
    """

    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached application settings.
    
    Uses LRU cache to ensure settings are only created once.
    
    Returns:
        Settings: Application settings instance.
    """
    return Settings()

