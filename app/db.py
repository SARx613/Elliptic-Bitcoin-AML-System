"""
Neo4j driver management.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from app.config import get_settings


_driver: AsyncDriver | None = None  # pylint: disable=invalid-name


def get_driver() -> AsyncDriver:
    """
    Lazily create and cache the Neo4j async driver.
    
    Uses singleton pattern to ensure only one driver instance exists.
    
    Returns:
        AsyncDriver: Cached Neo4j async driver instance.
    """
    global _driver  # pylint: disable=global-statement
    if _driver is None:
        settings = get_settings()
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


@asynccontextmanager
async def neo4j_session() -> AsyncIterator[AsyncSession]:
    """
    Provide an async Neo4j session as a context manager.
    
    Yields:
        AsyncSession: An async Neo4j session that is automatically closed after use.
        
    Example:
        ```python
        async with neo4j_session() as session:
            result = await session.run("MATCH (n) RETURN n")
        ```
    """
    driver = get_driver()
    async with driver.session() as session:
        yield session

